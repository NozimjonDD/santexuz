#!/usr/bin/env python3
"""Ubuntu-only operations. Read README.md; never execute on the coding machine.

No SSH, shell evaluation, automatic git pulls, database downgrades or pruning.
Run from a trusted, committed server checkout with sudo and a root-owned config.
"""
import argparse
import configparser
from datetime import datetime, timezone
import fcntl
import grp
import json
import os
from pathlib import Path
import pwd
import re
import secrets
import subprocess
import sys
import tarfile
import tempfile
import time


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent.parent
SYSTEM_PATH = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"


def run(args, **kwargs):
    """Never echo arguments/env: they may contain application or database secrets."""
    return subprocess.run([str(arg) for arg in args], check=True, **kwargs)


def output(args, **kwargs):
    return run(args, stdout=subprocess.PIPE, text=True, **kwargs).stdout.strip()


def atomic_write(path, text, mode=0o644, gid=0):
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            os.fchmod(stream.fileno(), mode)
            os.fchown(stream.fileno(), 0, gid)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read_env(path):
    result = {}
    info = path.stat()
    if info.st_uid != 0 or info.st_mode & 0o027:
        raise ValueError(f"Secret file must be root-owned, mode 0600 or 0640: {path}")
    for line in path.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if not separator or not re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
            raise ValueError(f"Invalid KEY=value in {path}; shell syntax is not supported.")
        if value != value.strip() or any(c in value for c in "\r\n\\\"'"):
            raise ValueError(f"Use unquoted, literal values without backslashes in {path}.")
        if key in result:
            raise ValueError(f"Duplicate key {key} in {path}")
        result[key] = value
    return result


def seal_release(release, group_id):
    """Readable code/venv for service users, writable only by root; never follow links."""
    for directory, subdirectories, files in os.walk(release, followlinks=False):
        for path in [Path(directory), *(Path(directory) / name for name in subdirectories + files)]:
            os.chown(path, 0, group_id, follow_symlinks=False)
            if not path.is_symlink():
                path.chmod(0o755 if path.is_dir() or path.stat().st_mode & 0o111 else 0o644)


class Deployment:
    def __init__(self, config_path):
        self.config_path = config_path.resolve(strict=True)
        info = self.config_path.stat()
        if info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError("Deployment config must be root-owned and not group/world writable.")
        config = configparser.ConfigParser(interpolation=None)
        config.read(self.config_path)
        config = config["deployment"]
        self.name = config["app_name"]
        self.user = config["app_user"]
        for name in (self.name, self.user):
            if not re.fullmatch(r"[a-z][a-z0-9_]{1,23}", name):
                raise ValueError("app_name/app_user: 2–24 lowercase letters, digits or underscore.")
        root = config["app_root"]
        if not re.fullmatch(r"/(srv|opt)/[a-z][a-z0-9_-]{1,39}", root):
            raise ValueError("app_root must be a dedicated direct child of /srv or /opt.")
        self.root = Path(root)
        if self.root.resolve() != self.root:
            raise ValueError("app_root and its parents must not be symlinks.")
        self.domain = config["domain"].lower()
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", self.domain) or "." not in self.domain:
            raise ValueError("Use one DNS hostname for domain (no scheme, port or wildcard).")
        if any(label.startswith("-") or label.endswith("-") or not label for label in self.domain.split(".")):
            raise ValueError("Invalid domain labels.")
        self.email = config["certificate_email"]
        if not re.fullmatch(r"[A-Za-z0-9_.+%-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", self.email):
            raise ValueError("Set certificate_email.")
        if self.domain.endswith(".example.com") or self.email.endswith("@example.com"):
            raise ValueError("Replace example domain and certificate_email before bootstrap.")
        self.etc = Path("/etc") / self.name
        self.migration_user = f"{self.name}_migrate"
        self.shared = self.root / "shared"
        self.releases = self.root / "releases"
        self.backups = Path("/var/backups") / self.name
        self.env_path = self.etc / "production.env"
        self.migration_path = self.etc / "migration.env"
        self.values = {
            "APP_NAME": self.name, "APP_USER": self.user, "APP_ROOT": str(self.root),
            "DOMAIN": self.domain, "CONFIG_PATH": str(self.config_path),
        }
        # Template paths are systemd/nginx tokens; spaces and control characters are forbidden.
        if not re.fullmatch(r"/[A-Za-z0-9_./-]+", str(self.config_path)):
            raise ValueError("Use a config path without spaces or special characters.")

    def render(self, file, extra=None):
        text = (HERE / file).read_text()
        for key, value in {**self.values, **(extra or {})}.items():
            text = text.replace(f"@@{key}@@", value)
        if re.search(r"@@[A-Z_]+@@", text):
            raise ValueError(f"Unresolved placeholder in {file}")
        return text

    def account(self, migration=False):
        account = pwd.getpwnam(self.migration_user if migration else self.user)
        if account.pw_uid == 0 or account.pw_dir != str(self.root) or grp.getgrgid(account.pw_gid).gr_name != self.user:
            raise ValueError("Use a dedicated non-root user/group with app_root as its home.")
        if migration and account.pw_uid == pwd.getpwnam(self.user).pw_uid:
            raise ValueError("Migration and application OS users must have different UIDs.")
        if set(os.getgrouplist(account.pw_name, account.pw_gid)) != {account.pw_gid}:
            raise ValueError("Dedicated OS accounts must not belong to additional groups.")
        return account

    def environment(self, migration=False):
        env = read_env(self.env_path)
        expected = {
            "DJANGO_SETTINGS_MODULE": "project_backend.settings.production", "DB_ENGINE": "postgresql",
            "DB_NAME": self.name, "DB_USER": f"{self.name}_app", "DB_HOST": "127.0.0.1", "DB_PORT": "5432",
            "MEDIA_ROOT": str(self.shared / "private"), "STATIC_ROOT": str(self.shared / "static"),
            "APP_LOG_PATH": str(self.shared / "logs/app.log"), "ALLOWED_HOSTS": self.domain,
            "MINI_APP_URL": f"https://{self.domain}/",
        }
        if any(env.get(key) != value for key, value in expected.items()):
            raise ValueError("production.env paths/database/hostname must match deploy.ini; remote DBs need a separate plan.")
        if any(value.startswith("CHANGE_ME") for value in env.values()):
            raise ValueError("Fill Telegram and routing values in production.env before release.")
        if migration:
            if self.migration_path.stat().st_mode & 0o077:
                raise ValueError("migration.env must have mode 0600 (root access only).")
            migration_env = read_env(self.migration_path)
            if set(migration_env) != {"DB_USER", "DB_PASSWORD"} or migration_env["DB_USER"] != f"{self.name}_migrator":
                raise ValueError("migration.env must contain only the dedicated migrator credentials.")
            env.update(migration_env)
        return {
            "PATH": SYSTEM_PATH, "LANG": "C.UTF-8", "HOME": str(self.shared),
            **env, "PYTHONUNBUFFERED": "1", "PYTHONDONTWRITEBYTECODE": "1",
        }

    def app_run(self, args, release, migration=False, **kwargs):
        # A separate UID also prevents the running app from reading migrator env via /proc.
        account = self.account(migration)
        return run(args, cwd=release, env=self.environment(migration), user=account.pw_uid,
                   group=account.pw_gid, extra_groups=[], **kwargs)

    def manage(self, release, *args, migration=False):
        return self.app_run([release / ".venv/bin/python", "manage.py", *args], release, migration)

    def sql(self, query, database="postgres"):
        return output(["runuser", "-u", "postgres", "--", "psql", "-X", "-q", "-A", "-t",
                       "-v", "ON_ERROR_STOP=1", "--host", "/var/run/postgresql", "--port", "5432",
                       "--username", "postgres", "--no-password", "--dbname", database],
                      input=query, stderr=subprocess.PIPE, env={"PATH": SYSTEM_PATH, "LANG": "C.UTF-8"})

    def grants(self):
        name = self.name
        owns_objects = self.sql(f'''
            SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
                WHERE n.nspname='public' AND pg_get_userbyid(c.relowner)='{name}_app'
            UNION ALL
            SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
                WHERE n.nspname='public' AND pg_get_userbyid(p.proowner)='{name}_app'
            UNION ALL
            SELECT 1 FROM pg_namespace WHERE nspname='public' AND pg_get_userbyid(nspowner)='{name}_app';
        ''', name)
        if owns_objects:
            raise ValueError("Runtime role owns database objects; transfer them to the migrator through a reviewed DBA migration first.")
        self.sql(f'''
            BEGIN;
            REVOKE ALL ON DATABASE "{name}" FROM PUBLIC;
            REVOKE ALL ON DATABASE "{name}" FROM "{name}_app";
            GRANT CONNECT ON DATABASE "{name}" TO "{name}_app";
            REVOKE CREATE ON SCHEMA public FROM PUBLIC;
            REVOKE ALL ON SCHEMA public FROM "{name}_app";
            GRANT USAGE ON SCHEMA public TO "{name}_app";
            REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC, "{name}_app";
            REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM PUBLIC, "{name}_app";
            GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "{name}_app";
            GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO "{name}_app";
            DO $$ BEGIN
                IF to_regclass('public.django_migrations') IS NOT NULL THEN
                    REVOKE INSERT, UPDATE, DELETE ON public.django_migrations FROM "{name}_app";
                END IF;
            END $$;
            ALTER DEFAULT PRIVILEGES FOR ROLE "{name}_migrator" IN SCHEMA public
                REVOKE ALL ON TABLES FROM "{name}_app";
            ALTER DEFAULT PRIVILEGES FOR ROLE "{name}_migrator" IN SCHEMA public
                REVOKE ALL ON SEQUENCES FROM "{name}_app";
            ALTER DEFAULT PRIVILEGES FOR ROLE "{name}_migrator" IN SCHEMA public
                GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "{name}_app";
            ALTER DEFAULT PRIVILEGES FOR ROLE "{name}_migrator" IN SCHEMA public
                GRANT USAGE, SELECT ON SEQUENCES TO "{name}_app";
            COMMIT;
        ''', name)

    def bootstrap(self):
        run(["apt-get", "update"])
        run(["apt-get", "install", "-y", "python3-venv", "python3-dev", "build-essential", "libpq-dev",
             "nginx", "postgresql", "postgresql-contrib", "certbot", "fonts-dejavu-core", "curl", "git"])
        run(["systemctl", "enable", "--now", "postgresql", "nginx"])
        try:
            pwd.getpwnam(self.user)
        except KeyError:
            run(["useradd", "--system", "--user-group", "--home-dir", self.root,
                 "--no-create-home", "--shell", "/usr/sbin/nologin", self.user])
        account = self.account()
        try:
            pwd.getpwnam(self.migration_user)
        except KeyError:
            run(["useradd", "--system", "--gid", self.user, "--home-dir", self.root,
                 "--no-create-home", "--shell", "/usr/sbin/nologin", self.migration_user])
        self.account(migration=True)
        for path, mode in ((self.root, 0o755), (self.releases, 0o755), (self.shared, 0o755),
                           (self.etc, 0o750), (self.backups, 0o700)):
            if path.is_symlink():
                raise ValueError(f"Managed directory must not be a symlink: {path}")
            path.mkdir(parents=True, exist_ok=True)
            os.chown(path, 0, account.pw_gid)
            path.chmod(mode)
        for directory, mode in (("private", 0o700), ("logs", 0o750), ("static", 0o755)):
            path = self.shared / directory
            if path.is_symlink():
                raise ValueError(f"Managed directory must not be a symlink: {path}")
            path.mkdir(exist_ok=True)
            os.chown(path, account.pw_uid, account.pw_gid)
            path.chmod(mode)
        Path("/var/www/letsencrypt").mkdir(parents=True, exist_ok=True)
        Path("/var/www/letsencrypt").chmod(0o755)
        if not self.env_path.exists():
            atomic_write(self.env_path, self.render("production.env.example", {
                "SECRET_KEY": secrets.token_urlsafe(64), "DB_PASSWORD": secrets.token_urlsafe(36),
                "WEBHOOK_SECRET": secrets.token_urlsafe(40),
            }), 0o640, account.pw_gid)
        if not self.migration_path.exists():
            atomic_write(self.migration_path,
                         f"DB_USER={self.name}_migrator\nDB_PASSWORD={secrets.token_urlsafe(36)}\n", 0o600)
        runtime = read_env(self.env_path)
        migration = read_env(self.migration_path)
        for role, password in ((f"{self.name}_app", runtime["DB_PASSWORD"]),
                               (f"{self.name}_migrator", migration["DB_PASSWORD"])):
            if not self.sql(f"SELECT 1 FROM pg_roles WHERE rolname='{role}';"):
                literal = password.replace("'", "''")
                self.sql(f'''CREATE ROLE "{role}" LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
                             NOREPLICATION NOBYPASSRLS PASSWORD '{literal}';''')
            role_info = self.sql(f"SELECT rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls FROM pg_roles WHERE rolname='{role}';")
            if role_info != "f":
                raise ValueError("Existing database role has elevated privileges; use a new app_name.")
            if self.sql(f"SELECT 1 FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname='{role}');"):
                raise ValueError("Dedicated database roles must not inherit membership of other roles.")
        if not self.sql(f"SELECT 1 FROM pg_database WHERE datname='{self.name}';"):
            self.sql(f'''CREATE DATABASE "{self.name}" OWNER "{self.name}_migrator" ENCODING 'UTF8' TEMPLATE template0;''')
        owner = self.sql(f"SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='{self.name}';")
        if owner != f"{self.name}_migrator":
            raise ValueError("Existing database has another owner; no ownership takeover was performed.")
        self.grants()
        atomic_write(self.shared / "maintenance.html", self.render("templates/maintenance.html"))
        self.install_units()
        site = Path(f"/etc/nginx/sites-available/{self.name}")
        if not site.exists():
            self.install_nginx("templates/nginx-http.conf")
        print(f"Bootstrap complete. Edit {self.env_path}: Telegram credentials and routing provider. Secrets were not printed.")

    def install_units(self):
        for filename, suffix in (("app.socket", ".socket"), ("app.service", ".service"),
                                 ("notifications.service", "-notifications.service"), ("notifications.timer", "-notifications.timer"),
                                 ("deadlines.service", "-deadlines.service"), ("deadlines.timer", "-deadlines.timer"),
                                 ("backup.service", "-backup.service"), ("backup.timer", "-backup.timer")):
            atomic_write(Path("/etc/systemd/system") / f"{self.name}{suffix}", self.render(f"templates/{filename}"))
        run(["systemctl", "daemon-reload"])

    def install_nginx(self, template):
        site = Path(f"/etc/nginx/sites-available/{self.name}")
        enabled = Path(f"/etc/nginx/sites-enabled/{self.name}")
        if enabled.is_symlink() and enabled.resolve() != site:
            raise ValueError("Nginx site link points to another project.")
        if enabled.exists() and not enabled.is_symlink():
            raise ValueError("Refusing to overwrite a non-symlink enabled Nginx site.")
        old = site.read_text() if site.exists() else None
        atomic_write(Path("/etc/nginx/conf.d/santex-private-log.conf"), self.render("templates/nginx-log.conf"))
        atomic_write(site, self.render(template))
        created_link = not enabled.is_symlink()
        if created_link:
            enabled.symlink_to(site)
        try:
            run(["nginx", "-t"])
            run(["systemctl", "reload", "nginx"])
        except BaseException:
            if old is not None:
                atomic_write(site, old)
            else:
                site.unlink(missing_ok=True)
            if created_link:
                enabled.unlink(missing_ok=True)
            raise

    def https(self):
        self.current()
        run(["certbot", "certonly", "--webroot", "--webroot-path", "/var/www/letsencrypt",
             "--non-interactive", "--agree-tos", "--email", self.email,
             "--cert-name", self.domain, "--domain", self.domain])
        hook = Path("/etc/letsencrypt/renewal-hooks/deploy")
        hook.mkdir(parents=True, exist_ok=True)
        atomic_write(hook / f"{self.name}-nginx", "#!/bin/sh\nset -eu\n/usr/sbin/nginx -t\n/bin/systemctl reload nginx\n", 0o755)
        self.install_nginx("templates/nginx-https.conf")
        run(["systemctl", "enable", "--now", "certbot.timer"])
        run(["curl", "--fail", "--silent", "--show-error", "--max-time", "15", f"https://{self.domain}/health/ready/"])

    def current(self):
        target = (self.root / "current").resolve(strict=True)
        if target.parent != self.releases or not (target / "manage.py").is_file():
            raise ValueError("current must point to a complete release inside app_root/releases.")
        return target

    def link(self, name, release):
        link = self.root / name
        if link.exists() and not link.is_symlink():
            raise ValueError(f"Refusing to replace non-symlink {link}")
        temporary = self.root / f".{name}-{secrets.token_hex(6)}"
        temporary.symlink_to(release)
        os.replace(temporary, link)

    def pause(self):
        atomic_write(self.shared / "maintenance.flag", "Deployment in progress\n")
        run(["systemctl", "stop", f"{self.name}-notifications.timer", f"{self.name}-deadlines.timer",
             f"{self.name}-backup.timer"])
        # Stop background writers before schema changes. Outbox delivery is at least once.
        run(["systemctl", "stop", f"{self.name}-notifications.service", f"{self.name}-deadlines.service"])
        run(["systemctl", "stop", f"{self.name}.socket", f"{self.name}.service"])

    def resume(self):
        run(["systemctl", "enable", f"{self.name}.socket", f"{self.name}.service",
             f"{self.name}-notifications.timer", f"{self.name}-deadlines.timer", f"{self.name}-backup.timer"])
        run(["systemctl", "start", f"{self.name}.socket", f"{self.name}.service"])
        self.probe()
        try:
            (self.shared / "maintenance.flag").unlink(missing_ok=True)
            run(["systemctl", "start", f"{self.name}-notifications.timer", f"{self.name}-deadlines.timer",
                 f"{self.name}-backup.timer"])
        except BaseException:
            atomic_write(self.shared / "maintenance.flag", "Background schedule activation failed\n")
            raise
        atomic_write(self.current() / "HEALTHY", datetime.now(timezone.utc).isoformat() + "\n")

    def probe(self):
        for _ in range(15):
            try:
                result = output(["curl", "--fail", "--silent", "--show-error", "--max-time", "3",
                                 "--unix-socket", f"/run/{self.name}-gunicorn.sock",
                                 "-H", f"Host: {self.domain}", "-H", "X-Forwarded-Proto: https",
                                 "http://localhost/health/ready/"], stderr=subprocess.DEVNULL)
                if json.loads(result).get("status") == "ok":
                    print("Readiness: ok")
                    return
            except (subprocess.CalledProcessError, ValueError):
                pass
            time.sleep(2)
        raise RuntimeError("Readiness failed. Maintenance stays enabled; inspect systemd journal.")

    def backup(self):
        destination = self.backups / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S-%fZ")
        destination.mkdir(mode=0o700, parents=True)
        try:
            with (destination / "database.dump").open("wb") as stream:
                run(["runuser", "-u", "postgres", "--", "pg_dump", "--format=custom", "--no-owner",
                     "--no-acl", "--host", "/var/run/postgresql", "--port", "5432", "--username", "postgres",
                     "--no-password", "--dbname", self.name], stdout=stream,
                    env={"PATH": SYSTEM_PATH, "LANG": "C.UTF-8"})
            run(["tar", "--create", "--gzip", "--file", destination / "private.tar.gz",
                 "--directory", self.shared, "private"])
            current = self.current() if (self.root / "current").exists() else None
            atomic_write(destination / "metadata.json", json.dumps({
                "database": self.name, "release": current.name if current else None,
                "commit": json.loads((current / "RELEASE.json").read_text()).get("commit") if current else None,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }, indent=2) + "\n", 0o600)
            # A backup is usable only after this marker; incomplete directories are retained.
            atomic_write(destination / "COMPLETE", "ok\n", 0o600)
        except BaseException:
            print(f"Incomplete backup retained at {destination}; do not restore it.", file=sys.stderr)
            raise
        print(f"Backup: {destination} (copy to encrypted off-server storage).")
        return destination

    def release(self, ref):
        self.environment()  # Refuse placeholders before building or interrupting service.
        self.account()
        repo = next((path for path in (SOURCE, *SOURCE.parents) if (path / ".git").exists()), None)
        if repo is None:
            raise ValueError("Run release from a Git checkout, not from an exported release directory.")
        git = ["git", "-c", f"safe.directory={repo}", "-C", SOURCE]
        if output([*git, "status", "--porcelain", "--untracked-files=normal", "--", "."]):
            raise ValueError("Commit the backend changes first; release only exports committed files.")
        commit = output([*git, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}"])
        prefix = output([*git, "rev-parse", "--show-prefix"])
        tree = f"{commit}:{prefix.rstrip('/')}" if prefix else commit
        release = self.releases / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S-%fZ-") + commit[:12])
        release.mkdir(mode=0o755)
        with tempfile.TemporaryFile() as archive:
            run([*git, "archive", "--format=tar", tree], stdout=archive)
            archive.seek(0)
            with tarfile.open(fileobj=archive) as bundle:
                for item in bundle.getmembers():
                    if Path(item.name).parts[0] in {".env", ".venv", "venv", ".git"}:
                        raise ValueError("Runtime environments/secrets must not be tracked in Git.")
                bundle.extractall(release, filter="data")  # Ubuntu 24.04 / Python 3.12+
        if not (release / "manage.py").is_file():
            raise ValueError("Git ref does not contain the backend at this repository path.")
        account = self.account()
        # data_filter may create directories with mode 0700 under our secure umask.
        # Normalize code before dropping privileges to build the virtual environment.
        seal_release(release, account.pw_gid)
        os.chown(release, account.pw_uid, account.pw_gid)
        build_env = {"PATH": SYSTEM_PATH, "LANG": "C.UTF-8", "HOME": str(self.shared), "PIP_NO_CACHE_DIR": "1"}
        run(["python3", "-m", "venv", release / ".venv"], user=account.pw_uid,
            group=account.pw_gid, extra_groups=[], env=build_env, cwd=release)
        run([release / ".venv/bin/python", "-m", "pip", "install", "--disable-pip-version-check",
             "-r", release / "requirements/production.txt"], user=account.pw_uid,
            group=account.pw_gid, extra_groups=[], env=build_env, cwd=release)
        resolved = output([release / ".venv/bin/python", "-m", "pip", "freeze"],
                          user=account.pw_uid, group=account.pw_gid, extra_groups=[], env=build_env, cwd=release)
        atomic_write(release / "requirements.resolved.txt", resolved + "\n")
        atomic_write(release / "RELEASE.json", json.dumps({"commit": commit, "release": release.name}) + "\n")
        # Dependencies are installed without root. Seal the entire release before services use it.
        seal_release(release, account.pw_gid)
        self.manage(release, "check", "--deploy", "--fail-level", "WARNING")
        self.manage(release, "makemigrations", "--check", "--dry-run")
        previous = self.current() if (self.root / "current").exists() else None
        if previous and not (previous / "HEALTHY").exists():
            candidate = self.root / "previous"
            previous = candidate.resolve() if candidate.exists() else None
            if previous and (previous.parent != self.releases or not (previous / "HEALTHY").exists()):
                raise ValueError("Previous release is not a known healthy release.")
        self.install_units()
        self.pause()
        # All failures from this point intentionally keep the site in maintenance.
        self.backup()
        self.manage(release, "migrate", "--noinput", migration=True)
        self.manage(release, "createcachetable", migration=True)
        self.grants()
        self.manage(release, "seed_pilot")
        self.manage(release, "collectstatic", "--noinput")
        self.link("current", release)
        if previous:
            self.link("previous", previous)
        self.resume()
        print(f"Release ready: {release.name}. Next: HTTPS and explicit Telegram registration.")

    def rollback(self):
        self.environment()
        target = (self.root / "previous").resolve(strict=True)
        if target.parent != self.releases or not (target / "manage.py").is_file() or not (target / "HEALTHY").exists():
            raise ValueError("No complete previous release.")
        old = self.current()
        self.pause()
        self.backup()
        # Deliberately never undo migrations or restore a database automatically.
        self.manage(target, "check", "--deploy", "--fail-level", "WARNING")
        self.manage(target, "collectstatic", "--noinput")
        self.link("current", target)
        self.link("previous", old)
        self.resume()
        print("Previous code activated. Database schema/data were not rolled back.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("/etc/santex/deploy.ini"))
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("bootstrap", "https", "backup", "rollback", "status"):
        commands.add_parser(name)
    release = commands.add_parser("release")
    release.add_argument("--ref", default="HEAD", help="Committed Git ref; default is this checkout's HEAD.")
    manage = commands.add_parser("manage")
    manage.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if sys.platform != "linux" or sys.version_info < (3, 12) or os.geteuid() != 0:
        parser.error("Run only on Ubuntu 24.04+ / Python 3.12+, as root (sudo).")
    os.umask(0o077)
    deployment = Deployment(args.config)
    # Serialize backup/release/rollback and prevent overlapping administrator runs.
    with open(f"/run/lock/{deployment.name}-deploy.lock", "w") as lock:
        try:
            # Nightly backup can wait for an in-progress release; interactive operations fail fast.
            fcntl.flock(lock, fcntl.LOCK_EX | (0 if args.command == "backup" else fcntl.LOCK_NB))
        except BlockingIOError:
            raise RuntimeError("Another deployment/backup is running; retry after it completes.") from None
        if args.command == "release":
            deployment.release(args.ref)
        elif args.command == "manage":
            if not args.arguments or args.arguments[0] in {"migrate", "createcachetable", "dbshell", "runserver"}:
                parser.error("manage requires an application command; use release for schema changes.")
            deployment.manage(deployment.current(), *args.arguments)
        elif args.command == "status":
            deployment.probe()
            run(["systemctl", "--no-pager", "status", f"{deployment.name}.service",
                 f"{deployment.name}.socket", f"{deployment.name}-notifications.timer",
                 f"{deployment.name}-deadlines.timer", f"{deployment.name}-backup.timer"])
        else:
            getattr(deployment, args.command)()


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, configparser.Error, RuntimeError, subprocess.CalledProcessError) as error:
        # CalledProcessError may carry command arguments. Never print those.
        detail = f"External command exited with code {error.returncode}." if isinstance(error, subprocess.CalledProcessError) else str(error)
        print(f"Stopped: {detail}", file=sys.stderr)
        print("If maintenance.flag exists, keep it until the cause is resolved. See deploy/ubuntu/README.md.", file=sys.stderr)
        sys.exit(1)

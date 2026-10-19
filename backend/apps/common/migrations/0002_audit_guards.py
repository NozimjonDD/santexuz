"""Database safeguards also reject raw SQL and queryset mutations."""
from django.db import migrations


def install_guards(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor == "postgresql":
        schema_editor.execute("""
            CREATE FUNCTION santex_audit_immutable() RETURNS trigger AS $$
            BEGIN RAISE EXCEPTION 'Audit events are append-only'; END;
            $$ LANGUAGE plpgsql;
        """)
        schema_editor.execute("CREATE TRIGGER audit_immutable BEFORE UPDATE OR DELETE ON common_auditevent FOR EACH ROW EXECUTE FUNCTION santex_audit_immutable()")
    elif vendor == "sqlite":
        schema_editor.execute("CREATE TRIGGER audit_no_update BEFORE UPDATE ON common_auditevent BEGIN SELECT RAISE(ABORT, 'Audit events are append-only'); END")
        schema_editor.execute("CREATE TRIGGER audit_no_delete BEFORE DELETE ON common_auditevent BEGIN SELECT RAISE(ABORT, 'Audit events are append-only'); END")
    else:
        raise RuntimeError("Audit DB safeguards require PostgreSQL or SQLite.")


def remove_guards(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute("DROP TRIGGER IF EXISTS audit_immutable ON common_auditevent")
        schema_editor.execute("DROP FUNCTION IF EXISTS santex_audit_immutable()")
    elif schema_editor.connection.vendor == "sqlite":
        schema_editor.execute("DROP TRIGGER IF EXISTS audit_no_update")
        schema_editor.execute("DROP TRIGGER IF EXISTS audit_no_delete")


class Migration(migrations.Migration):
    dependencies = [("common", "0001_initial")]
    operations = [migrations.RunPython(install_guards, remove_guards)]

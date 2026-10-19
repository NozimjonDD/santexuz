"""Check the deployed public API from the other machine, without credentials.

Example: python scripts/check_public_api.py --base-url https://your-domain.example
Only status/format information is printed; response bodies are never logged.
"""
import argparse
import json
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


PATHS = (
    "/health/ready/",
    *(f"/api/v1/common/{resource}/" for resource in (
        "regions", "service-groups", "services", "materials", "plumbers", "stores", "service-center",
    )),
    "/api/v1/common/service-rates/?region=1",
)


def check(base_url, path):
    request = Request(base_url + path, headers={"Accept": "application/json"})
    try:
        try:
            response = urlopen(request, timeout=15)
        except HTTPError as error:
            response = error
        with response:
            status = response.code
            content_type = response.headers.get_content_type()
            body = response.read(1024 * 1024 + 1)
    except (URLError, OSError, ValueError, HTTPException):
        print(f"FAIL {path}: connection failed")
        return False
    if status != 200:
        print(f"FAIL {path}: HTTP {status}, {content_type}")
        return False
    nullable = path.endswith("/service-center/")
    try:
        data = json.loads(body) if body else None
    except (ValueError, UnicodeError):
        print(f"FAIL {path}: HTTP 200 returned non-JSON ({content_type}); check proxy routing")
        return False
    valid = len(body) <= 1024 * 1024 and (content_type == "application/json" or nullable and not body)
    if path == "/health/ready/":
        valid = valid and data == {"status": "ok"}
    elif nullable:
        valid = valid and (data is None or isinstance(data, dict) and "name" in data)
    else:
        valid = valid and (isinstance(data, list) or isinstance(data, dict) and isinstance(data.get("results"), list))
    print(f"{'OK' if valid else 'FAIL'} {path}: HTTP {status}, {content_type}" + ("" if valid else ", unexpected response shape"))
    return valid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="API origin, e.g. https://your-domain.example")
    options = parser.parse_args()
    try:
        origin = urlsplit(options.base_url)
    except ValueError:
        parser.error("--base-url is not a valid origin")
    if origin.scheme not in {"http", "https"} or not origin.hostname or origin.username or origin.password or origin.path not in {"", "/"} or origin.query or origin.fragment:
        parser.error("--base-url must be an HTTP(S) origin without credentials, a path or query")
    results = [check(options.base_url.rstrip("/"), path) for path in PATHS]
    if not all(results):
        print("Check the server logs, DB/migrations and Nginx API routing for failing paths.")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

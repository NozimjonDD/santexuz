"""Select local, optional image derivatives without requiring an asset build."""
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage


def _available(path: str) -> bool:
    if settings.DEBUG:
        # Development serves source static files, rather than collectstatic output.
        return bool(finders.find(path))
    try:
        # Check the files actually served in production. A source-only derivative
        # must not be selected before collectstatic copies it into the release.
        return Path(staticfiles_storage.path(path)).is_file()
    except (NotImplementedError, OSError, ValueError):
        # Non-filesystem storage keeps the original portable PNG URLs. Generating
        # derivatives never introduces per-request remote storage/API probes.
        return False


def miniapp_images() -> dict[str, str]:
    images = {}
    for key, stem in (("hero", "plumbing-hero"), ("atlas", "service-scenes")):
        optimized = f"miniapp/images/{stem}.webp"
        images[key] = optimized if _available(optimized) else f"miniapp/images/{stem}.png"
    return images

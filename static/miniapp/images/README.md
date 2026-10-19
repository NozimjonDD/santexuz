# Santex UI photography

2026-10-19: two new assets generated with the built-in `imagegen` tool and copied into this project's static directory. No CLI, API-key workflow, image converter or local build was run. The original generated outputs were retained.

- `static/miniapp/images/plumbing-hero.png`: illustrative editorial plumbing photograph for the customer home hero.
- `static/miniapp/images/service-scenes.png`: one square 2×2 photographic atlas. Heating: top-left; installation: top-right; pipes/drainage: bottom-left; repair: bottom-right. CSS crops the quadrants without stretching them.

These are AI-generated illustrations in a photographic style, not photographs of the actual partner team. They are decorative, carry no customer/employee identity, and are never substituted for an API partner's profile photo. Partner photos come from the API; missing/broken photos fall back to their initials. There are no fabricated ratings, badges or customer statistics in these assets.

The PNGs are the original outputs, about 1.9 MB each. The category atlas is shared across every matching card and requested as one cached asset; the hero image is requested only on the customer home screen. Images are decoded asynchronously. No remote image host, analytics endpoint, external font or image CDN is introduced. These source PNGs work without an encoding step. The images were inspected directly after generation; the live UI was not launched or visually verified on the write-only machine.

## Optional mobile image preparation — boshqa kompyuterda

Existing Pillow requirements are sufficient; no frontend bundler or additional dependency is needed. In the active project virtual environment on the asset/deployment machine:

```bash
python scripts/prepare_miniapp_images.py && python scripts/prepare_miniapp_images.py --check && python manage.py collectstatic --noinput
```

The script keeps both original PNGs, writes `plumbing-hero.webp` (up to 960×640) and `service-scenes.webp` (up to 1024×1024), and prints the actual dimensions, byte size and saving. WebP quality defaults to 82; `--quality 60` through `--quality 95` is available. It rejects a misaligned atlas and derivatives larger than the original, strips metadata through RGB conversion, and replaces each derivative atomically with readable file permissions. `--check` reads and verifies the existing derivatives without changing files.

Django selects each WebP independently only when the file exists. Development checks source static files; production checks the local static storage that actually serves the collected release. A WebP generated in the source directory but not collected is never advertised in production. The template resolves every selected URL through Django's static storage, including a changed `STATIC_URL`. There is no browser image-probing request and no broken `srcset`. PNGs remain automatic fallbacks when optimization has not run. With a non-filesystem static backend, originals are selected without any per-request remote storage checks.

Run preparation again after replacing the source PNGs, then collect static files and reload the app page. Retain the original files when copying a release. Existing generated WebPs are optional derivative artifacts; this Windows coding machine did not generate or verify them. The selection tests are in `apps/common/test_miniapp_assets.py` and must also run on the verification machine. Confirm the images and crop framing visually there, especially at 320px and 390px widths and in Telegram's webview.

## Final prompt: hero

Use case: photorealistic-natural. Asset type: production website service hero photograph, not a UI mockup. Create one landscape editorial photograph for a modern plumbing service Mini App in Uzbekistan. A professional Central Asian male plumber in his early thirties wearing a plain navy work shirt, carefully adjusting a brushed chrome faucet at a clean white contemporary sink. Natural anatomically correct hands holding a real adjustable wrench around a fitting, believable tools and installation. Warm daylight, off-white tiled room, subtle pale blue and sage accents, authentic materials, refined quiet documentary photography. Framing: waist-up three-quarter view, human and faucet predominantly in the right two thirds, clean neutral background toward left; plumber face and tap both clearly visible, no exaggerated smile. Landscape 3:2 composition. No lettering, text, branding, badges, watermarks or graphical overlay. Real camera texture and fine details, avoid CGI, glossy 3D and illustration. This is an illustrative service photograph, not an identified real employee.

## Final prompt: service atlas

Use case: photorealistic-natural. Asset type: a single four-cell square photographic texture atlas for CSS category cards. Create ONE square image divided PRECISELY into a 2 by 2 grid of FOUR EQUAL square photographs edge to edge, no gutters, no borders, no padding, no rounded corners and no text. The division must lie exactly at the center of the image horizontally and vertically. Top-left square: close-up of a clean modern white panel heating radiator with brushed metal thermostat against warm cream plaster, radiator fills frame. Top-right square: brushed chrome faucet over a beautiful white ceramic bathroom basin, clean pale stone background, faucet fills frame. Bottom-left square: neatly installed gray drain pipes and white PPR water pipes with real joints beneath a clean basin, believable functional plumbing, no mess. Bottom-right square: close-up natural human hands of a plumber tightening a chrome pipe fitting with a blue-handled adjustable wrench, focus on fitting, no face. Every tile is an independent photorealistic editorial photograph with its main subject in the center, soft daylight, muted natural white/gray/blue colors, realistic material texture, balanced exposure and refined minimal photography. The four images must remain strictly in their own equal quadrants; no objects cross quadrant boundaries. No lettering, watermarks, logos, labels or collage frames. Not a website, not icons, not an illustration. Atlas will be cropped into four category photos using CSS.

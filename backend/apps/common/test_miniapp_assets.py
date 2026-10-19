from unittest.mock import patch

from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from apps.common.miniapp_assets import miniapp_images


class MiniAppImageSelectionTests(SimpleTestCase):
    @override_settings(DEBUG=True)
    def test_missing_derivatives_keep_both_originals(self):
        with patch("apps.common.miniapp_assets.finders.find", return_value=None):
            self.assertEqual(miniapp_images(), {
                "hero": "miniapp/images/plumbing-hero.png",
                "atlas": "miniapp/images/service-scenes.png",
            })

    @override_settings(DEBUG=True)
    def test_partial_preparation_selects_only_the_available_derivative(self):
        with patch("apps.common.miniapp_assets.finders.find", side_effect=["/static/hero.webp", None]):
            images = miniapp_images()
        self.assertTrue(images["hero"].endswith(".webp"))
        self.assertTrue(images["atlas"].endswith(".png"))

    @override_settings(DEBUG=False)
    def test_production_selects_collected_files_not_source_only_files(self):
        with patch("apps.common.miniapp_assets.finders.find") as find, \
                patch("apps.common.miniapp_assets.staticfiles_storage") as storage, \
                patch("apps.common.miniapp_assets.Path.is_file", return_value=True):
            storage.path.side_effect = lambda name: f"/srv/santex/static/{name}"
            images = miniapp_images()
            find.assert_not_called()
            self.assertEqual(storage.path.call_count, 2)
        self.assertTrue(all(path.endswith(".webp") for path in images.values()))

    @override_settings(DEBUG=False)
    def test_source_derivatives_are_not_advertised_until_collected(self):
        with patch("apps.common.miniapp_assets.staticfiles_storage") as storage, \
                patch("apps.common.miniapp_assets.Path.is_file", return_value=False):
            storage.path.side_effect = lambda name: f"/srv/santex/static/{name}"
            self.assertTrue(all(path.endswith(".png") for path in miniapp_images().values()))

    @override_settings(DEBUG=False)
    def test_remote_storage_does_not_trigger_network_exists_probes(self):
        with patch("apps.common.miniapp_assets.staticfiles_storage") as storage:
            storage.path.side_effect = NotImplementedError
            self.assertTrue(all(path.endswith(".png") for path in miniapp_images().values()))
            storage.exists.assert_not_called()

    @override_settings(STATIC_URL="/asset-prefix/")
    def test_page_resolves_asset_paths_through_static_storage(self):
        with patch("apps.common.views.miniapp_images", return_value={
            "hero": "miniapp/images/plumbing-hero.webp",
            "atlas": "miniapp/images/service-scenes.png",
        }):
            response = self.client.get(reverse("common:home"))
        self.assertContains(response, 'data-miniapp-hero="/asset-prefix/miniapp/images/plumbing-hero.webp"')
        self.assertContains(response, 'data-miniapp-atlas="/asset-prefix/miniapp/images/service-scenes.png"')
        self.assertEqual(response["Cache-Control"], "no-store")

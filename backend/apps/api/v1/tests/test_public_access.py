"""Public catalog access must not weaken private order/account boundaries."""
from rest_framework.test import APITestCase


class PublicCatalogAccessTests(APITestCase):
    def test_stale_or_missing_jwt_does_not_block_public_catalog(self):
        paths = ["regions/", "service-groups/", "services/", "materials/", "plumbers/", "stores/", "service-center/", "service-rates/?region=1"]
        for authorization in (None, "Bearer expired-or-invalid"):
            self.client.credentials(**({"HTTP_AUTHORIZATION": authorization} if authorization else {}))
            for path in paths:
                with self.subTest(authorization=authorization, path=path):
                    self.assertEqual(self.client.get(f"/api/v1/common/{path}").status_code, 200)

    def test_private_accounts_orders_and_admin_stay_protected(self):
        self.client.credentials()
        for path in ("auth/me/", "site/orders/", "admin/regions/"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(f"/api/v1/{path}").status_code, 401)
        self.assertEqual(self.client.post("/api/v1/site/orders/", {}, format="json").status_code, 401)

"""Catalog/provisioning authorization and input contracts over the real API."""
from datetime import time
from io import StringIO

from django.core.management import call_command
from django.db import DatabaseError, connection, transaction
from django.test import TestCase
from rest_framework.test import APITestCase

from apps.catalog.models import ContractTemplate, Region, ServiceCenter, ServiceGroup
from apps.common.audit import AuditEvent, record
from apps.users.models import User


class ManagementAPITests(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", is_staff=True)
        self.customer = User.objects.create_user(username="customer")

    def post(self, resource, payload, expected=201):
        self.client.force_authenticate(self.staff)
        response = self.client.post(f"/api/v1/admin/{resource}/", payload, format="json")
        self.assertEqual(response.status_code, expected, response.data)
        return response.data

    def test_staff_catalog_crud_public_catalog_filtering_and_audit(self):
        region = self.post("regions", {"name": "Marhamat", "code": "marhamat"})
        group = self.post("service-groups", {"name": "Ta’mir", "name_en": "Repair", "code": "repair"})
        service = self.post("services", {"name": "Kran", "group": group["id"], "unit": "dona", "warranty_days": 90})
        rate = self.post("service-rates", {"region": region["id"], "service": service["id"], "unit_price": "150000", "urgent_fee": "20000"})
        material = self.post("materials", {"name": "Quvur", "unit": "metr", "brand": "Test"})
        for resource, entity in (("regions", region), ("service-groups", group), ("services", service), ("service-rates", rate), ("materials", material)):
            with self.subTest(resource=resource):
                self.assertEqual(self.client.get(f"/api/v1/admin/{resource}/").status_code, 200)
                self.assertEqual(self.client.get(f"/api/v1/admin/{resource}/{entity['id']}/").status_code, 200)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/v1/common/service-rates/").status_code, 400)
        response = self.client.get(f"/api/v1/common/service-rates/?region={region['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["unit_price"], "150000.00")
        self.assertEqual(self.client.get("/api/v1/common/services/?group=bad").status_code, 400)
        for resource in ("regions", "service-groups", "services", "materials", "plumbers", "stores"):
            self.assertEqual(self.client.get(f"/api/v1/common/{resource}/").status_code, 200)
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.patch(f"/api/v1/admin/materials/{material['id']}/", {"name": "Yangi quvur"}, format="json").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/v1/admin/materials/{material['id']}/").status_code, 204)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(f"/api/v1/common/materials/{material['id']}/").status_code, 404)
        self.assertTrue(AuditEvent.objects.filter(actor=self.staff, action="api.deactivate").exists())

    def test_provision_partner_profiles_validate_role_and_hide_credentials(self):
        plumber = self.post("users", {"username": "plumber", "role": "plumber", "telegram_id": 501, "password": "LongRuntimePassword!901"})
        store = self.post("users", {"username": "store", "role": "store", "telegram_id": 502})
        self.assertNotIn("password", plumber)
        self.assertTrue(User.objects.get(pk=plumber["id"]).check_password("LongRuntimePassword!901"))
        self.assertFalse(User.objects.get(pk=store["id"]).has_usable_password())
        region = self.post("regions", {"name": "Marhamat", "code": "marhamat"})
        group = self.post("service-groups", {"name": "Ta’mir", "code": "repair"})
        profile = self.post("plumbers", {"user": plumber["id"], "regions": [region["id"]], "services": [group["id"]], "commission_rate": "10", "experience_years": 5})
        shop = self.post("stores", {"user": store["id"], "name": "Do‘kon", "address": "Test", "latitude": "40", "longitude": "72", "commission_rate": "5"})
        self.post("plumbers", {"user": store["id"], "regions": [], "services": []}, 400)
        self.post("stores", {"user": self.customer.pk, "name": "Wrong", "address": "Test"}, 400)
        self.post("users", {"username": "weak", "password": "123"}, 400)
        self.post("users", {"username": "elevation", "is_superuser": True}, 400)
        self.client.force_authenticate(self.customer)
        for resource in ("users", "plumbers", "stores", "regions", "service-groups", "services", "materials", "contract-templates", "audit-events"):
            with self.subTest(resource=resource):
                self.assertEqual(self.client.get(f"/api/v1/admin/{resource}/").status_code, 403)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(f"/api/v1/common/plumbers/{profile['id']}/photo/").status_code, 404)
        self.assertEqual(self.client.get(f"/api/v1/common/stores/{shop['id']}/").status_code, 200)

    def test_phone_verification_reset_staff_self_disable_and_role_reclassification(self):
        from django.utils import timezone
        target = User.objects.create_user(username="verified", telegram_id=551, phone_number="+998901111111", phone_verified_at=timezone.now())
        self.client.force_authenticate(self.staff)
        path = f"/api/v1/admin/users/{target.pk}/"
        self.assertEqual(self.client.patch(path, {"telegram_id": 552}, format="json").status_code, 200)
        target.refresh_from_db()
        self.assertIsNone(target.phone_verified_at)
        self.assertEqual(self.client.patch(path, {"role": "store"}, format="json").status_code, 400)
        self.assertEqual(self.client.patch(f"/api/v1/admin/users/{self.staff.pk}/", {"is_staff": False}, format="json").status_code, 400)
        self.assertEqual(self.client.delete(f"/api/v1/admin/users/{self.staff.pk}/").status_code, 400)

    def test_center_configuration_and_template_versioning(self):
        self.client.force_authenticate(self.staff)
        payload = {"name": "Markaz", "address": "Test", "phone": "+998901234567", "opening_time": "09:00", "closing_time": "18:00",
            "working_days": [0, 1, 2, 3, 4], "default_plumber_commission": "10", "default_store_commission": "5",
            "advance_kind": "percent", "advance_value": "50", "plumber_response_minutes": 20}
        self.assertEqual(self.client.put("/api/v1/admin/service-center/", payload, format="json").status_code, 200)
        self.assertEqual(self.client.patch("/api/v1/admin/service-center/", {"advance_value": "101"}, format="json").status_code, 400)
        self.assertEqual(self.client.patch("/api/v1/admin/service-center/", {"working_days": [7]}, format="json").status_code, 400)
        template = self.post("contract-templates", {"language": "uz", "version": 1, "text": "Test fixture"})
        path = f"/api/v1/admin/contract-templates/{template['id']}/"
        self.assertEqual(self.client.patch(path, {"text": "Mutated text"}, format="json").status_code, 400)
        self.assertEqual(self.client.patch(path, {"is_active": False}, format="json").status_code, 200)
        self.post("contract-templates", {"language": "uz", "version": 2, "text": "New fixture"})
        audit = AuditEvent.objects.filter(actor=self.staff).first()
        self.assertEqual(self.client.get(f"/api/v1/admin/audit-events/{audit.pk}/").status_code, 200)
        self.assertEqual(self.client.patch(f"/api/v1/admin/audit-events/{audit.pk}/", {"action": "tampered"}, format="json").status_code, 405)
        self.assertEqual(self.client.delete(f"/api/v1/admin/audit-events/{audit.pk}/").status_code, 405)
        self.client.force_authenticate(None)
        center = self.client.get("/api/v1/common/service-center/")
        self.assertEqual(center.status_code, 200)
        self.assertNotIn("default_plumber_commission", center.data)

    def test_seed_command_is_idempotent_and_does_not_invent_prices(self):
        output = StringIO()
        call_command("seed_pilot", stdout=output)
        call_command("seed_pilot", stdout=output)
        self.assertEqual(Region.objects.filter(code="andijon-marhamat").count(), 1)
        self.assertEqual(ServiceGroup.objects.count(), 4)
        self.assertFalse(ServiceCenter.objects.exists())
        self.assertFalse(ContractTemplate.objects.exists())

    def test_openapi_and_docs_are_staff_only_and_schema_is_generated(self):
        self.assertEqual(self.client.get("/api/schema/").status_code, 401)
        self.client.force_authenticate(self.customer)
        self.assertEqual(self.client.get("/api/schema/").status_code, 403)
        self.assertEqual(self.client.get("/api/docs/").status_code, 403)
        self.client.force_authenticate(self.staff)
        schema = self.client.get("/api/schema/")
        self.assertEqual(schema.status_code, 200)
        self.assertIn("/api/v1/site/orders/{id}/approve-quote/", schema.data["paths"])
        schemes = schema.data["components"]["securitySchemes"]
        self.assertEqual(schemes["jwtAuth"]["scheme"], "bearer")
        components = schema.data["components"]["schemas"]
        self.assertNotIn("is_active", components["PublicRegion"]["properties"])
        self.assertIn("is_active", components["Region"]["properties"])
        self.assertEqual(self.client.get("/api/docs/").status_code, 200)


class DatabaseAuditTests(TestCase):
    def test_audit_update_rejected_even_by_raw_sql(self):
        actor = User.objects.create_user(username="audit-actor")
        event = record(actor, "fixture", actor)
        with self.assertRaises(DatabaseError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("UPDATE common_auditevent SET action = %s WHERE id = %s", ["tampered", event.pk])
        event.refresh_from_db()
        self.assertEqual(event.action, "fixture")

    def test_template_raw_sql_mutation_rejected(self):
        template = ContractTemplate.objects.create(language="uz", version=1, text="Snapshot fixture")
        with self.assertRaises(DatabaseError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("UPDATE catalog_contracttemplate SET text = %s WHERE id = %s", ["tampered", template.pk])

"""Restore journal and contract triggers lost by SQLite table rebuilds."""
from importlib import import_module

from django.db import migrations


def restore_guards(apps, schema_editor):
    if schema_editor.connection.vendor == "sqlite":
        guards = import_module("apps.orders.migrations.0002_immutable_records")
        guards.unprotect_records(apps, schema_editor)
        guards.protect_records(apps, schema_editor)


class Migration(migrations.Migration):
    dependencies = [("orders", "0005_explicit_model_tables")]
    operations = [migrations.RunPython(restore_guards, migrations.RunPython.noop)]

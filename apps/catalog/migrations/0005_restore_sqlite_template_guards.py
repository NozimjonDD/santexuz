"""Restore template protection after SQLite rebuilds for BaseModel fields."""
from importlib import import_module

from django.db import migrations


def restore_guards(apps, schema_editor):
    if schema_editor.connection.vendor == "sqlite":
        guards = import_module("apps.catalog.migrations.0002_template_guards")
        guards.remove_guards(apps, schema_editor)
        guards.install_guards(apps, schema_editor)


class Migration(migrations.Migration):
    dependencies = [("catalog", "0004_explicit_model_tables")]
    operations = [migrations.RunPython(restore_guards, migrations.RunPython.noop)]

"""SQLite table rebuilds discard custom triggers during schema changes."""
from importlib import import_module

from django.db import migrations


def restore_guards(apps, schema_editor):
    if schema_editor.connection.vendor == "sqlite":
        guards = import_module("apps.common.migrations.0002_audit_guards")
        guards.remove_guards(apps, schema_editor)
        guards.install_guards(apps, schema_editor)


class Migration(migrations.Migration):
    dependencies = [("common", "0004_explicit_model_tables")]
    # Undoing a repair must not remove protections from existing audit events.
    operations = [migrations.RunPython(restore_guards, migrations.RunPython.noop)]

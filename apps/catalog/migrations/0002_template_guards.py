from django.db import migrations


def install_guards(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute("""
            CREATE FUNCTION santex_template_immutable() RETURNS trigger AS $$
            BEGIN
              IF TG_OP = 'DELETE' THEN
                RAISE EXCEPTION 'Contract templates must be versioned, not deleted';
              END IF;
              IF NEW.language IS DISTINCT FROM OLD.language OR NEW.version IS DISTINCT FROM OLD.version OR NEW.text IS DISTINCT FROM OLD.text THEN
                RAISE EXCEPTION 'Create a new contract template version';
              END IF;
              RETURN NEW;
            END; $$ LANGUAGE plpgsql;
        """)
        schema_editor.execute("CREATE TRIGGER template_immutable BEFORE UPDATE OR DELETE ON catalog_contracttemplate FOR EACH ROW EXECUTE FUNCTION santex_template_immutable()")
    elif schema_editor.connection.vendor == "sqlite":
        schema_editor.execute("CREATE TRIGGER template_no_update BEFORE UPDATE ON catalog_contracttemplate WHEN NEW.language <> OLD.language OR NEW.version <> OLD.version OR NEW.text <> OLD.text BEGIN SELECT RAISE(ABORT, 'Create a new contract template version'); END")
        schema_editor.execute("CREATE TRIGGER template_no_delete BEFORE DELETE ON catalog_contracttemplate BEGIN SELECT RAISE(ABORT, 'Contract templates must be versioned'); END")


def remove_guards(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute("DROP TRIGGER IF EXISTS template_immutable ON catalog_contracttemplate")
        schema_editor.execute("DROP FUNCTION IF EXISTS santex_template_immutable()")
    elif schema_editor.connection.vendor == "sqlite":
        schema_editor.execute("DROP TRIGGER IF EXISTS template_no_update")
        schema_editor.execute("DROP TRIGGER IF EXISTS template_no_delete")


class Migration(migrations.Migration):
    dependencies = [("catalog", "0001_initial")]
    operations = [migrations.RunPython(install_guards, remove_guards)]

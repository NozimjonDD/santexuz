from django.db import migrations


TABLES = ("orders_quote", "orders_payment", "orders_refund", "orders_settlement", "orders_cashhandover", "orders_orderevent")


def protect_records(apps, schema_editor):
    if schema_editor.connection.vendor == "sqlite":
        for table in TABLES:
            schema_editor.execute(f"CREATE TRIGGER {table}_no_update BEFORE UPDATE ON {table} BEGIN SELECT RAISE(ABORT, 'Immutable order record'); END")
            schema_editor.execute(f"CREATE TRIGGER {table}_no_delete BEFORE DELETE ON {table} BEGIN SELECT RAISE(ABORT, 'Immutable order record'); END")
        schema_editor.execute("""
            CREATE TRIGGER orders_contract_no_update BEFORE UPDATE ON orders_contract
            WHEN OLD.signed_at IS NOT NULL OR NEW.order_id IS NOT OLD.order_id OR
                 NEW.quote_id IS NOT OLD.quote_id OR NEW.language IS NOT OLD.language OR
                 NEW.template_version IS NOT OLD.template_version OR NEW.text_snapshot IS NOT OLD.text_snapshot OR
                 NEW.parties_snapshot IS NOT OLD.parties_snapshot
            BEGIN SELECT RAISE(ABORT, 'Contract snapshot cannot be changed'); END
        """)
        schema_editor.execute("CREATE TRIGGER orders_contract_no_delete BEFORE DELETE ON orders_contract BEGIN SELECT RAISE(ABORT, 'Contract snapshot cannot be deleted'); END")
        return
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute("""
        CREATE FUNCTION orders_reject_mutation() RETURNS trigger AS $$
        BEGIN RAISE EXCEPTION 'Immutable order record cannot be changed'; END;
        $$ LANGUAGE plpgsql;
    """)
    for table in TABLES:
        schema_editor.execute(f"CREATE TRIGGER {table}_immutable BEFORE UPDATE OR DELETE ON {table} FOR EACH ROW EXECUTE FUNCTION orders_reject_mutation();")
    schema_editor.execute("""
        CREATE FUNCTION orders_protect_contract() RETURNS trigger AS $$
        BEGIN
          IF TG_OP = 'DELETE' THEN
            RAISE EXCEPTION 'Contract snapshots cannot be deleted';
          END IF;
          IF OLD.signed_at IS NOT NULL OR
             ROW(NEW.order_id, NEW.quote_id, NEW.language, NEW.template_version, NEW.text_snapshot, NEW.parties_snapshot)
             IS DISTINCT FROM ROW(OLD.order_id, OLD.quote_id, OLD.language, OLD.template_version, OLD.text_snapshot, OLD.parties_snapshot) THEN
            RAISE EXCEPTION 'Contract snapshot cannot be changed';
          END IF;
          RETURN NEW;
        END; $$ LANGUAGE plpgsql;
        CREATE TRIGGER orders_contract_immutable BEFORE UPDATE OR DELETE ON orders_contract
        FOR EACH ROW EXECUTE FUNCTION orders_protect_contract();
    """)


def unprotect_records(apps, schema_editor):
    if schema_editor.connection.vendor == "sqlite":
        for table in TABLES:
            schema_editor.execute(f"DROP TRIGGER IF EXISTS {table}_no_update")
            schema_editor.execute(f"DROP TRIGGER IF EXISTS {table}_no_delete")
        schema_editor.execute("DROP TRIGGER IF EXISTS orders_contract_no_update")
        schema_editor.execute("DROP TRIGGER IF EXISTS orders_contract_no_delete")
        return
    if schema_editor.connection.vendor != "postgresql":
        return
    for table in TABLES:
        schema_editor.execute(f"DROP TRIGGER IF EXISTS {table}_immutable ON {table};")
    schema_editor.execute("DROP TRIGGER IF EXISTS orders_contract_immutable ON orders_contract;")
    schema_editor.execute("DROP FUNCTION IF EXISTS orders_protect_contract();")
    schema_editor.execute("DROP FUNCTION IF EXISTS orders_reject_mutation();")


class Migration(migrations.Migration):
    dependencies = [("orders", "0001_initial")]
    operations = [migrations.RunPython(protect_records, unprotect_records)]

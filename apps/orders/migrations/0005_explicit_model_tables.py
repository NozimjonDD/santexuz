from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("orders", "0004_immutable_basemodel_fields")]

    operations = [
        migrations.AlterModelTable(name="order", table="orders_order"),
        migrations.AlterModelTable(name="serviceitem", table="orders_serviceitem"),
        migrations.AlterModelTable(name="materialitem", table="orders_materialitem"),
        migrations.AlterModelTable(name="quote", table="orders_quote"),
        migrations.AlterModelTable(name="contract", table="orders_contract"),
        migrations.AlterModelTable(name="delivery", table="orders_delivery"),
        migrations.AlterModelTable(name="deliveryitem", table="orders_deliveryitem"),
        migrations.AlterModelTable(name="payment", table="orders_payment"),
        migrations.AlterModelTable(name="refund", table="orders_refund"),
        migrations.AlterModelTable(name="cashhandover", table="orders_cashhandover"),
        migrations.AlterModelTable(name="settlement", table="orders_settlement"),
        migrations.AlterModelTable(name="issue", table="orders_issue"),
        migrations.AlterModelTable(name="rating", table="orders_rating"),
        migrations.AlterModelTable(name="attachment", table="orders_attachment"),
        migrations.AlterModelTable(name="orderevent", table="orders_orderevent"),
    ]

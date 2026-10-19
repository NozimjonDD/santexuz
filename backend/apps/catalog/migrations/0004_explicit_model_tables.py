from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("catalog", "0003_catalog_basemodel_fields")]

    operations = [
        migrations.AlterModelTable(name="region", table="catalog_region"),
        migrations.AlterModelTable(name="servicegroup", table="catalog_servicegroup"),
        migrations.AlterModelTable(name="service", table="catalog_service"),
        migrations.AlterModelTable(name="servicerate", table="catalog_servicerate"),
        migrations.AlterModelTable(name="material", table="catalog_material"),
        migrations.AlterModelTable(name="servicecenter", table="catalog_servicecenter"),
        migrations.AlterModelTable(name="contracttemplate", table="catalog_contracttemplate"),
    ]

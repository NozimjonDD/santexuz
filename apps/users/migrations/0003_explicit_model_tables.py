from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("users", "0002_user_basemodel_fields")]

    operations = [
        migrations.AlterModelTable(name="user", table="users_user"),
        migrations.AlterModelTable(name="plumberprofile", table="users_plumberprofile"),
        migrations.AlterModelTable(name="store", table="users_store"),
    ]

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("tg_bot", "0002_tg_bot_basemodel_fields")]

    operations = [
        migrations.AlterModelTable(name="notification", table="tg_bot_notification"),
        migrations.AlterModelTable(name="botupdate", table="tg_bot_botupdate"),
    ]

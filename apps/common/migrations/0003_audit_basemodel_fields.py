import django.utils.timezone
from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):
    dependencies = [("common", "0002_audit_guards")]

    operations = [
        migrations.AddField(
            model_name="auditevent",
            name="updated_at",
            field=models.DateTimeField(
                auto_now=True,
                default=django.utils.timezone.now,
                verbose_name=_("Updated at"),
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="auditevent",
            name="is_deleted",
            field=models.BooleanField(default=False, verbose_name=_("Is deleted")),
        ),
        migrations.AddField(
            model_name="auditevent",
            name="deleted_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name=_("Deleted at"),
            ),
        ),
        migrations.AlterField(
            model_name="auditevent",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name=_("Date")),
        ),
    ]

import django.utils.timezone
from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


MODELS = ("notification", "botupdate")


class Migration(migrations.Migration):
    dependencies = [("tg_bot", "0001_initial")]

    operations = [
        *[
            migrations.AddField(
                model_name=model_name,
                name="updated_at",
                field=models.DateTimeField(
                    auto_now=True,
                    default=django.utils.timezone.now,
                    verbose_name=_("Updated at"),
                ),
                preserve_default=False,
            )
            for model_name in MODELS
        ],
        *[
            migrations.AddField(
                model_name=model_name,
                name="is_deleted",
                field=models.BooleanField(default=False, verbose_name=_("Is deleted")),
            )
            for model_name in MODELS
        ],
        *[
            migrations.AddField(
                model_name=model_name,
                name="deleted_at",
                field=models.DateTimeField(
                    blank=True,
                    null=True,
                    verbose_name=_("Deleted at"),
                ),
            )
            for model_name in MODELS
        ],
        *[
            migrations.AlterField(
                model_name=model_name,
                name="created_at",
                field=models.DateTimeField(auto_now_add=True, verbose_name=_("Date")),
            )
            for model_name in MODELS
        ],
    ]

from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


TIMESTAMPED_MODELS = (
    "order",
    "serviceitem",
    "materialitem",
    "contract",
    "delivery",
    "issue",
    "rating",
    "attachment",
)


class Migration(migrations.Migration):
    dependencies = [("orders", "0002_immutable_records")]

    operations = [
        *[
            migrations.AddField(
                model_name=model_name,
                name="is_deleted",
                field=models.BooleanField(default=False, verbose_name="Is deleted"),
            )
            for model_name in TIMESTAMPED_MODELS
        ],
        *[
            migrations.AddField(
                model_name=model_name,
                name="deleted_at",
                field=models.DateTimeField(
                    blank=True,
                    null=True,
                    verbose_name="Deleted at",
                ),
            )
            for model_name in TIMESTAMPED_MODELS
        ],
        *[
            migrations.AlterField(
                model_name=model_name,
                name="created_at",
                field=models.DateTimeField(
                    auto_now_add=True,
                    verbose_name=_("Date"),
                ),
            )
            for model_name in TIMESTAMPED_MODELS
        ],
        *[
            migrations.AlterField(
                model_name=model_name,
                name="updated_at",
                field=models.DateTimeField(
                    auto_now=True,
                    verbose_name=_("Updated at"),
                ),
            )
            for model_name in TIMESTAMPED_MODELS
        ],
    ]

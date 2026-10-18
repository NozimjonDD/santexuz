import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


def create_existing_consumer_profiles(apps, schema_editor):
    User = apps.get_model("users", "User")
    Consumer = apps.get_model("users", "Consumer")
    database = schema_editor.connection.alias
    Consumer.objects.using(database).bulk_create(
        Consumer(user_id=user_id)
        for user_id in User.objects.using(database).filter(role="customer").values_list("pk", flat=True)
    )


class Migration(migrations.Migration):
    dependencies = [("users", "0003_explicit_model_tables")]

    operations = [
        migrations.CreateModel(
            name="Consumer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name=_("Date"))),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))),
                ("is_deleted", models.BooleanField(default=False, verbose_name=_("Is deleted"))),
                ("deleted_at", models.DateTimeField(blank=True, null=True, verbose_name=_("Deleted at"))),
                ("address", models.TextField(blank=True)),
                ("latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(-90), django.core.validators.MaxValueValidator(90)])),
                ("longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)])),
                ("user", models.OneToOneField(limit_choices_to={"role": "customer"}, on_delete=django.db.models.deletion.PROTECT, related_name="consumer_profile", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "users_consumer",
                "constraints": [
                    models.CheckConstraint(condition=models.Q(latitude__isnull=True) | models.Q(latitude__gte=-90, latitude__lte=90), name="consumer_latitude_range"),
                    models.CheckConstraint(condition=models.Q(longitude__isnull=True) | models.Q(longitude__gte=-180, longitude__lte=180), name="consumer_longitude_range"),
                ],
            },
        ),
        migrations.RunPython(create_existing_consumer_profiles, migrations.RunPython.noop),
    ]

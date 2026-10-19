import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name="BotUpdate", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("update_id", models.BigIntegerField(unique=True)), ("created_at", models.DateTimeField(auto_now_add=True)),
        ]),
        migrations.CreateModel(name="Notification", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("event", models.CharField(max_length=100)), ("order_id", models.BigIntegerField(blank=True, null=True)),
            ("payload", models.JSONField(default=dict)), ("created_at", models.DateTimeField(auto_now_add=True)),
            ("sent_at", models.DateTimeField(blank=True, null=True)), ("read_at", models.DateTimeField(blank=True, null=True)),
            ("attempts", models.PositiveIntegerField(default=0)),
            ("next_attempt_at", models.DateTimeField(default=django.utils.timezone.now)),
            ("last_error", models.CharField(blank=True, max_length=100)),
            ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
        ], options={"ordering": ["-id"], "indexes": [models.Index(fields=["sent_at", "next_attempt_at"], name="notification_pending_idx")]}),
    ]

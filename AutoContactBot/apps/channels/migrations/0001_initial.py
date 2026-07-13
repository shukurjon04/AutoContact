from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Channel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("telegram_id", models.BigIntegerField(unique=True)),
                ("username", models.CharField(blank=True, max_length=128, null=True)),
                ("description", models.TextField(blank=True, default="")),
                ("is_active", models.BooleanField(default=True)),
                ("bot_is_admin", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Kanal / Guruh",
                "verbose_name_plural": "Kanallar / Guruhlar",
                "db_table": "channels",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Tariff",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                (
                    "channel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tariffs",
                        to="channels.channel",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "duration_days",
                    models.PositiveIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(100)],
                    ),
                ),
                (
                    "discount_percent",
                    models.DecimalField(decimal_places=2, default=0, max_digits=5),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Tarif",
                "verbose_name_plural": "Tariflar",
                "db_table": "tariffs",
                "ordering": ["channel", "sort_order", "duration_days"],
            },
        ),
    ]

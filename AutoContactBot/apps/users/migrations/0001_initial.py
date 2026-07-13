from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TelegramUser",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("telegram_id", models.BigIntegerField(db_index=True, unique=True)),
                ("username", models.CharField(blank=True, max_length=128, null=True)),
                ("first_name", models.CharField(blank=True, default="", max_length=255)),
                ("last_name", models.CharField(blank=True, default="", max_length=255)),
                ("is_bot_blocked", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("language_code", models.CharField(default="uz", max_length=10)),
                ("registered_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Telegram foydalanuvchi",
                "verbose_name_plural": "Telegram foydalanuvchilar",
                "db_table": "telegram_users",
                "ordering": ["-registered_at"],
            },
        ),
    ]

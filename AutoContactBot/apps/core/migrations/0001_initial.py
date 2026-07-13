from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PaymentSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "card_number",
                    models.CharField(
                        default="8600 0000 0000 0000",
                        help_text="Karta raqami (masalan: 8600 1234 5678 9010)",
                        max_length=20,
                    ),
                ),
                (
                    "card_owner",
                    models.CharField(
                        default="Falonchi Pistonchiyev",
                        help_text="Karta egasining ismi va familyasi",
                        max_length=255,
                    ),
                ),
            ],
            options={
                "verbose_name": "To'lov sozlamalari",
                "verbose_name_plural": "To'lov sozlamalari",
            },
        ),
    ]

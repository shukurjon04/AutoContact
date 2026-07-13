import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0001_initial"),
        ("channels", "0001_initial"),
        ("subscriptions", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transactions",
                        to="users.telegramuser",
                    ),
                ),
                (
                    "channel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transactions",
                        to="channels.channel",
                    ),
                ),
                (
                    "tariff",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="transactions",
                        to="channels.tariff",
                    ),
                ),
                (
                    "subscription",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="transactions",
                        to="subscriptions.subscription",
                    ),
                ),
                ("payme_transaction_id", models.CharField(blank=True, db_index=True, max_length=255, null=True, unique=True)),
                ("payme_state", models.IntegerField(blank=True, null=True)),
                ("amount", models.BigIntegerField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Kutilmoqda"),
                            ("paid", "To'landi"),
                            ("cancelled", "Bekor qilindi"),
                            ("failed", "Muvaffaqiyatsiz"),
                        ],
                        db_index=True,
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("cancelled_at", models.DateTimeField(blank=True, null=True)),
                ("cancel_reason", models.IntegerField(blank=True, null=True)),
                ("payme_create_time", models.BigIntegerField(blank=True, null=True)),
                ("payme_perform_time", models.BigIntegerField(blank=True, null=True)),
                ("payme_cancel_time", models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Tranzaksiya",
                "verbose_name_plural": "Tranzaksiyalar",
                "db_table": "transactions",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="transaction",
            index=models.Index(fields=["user", "status"], name="tx_user_status_idx"),
        ),
        migrations.AddIndex(
            model_name="transaction",
            index=models.Index(fields=["payme_transaction_id"], name="tx_payme_id_idx"),
        ),
    ]

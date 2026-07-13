import uuid
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0001_initial"),
        ("channels", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Subscription",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscriptions",
                        to="users.telegramuser",
                    ),
                ),
                (
                    "channel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscriptions",
                        to="channels.channel",
                    ),
                ),
                (
                    "tariff",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="subscriptions",
                        to="channels.tariff",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Faol"),
                            ("expired", "Muddati tugagan"),
                            ("cancelled", "Bekor qilingan"),
                        ],
                        db_index=True,
                        default="active",
                        max_length=20,
                    ),
                ),
                ("start_date", models.DateTimeField(default=django.utils.timezone.now)),
                ("end_date", models.DateTimeField(db_index=True)),
                ("invite_link_sent", models.BooleanField(default=False)),
                (
                    "invite_link_delivery_status",
                    models.CharField(
                        choices=[("sent", "Yuborildi"), ("failed", "Yuborilmadi"), ("pending", "Kutilmoqda")],
                        default="pending",
                        max_length=20,
                    ),
                ),
                (
                    "reminder_sent",
                    models.CharField(
                        choices=[
                            ("none", "Yuborilmagan"),
                            ("3d", "3 kun qolganida"),
                            ("1d", "1 kun qolganida"),
                            ("1h", "1 soat qolganida"),
                        ],
                        default="none",
                        max_length=10,
                    ),
                ),
                ("extended_by_admin", models.BooleanField(default=False)),
                ("admin_note", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Obuna",
                "verbose_name_plural": "Obunalar",
                "db_table": "subscriptions",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="subscription",
            index=models.Index(fields=["user", "channel", "status"], name="sub_user_channel_status_idx"),
        ),
        migrations.AddIndex(
            model_name="subscription",
            index=models.Index(fields=["status", "end_date"], name="sub_status_enddate_idx"),
        ),
        migrations.CreateModel(
            name="AdminAction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("admin_telegram_id", models.BigIntegerField()),
                (
                    "subscription",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="admin_actions",
                        to="subscriptions.subscription",
                    ),
                ),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("extend", "Muddatni uzaytirish"),
                            ("cancel", "Obunani bekor qilish"),
                            ("kick", "Guruhdan chiqarish"),
                            ("grant", "Bepul obuna berish"),
                        ],
                        max_length=20,
                    ),
                ),
                ("details", models.JSONField(default=dict)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Admin amali",
                "verbose_name_plural": "Admin amallari",
                "db_table": "admin_actions",
                "ordering": ["-timestamp"],
            },
        ),
    ]

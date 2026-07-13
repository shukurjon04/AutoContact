import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0001_initial"),
        ("channels", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Broadcast",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("text", models.TextField(max_length=4096)),
                ("photo", models.ImageField(blank=True, null=True, upload_to="broadcasts/")),
                (
                    "target_type",
                    models.CharField(
                        choices=[
                            ("all", "Barcha foydalanuvchilar"),
                            ("channel", "Kanal obunachilari"),
                            ("expiring", "Muddati tugayotganlar"),
                        ],
                        default="all",
                        max_length=20,
                    ),
                ),
                (
                    "target_channel",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="broadcasts",
                        to="channels.channel",
                    ),
                ),
                ("expiring_days", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Tayyorlanmoqda"),
                            ("in_progress", "Yuborilmoqda"),
                            ("completed", "Yakunlandi"),
                            ("failed", "Xatolik"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("total_count", models.PositiveIntegerField(default=0)),
                ("sent_count", models.PositiveIntegerField(default=0)),
                ("failed_count", models.PositiveIntegerField(default=0)),
                ("created_by", models.CharField(default="admin", max_length=128)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Broadcast",
                "verbose_name_plural": "Broadcastlar",
                "db_table": "broadcasts",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="BroadcastRecipient",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                (
                    "broadcast",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipients",
                        to="notifications.broadcast",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="broadcast_receipts",
                        to="users.telegramuser",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Kutilmoqda"),
                            ("sent", "Yuborildi"),
                            ("failed", "Yuborilmadi"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Broadcast qabul qiluvchi",
                "verbose_name_plural": "Broadcast qabul qiluvchilar",
                "db_table": "broadcast_recipients",
            },
        ),
        migrations.AlterUniqueTogether(
            name="broadcastrecipient",
            unique_together={("broadcast", "user")},
        ),
    ]

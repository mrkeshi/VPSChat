from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="RoomVerifiedBadge",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_key", models.CharField(max_length=64)),
                ("display_name", models.CharField(blank=True, default="", max_length=80)),
                ("granted_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("room", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="verified_badges", to="chat.room")),
            ],
        ),
        migrations.AddField(
            model_name="message",
            name="sender_session_key",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
        migrations.AddField(
            model_name="message",
            name="sender_is_admin",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="message",
            name="sender_is_verified",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="message",
            name="reply_to",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="replies", to="chat.message"),
        ),
        migrations.AddIndex(
            model_name="message",
            index=models.Index(fields=["room", "timestamp"], name="msg_room_ts_idx"),
        ),
        migrations.AddIndex(
            model_name="message",
            index=models.Index(fields=["room", "type"], name="msg_room_type_idx"),
        ),
        migrations.AlterUniqueTogether(
            name="roomverifiedbadge",
            unique_together={("room", "session_key")},
        ),
        migrations.AddIndex(
            model_name="roomverifiedbadge",
            index=models.Index(fields=["room", "session_key"], name="badge_room_sess_idx"),
        ),
        migrations.CreateModel(
            name="MessageReceipt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_key", models.CharField(max_length=64)),
                ("delivered_at", models.DateTimeField(blank=True, null=True)),
                ("seen_at", models.DateTimeField(blank=True, null=True)),
                ("message", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="receipts", to="chat.message")),
            ],
        ),
        migrations.AlterUniqueTogether(
            name="messagereceipt",
            unique_together={("message", "session_key")},
        ),
        migrations.AddIndex(
            model_name="messagereceipt",
            index=models.Index(fields=["message", "session_key"], name="rcpt_msg_sess_idx"),
        ),
        migrations.AddIndex(
            model_name="messagereceipt",
            index=models.Index(fields=["message", "delivered_at"], name="rcpt_msg_del_idx"),
        ),
        migrations.AddIndex(
            model_name="messagereceipt",
            index=models.Index(fields=["message", "seen_at"], name="rcpt_msg_seen_idx"),
        ),
    ]

# Generated manually for initial setup
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django.core.validators

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
                ('slug', models.SlugField(max_length=140, unique=True, validators=[django.core.validators.RegexValidator(message='Slug must contain only lowercase letters, digits and hyphens.', regex='^[a-z0-9-]+$')])),
                ('is_protected', models.BooleanField(default=False)),
                ('password_hash', models.CharField(blank=True, max_length=256, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_name', models.CharField(max_length=80)),
                ('content', models.TextField(blank=True, default='')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('type', models.CharField(choices=[('text', 'Text'), ('file', 'File'), ('system', 'System')], default='text', max_length=10)),
                ('file', models.FileField(blank=True, null=True, upload_to='uploads/%Y/%m/%d/')),
                ('file_name', models.CharField(blank=True, default='', max_length=255)),
                ('uploader_session_key', models.CharField(blank=True, default='', max_length=64)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.room')),
            ],
            options={'ordering': ['timestamp']},
        ),
        migrations.CreateModel(
            name='RoomPresence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=64)),
                ('display_name', models.CharField(max_length=80)),
                ('last_seen_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_online', models.BooleanField(default=False)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='presences', to='chat.room')),
            ],
        ),
        migrations.AddIndex(
            model_name='roompresence',
            index=models.Index(fields=['room', 'is_online'], name='chat_roompr_room_id_1e6107_idx'),
        ),
        migrations.AddIndex(
            model_name='roompresence',
            index=models.Index(fields=['room', 'last_seen_at'], name='chat_roompr_room_id_3b02fa_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='roompresence',
            unique_together={('room', 'session_key')},
        ),
    ]

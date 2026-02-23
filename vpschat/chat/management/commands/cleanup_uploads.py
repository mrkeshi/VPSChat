from __future__ import annotations

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from chat.models import Message

class Command(BaseCommand):
    help = "پاک‌سازی فایل‌های قدیمی آپلودشده (بر اساس سن پیام فایل)."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=30, help="فایل‌های قدیمی‌تر از این تعداد روز حذف شوند.")
        parser.add_argument("--dry-run", action="store_true", help="فقط نمایش؛ بدون حذف واقعی.")

    def handle(self, *args, **opts):
        days = opts["days"]
        dry = opts["dry_run"]
        cutoff = timezone.now() - timedelta(days=days)

        qs = Message.objects.filter(type=Message.TYPE_FILE, timestamp__lt=cutoff).exclude(file="")
        total = qs.count()
        self.stdout.write(self.style.WARNING(f"Found {total} old file messages older than {days} days."))

        deleted = 0
        for msg in qs.iterator():
            if msg.file:
                self.stdout.write(f"- {msg.id} {msg.file.name}")
                if not dry:
                    msg.file.delete(save=False)
                    msg.delete()
                    deleted += 1

        if dry:
            self.stdout.write(self.style.SUCCESS("Dry run finished."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} messages + files."))

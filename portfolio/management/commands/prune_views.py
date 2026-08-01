from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from portfolio.models import PageView


class Command(BaseCommand):
    help = 'Delete PageView rows older than PAGEVIEW_RETENTION_DAYS. Run from cron.'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=settings.PAGEVIEW_RETENTION_DAYS)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=options['days'])
        qs = PageView.objects.filter(created_at__lt=cutoff)
        count = qs.count()

        if options['dry_run']:
            self.stdout.write(f'Would delete {count} view(s) older than {cutoff:%Y-%m-%d}.')
            return

        qs.delete()
        self.stdout.write(self.style.SUCCESS(
            f'Deleted {count} view(s) older than {cutoff:%Y-%m-%d}.'
        ))

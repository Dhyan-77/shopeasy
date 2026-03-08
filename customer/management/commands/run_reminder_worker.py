import time
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from customer.models import Due, Notification


class Command(BaseCommand):
    help = "Runs a simple polling reminder worker (no Celery/Redis)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--interval",
            type=int,
            default=15,
            help="Poll interval in seconds",
        )

    def handle(self, *args, **options):
        interval = options["interval"]

        self.stdout.write(
            self.style.SUCCESS(
                f"Reminder worker started. Polling every {interval}s"
            )
        )

        try:
            while True:
                now = timezone.now()

                with transaction.atomic():

                    dues = (
                        Due.objects
                        .select_for_update(skip_locked=True)
                        .filter(
                            status="pending",
                            due_at__lte=now,
                            reminded_at__isnull=True,
                            user__subscription__status="active"
                        )
                        .select_related("customer", "user")
                        .order_by("due_at")[:50]
                    )

                    for due in dues:
                        try:
                            amount = due.amount_paise // 100

                            Notification.objects.create(
                                user=due.user,
                                title="Payment Reminder",
                                message=f"{due.customer.name} ₹{amount} due now",
                                due=due
                            )

                            due.reminded_at = now
                            due.reminder_sent_count += 1
                            due.save(
                                update_fields=[
                                    "reminded_at",
                                    "reminder_sent_count",
                                    "updated_at"
                                ]
                            )

                            self.stdout.write(
                                f"[REMINDER] {due.customer.name} ₹{amount}"
                            )

                        except Exception as e:
                            self.stderr.write(
                                f"Reminder failed for {due.id}: {str(e)}"
                            )

                time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING("Reminder worker stopped")
            )
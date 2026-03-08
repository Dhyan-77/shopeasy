from django.db import models
from django.conf import settings

class Subscription(models.Model):
    class Status(models.TextChoices):
        CREATED = "created", "Created"
        ACTIVE = "active", "Active"
        HALTED = "halted", "Halted"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"
        EXPIRED = "expired", "Expired"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription"
    )

    razorpay_subscription_id = models.CharField(max_length=100, unique=True)
    razorpay_plan_id = models.CharField(max_length=100)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)

    current_start = models.DateTimeField(null=True, blank=True)
    current_end = models.DateTimeField(null=True, blank=True)

    total_count = models.PositiveIntegerField(default=12)
    paid_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
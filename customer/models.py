from django.db import models
import uuid
from django.conf import settings
from django.utils import timezone



class Customers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name="customers",
        db_index=True, )

    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20) 
    notes = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    class Meta:
        unique_together = [("user", "phone")]
        indexes = [
            models.Index(fields=["user", "name"]),
            models.Index(fields=["user", "phone"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.phone})"




class Due(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dues",
        db_index=True,
    )
    customer = models.ForeignKey(
        Customers,
        on_delete=models.CASCADE,
        related_name="dues",
        db_index=True,
    )

    amount_paise = models.PositiveIntegerField()  # money safe
    currency = models.CharField(max_length=8, default="INR")

    due_at = models.DateTimeField(db_index=True)  # timezone-aware
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    reminded_at = models.DateTimeField(null=True, blank=True)
    reminder_sent_count = models.PositiveSmallIntegerField(default=0)

    # Optional custom message template per due
    message_template = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "status", "due_at"]),
            models.Index(fields=["customer", "status", "due_at"]),
        ]

    def __str__(self):
        return f"{self.customer.name} ₹{self.amount_paise/100:.2f} due {self.due_at}"

    @property
    def is_overdue(self):
        return self.status == self.Status.PENDING and self.due_at <= timezone.now()
    




class Notification(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=200)
    message = models.TextField()

    due = models.ForeignKey(
        Due,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    
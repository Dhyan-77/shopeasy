from rest_framework import serializers
from .models import Customers, Due
from .models import Notification

class CustomersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields = ("id", "name", "phone", "notes", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class DueSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    customer_phone = serializers.CharField(source="customer.phone", read_only=True)

    class Meta:
        model = Due
        fields = (
            "id",
            "customer",
            "customer_name",
            "customer_phone",
            "amount_paise",
            "currency",
            "due_at",
            "status",
            "reminded_at",
            "reminder_sent_count",
            "message_template",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "currency",
            "reminded_at",
            "reminder_sent_count",
            "created_at",
            "updated_at",
        )
def validate_status(self, value):
    value = (value or "").strip().lower()
    return value







class NotificationSerializer(serializers.ModelSerializer):

    customer_name = serializers.CharField(
        source="due.customer.name",
        read_only=True
    )

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "is_read",
            "created_at",
            "due",
            "customer_name",
        ]


class DashboardDueSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name")
    amount = serializers.SerializerMethodField()
    due_date = serializers.DateTimeField(source="due_at")

    class Meta:
        model = Due
        fields = ["id", "customer_name", "amount", "due_date", "status"]

    def get_amount(self, obj):
        return obj.amount_paise / 100
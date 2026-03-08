import json
import hmac
import hashlib
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from .models import Subscription

class RazorpayWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        body = request.body
        signature = request.headers.get("X-Razorpay-Signature", "")

        expected = hmac.new(
            bytes(settings.RAZORPAY_WEBHOOK_SECRET, "utf-8"),
            body,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected):
            return HttpResponse(status=400)

        payload = json.loads(body)
        event = payload.get("event")
        entity = payload.get("payload", {})

        sub_data = (
            entity.get("subscription", {}).get("entity")
            or entity.get("payment", {}).get("entity", {})
        )

        subscription_id = sub_data.get("id") or sub_data.get("subscription_id")
        if subscription_id:
            sub = Subscription.objects.filter(
                razorpay_subscription_id=subscription_id
            ).first()

            if sub:
                if event in ["subscription.activated", "subscription.charged"]:
                    sub.status = "active"
                elif event in ["subscription.cancelled"]:
                    sub.status = "cancelled"
                elif event in ["subscription.completed"]:
                    sub.status = "completed"
                elif event in ["subscription.halted"]:
                    sub.status = "halted"

                sub.save(update_fields=["status", "updated_at"])

        return HttpResponse(status=200)
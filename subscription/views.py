import razorpay
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class CreateSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        existing = getattr(request.user, "subscription", None)
        if existing and existing.status in ["active", "created"]:
            return Response({
                "subscription_id": existing.razorpay_subscription_id,
                "key": settings.RAZORPAY_KEY_ID,
            })

        razorpay_sub = client.subscription.create({
            "plan_id": settings.RAZORPAY_YEARLY_PLAN_ID,
            "total_count": 12,
            "customer_notify": 1,
            "notes": {
                "user_id": str(request.user.id),
                "email": request.user.email,
            }
        })

        from .models import Subscription
        Subscription.objects.update_or_create(
            user=request.user,
            defaults={
                "razorpay_subscription_id": razorpay_sub["id"],
                "razorpay_plan_id": settings.RAZORPAY_YEARLY_PLAN_ID,
                "status": razorpay_sub["status"],
                "total_count": razorpay_sub.get("total_count", 12),
                "paid_count": razorpay_sub.get("paid_count", 0),
            }
        )

        return Response({
            "subscription_id": razorpay_sub["id"],
            "key": settings.RAZORPAY_KEY_ID,
        })
    

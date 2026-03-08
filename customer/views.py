from django.db.models import Q
from django.utils import timezone
from.serializers import NotificationSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Notification
from .models import Customers, Due
from .serializers import CustomersSerializer, DueSerializer
from django.db.models import Sum
import urllib.parse
from rest_framework.views import APIView
from urllib.parse import quote
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import DashboardDueSerializer
from .models import Due
from subscription.permission import HasActiveSubscription

# -------------------------
# Customers
# -------------------------

class CustomersListCreateView(generics.ListCreateAPIView):
    serializer_class = CustomersSerializer
    permission_classes = [permissions.IsAuthenticated,HasActiveSubscription]

    def get_queryset(self):
        qs = Customers.objects.filter(user=self.request.user).order_by("-created_at")
        q = self.request.query_params.get("q")
        if q:
            q = q.strip()
            qs = qs.filter(Q(name__icontains=q) | Q(phone__icontains=q))
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CustomersDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomersSerializer
    permission_classes = [permissions.IsAuthenticated,HasActiveSubscription]

    def get_queryset(self):
        return Customers.objects.filter(user=self.request.user)


# -------------------------
# Dues
# -------------------------

class DueListCreateView(generics.ListCreateAPIView):
    serializer_class = DueSerializer
    permission_classes = [permissions.IsAuthenticated,HasActiveSubscription]

    def get_queryset(self):
        qs = (
            Due.objects.filter(user=self.request.user)
            .select_related("customer")
            .order_by("due_at")
        )

        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        # overdue=1 => pending & due_at <= now
        if self.request.query_params.get("overdue") == "1":
            qs = qs.filter(status="pending", due_at__lte=timezone.now())

        # optional: filter by customer
        customer_id = self.request.query_params.get("customer")
        if customer_id:
            qs = qs.filter(customer_id=customer_id)

        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DueDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DueSerializer
    permission_classes = [permissions.IsAuthenticated,HasActiveSubscription]

    def get_queryset(self):
        return Due.objects.filter(user=self.request.user).select_related("customer")


class DueMarkPaidView(APIView):
    permission_classes = [permissions.IsAuthenticated,HasActiveSubscription]

    def post(self, request, pk):
        due = Due.objects.filter(user=request.user, pk=pk).first()
        if not due:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        due.status = "paid"
        due.save(update_fields=["status", "updated_at"])
        return Response({"message": "Marked as paid"}, status=status.HTTP_200_OK)


class DueCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated,HasActiveSubscription]

    def post(self, request, pk):
        due = Due.objects.filter(user=request.user, pk=pk).first()
        if not due:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        due.status = "cancelled"
        due.save(update_fields=["status", "updated_at"])
        return Response({"message": "Cancelled"}, status=status.HTTP_200_OK)







class DueWhatsappLinkView(APIView):
    permission_classes = [IsAuthenticated,HasActiveSubscription]

    def get(self, request, pk):
        due = Due.objects.filter(user=request.user, pk=pk).select_related("customer").first()
        if not due:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        customer = due.customer

        # Clean phone: keep digits only
        phone = "".join(ch for ch in (customer.phone or "") if ch.isdigit())

        amount = due.amount_paise / 100

        # Use custom template if set, else default
        if due.message_template.strip():
            msg = due.message_template.strip()
        else:
            msg = f"Hi {customer.name}, your payment of ₹{amount:.0f} is due. Please clear it. Thanks."

        wa_url = f"https://wa.me/{phone}?text={quote(msg)}"
        return Response({"wa_url": wa_url, "message": msg})



class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated,HasActiveSubscription]

    def get(self, request):
        user = request.user
        now = timezone.now()

        pending_qs = Due.objects.filter(user=user, status="pending")

        total_pending = pending_qs.count()

        overdue = pending_qs.filter(
            due_at__lt=now
        ).count()

        due_today = pending_qs.filter(
            due_at__date=now.date()
        ).count()

        total_amount_paise = pending_qs.aggregate(
            total=Sum("amount_paise")
        )["total"] or 0

        total_amount = total_amount_paise / 100

        # newest dues first
        recent_dues = pending_qs.select_related("customer").order_by("due_at")[:10]

        return Response({
            "user": {
                "email": user.email,
                "name": user.username
            },
            "stats": {
                "total_pending": total_pending,
                "overdue": overdue,
                "due_today": due_today,
                "total_amount": total_amount
            },
            "dues": DashboardDueSerializer(recent_dues, many=True).data
        })


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by("-created_at")    
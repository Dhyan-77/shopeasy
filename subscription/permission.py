from rest_framework.permissions import BasePermission
from .models import Subscription


class HasActiveSubscription(BasePermission):

    message = "Your subscription has expired. Please subscribe to continue."

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        sub = getattr(request.user, "subscription", None)

        if not sub:
            return False

        return sub.status == "active"
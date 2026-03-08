from django.urls import path
from .views import (
    CustomersListCreateView, CustomersDetailView,
    DueListCreateView, DueDetailView,
    DueMarkPaidView, DueCancelView,
)

from .views import DueWhatsappLinkView
from .views import DashboardView
from .views import NotificationListView
urlpatterns = [
    # Customers
    path("customers/", CustomersListCreateView.as_view(), name="customers-list-create"),
    path("customers/<uuid:pk>/", CustomersDetailView.as_view(), name="customers-detail"),

    # Dues
    path("dues/", DueListCreateView.as_view(), name="dues-list-create"),
    path("dues/<uuid:pk>/", DueDetailView.as_view(), name="dues-detail"),
    path("dues/<uuid:pk>/mark-paid/", DueMarkPaidView.as_view(), name="dues-mark-paid"),
    path("dues/<uuid:pk>/cancel/", DueCancelView.as_view(), name="dues-cancel"),
    path("dues/<uuid:pk>/whatsapp-link/", DueWhatsappLinkView.as_view(), name="dues-whatsapp-link"),
    path("dashboard/", DashboardView.as_view()),
    path("notifications/", NotificationListView.as_view()),
]
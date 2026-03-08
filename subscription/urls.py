from django.urls import path
from .views import CreateSubscriptionView
from .webhook import RazorpayWebhookView
urlpatterns = [
    path("billing/create-subscription/", CreateSubscriptionView.as_view()),
    path("billing/webhook/", RazorpayWebhookView.as_view()),
]    
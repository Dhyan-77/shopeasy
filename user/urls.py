from django.urls import path
from .views import SignupView
from rest_framework_simplejwt.views import TokenObtainPairView ,TokenRefreshView
urlpatterns = [
    path('login/',TokenObtainPairView.as_view()),
    path('signup/',SignupView.as_view() ),
    path('refresh/',TokenRefreshView.as_view())
   
]

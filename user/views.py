from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.utils import timezone
from .serializers import signupserializers

class SignupView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        serializer = signupserializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "Signup successful",
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                },
            },
            status=status.HTTP_201_CREATED,
        )



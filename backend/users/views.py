from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model

from .serializers import UserSerializer, CreateUserSerializer

User = get_user_model()


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email et mot de passe requis."}, status=400)

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response({"error": "Identifiants invalides."}, status=401)

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data
        })


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != "Admin":
            raise PermissionDenied("Seuls les administrateurs peuvent créer des comptes.")
        serializer.save()

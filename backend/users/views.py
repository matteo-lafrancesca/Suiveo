from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

from .serializers import UserSerializer, CreateUserSerializer, InviteSupervisorSerializer, CompleteRegistrationSerializer

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

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response({"error": "Ancien et nouveau mot de passe requis."}, status=400)

        # Vérification ancien mot de passe
        if not user.check_password(old_password):
             return Response({"error": "Ancien mot de passe incorrect."}, status=400)

        # Application nouveau mot de passe
        user.set_password(new_password)
        user.save()
        
        return Response({"message": "Mot de passe mis à jour avec succès."})


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != "Admin":
            raise PermissionDenied("Seuls les administrateurs peuvent créer des comptes.")
        serializer.save()


class InviteSupervisorView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.role != "Admin":
            raise PermissionDenied("Seuls les administrateurs peuvent inviter des superviseurs.")
        
        serializer = InviteSupervisorSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            if User.objects.filter(email=email).exists():
                return Response({"error": "Un utilisateur avec cet email existe déjà."}, status=400)
            
            user = User.objects.create(
                email=email,
                role=User.Role.SUPERVISOR,
                is_active=False
            )
            user.set_unusable_password()
            user.save()
            
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Construct activation link
            activation_link = f"{settings.FRONTEND_URL}/activate-account?uid={uid}&token={token}"
            
            send_mail(
                'Activation de votre compte Superviseur',
                f'Bonjour,\n\nVeuillez cliquer sur le lien suivant pour activer votre compte et définir votre mot de passe :\n{activation_link}',
                'noreply@suiveo.com',
                [email],
                fail_silently=False,
            )
            
            return Response({"message": "Invitation envoyée avec succès."})
        return Response(serializer.errors, status=400)


class ActivateAccountView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        uidb64 = request.query_params.get('uid')
        token = request.query_params.get('token')
        
        if not uidb64 or not token:
            return Response({"error": "Paramètres manquants."}, status=400)
            
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Utilisateur invalide."}, status=400)
            
        # Check expiration (30 minutes)
        if not user.is_active and user.date_joined + timedelta(minutes=30) < timezone.now():
            user.delete()
            return Response({"error": "Le lien d'activation a expiré (délai de 30 minutes dépassé). Le compte a été supprimé."}, status=400)

        if default_token_generator.check_token(user, token):
            return Response({"email": user.email})
        else:
            return Response({"error": "Lien invalide ou expiré."}, status=400)

    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        password = request.data.get('password')
        
        if not all([uidb64, token, first_name, last_name, password]):
             return Response({"error": "Tous les champs sont requis."}, status=400)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user:
             # Check expiration (30 minutes)
            if not user.is_active and user.date_joined + timedelta(minutes=30) < timezone.now():
                user.delete()
                return Response({"error": "Le lien d'activation a expiré (délai de 30 minutes dépassé). Le compte a été supprimé."}, status=400)

        if user is not None and default_token_generator.check_token(user, token):
            serializer = CompleteRegistrationSerializer(user, data={
                'first_name': first_name,
                'last_name': last_name,
                'password': password
            })
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Compte activé avec succès."})
            return Response(serializer.errors, status=400)
        else:
            return Response({"error": "Lien d'activation invalide ou expiré."}, status=400)

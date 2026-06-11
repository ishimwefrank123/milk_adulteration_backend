from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegisterSerializer, UserLoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, UserSerializer, UserProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsAdmin, IsSeller, IsSupplier
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=201)
        return Response(serializer.errors, status=400)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data

            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Login successful",
                "user": {
                    "email": user.email,
                    "role": user.role
                },
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            })

        return Response(serializer.errors, status=400)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logout successful"}, status=205)

        except Exception:
            return Response({"error": "Invalid token"}, status=400)


# --- Example Endpoints for RBAC ---

class AdminOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        return Response({"message": f"Welcome Admin {request.user.email}!"})

class SellerOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsSeller]
    
    def get(self, request):
        return Response({"message": f"Welcome Seller {request.user.email}!"})

class SellerOrSupplierView(APIView):
    permission_classes = [IsAuthenticated, IsSeller | IsSupplier]
    
    def get(self, request):
        return Response({"message": f"Welcome {request.user.role} {request.user.email}!"})


# --- Password Reset Views ---

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()

            if user:
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = PasswordResetTokenGenerator().make_token(user)
                
                # Adjust this to point to your React/Vue frontend domain
                frontend_url = "http://localhost:3000/reset-password"
                reset_link = f"{frontend_url}?uid={uidb64}&token={token}"

                send_mail(
                    subject="Password Reset Request",
                    message=f"Please click the link below to reset your password:\n\n{reset_link}\n\nIf you did not request this, please ignore this email.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )

            return Response({"message": "If an account with this email exists, a password reset link has been sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- Admin User Management ---

class AdminUserViewSet(viewsets.ModelViewSet):
    """
    CRUD for users. Only accessible by admins.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        return UserSerializer

class UserProfileView(APIView):
    """
    Profile management for the currently logged-in user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
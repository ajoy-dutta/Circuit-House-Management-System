from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .models import HonourBoard
from .serializers import*
from rest_framework.permissions import BasePermission
User=get_user_model()
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'NDC'



# List and Create HonourBoard entries
class HonourBoardListCreateView(generics.ListCreateAPIView):
    queryset = HonourBoard.objects.all().order_by('-joining_date')
    serializer_class = HonourBoardSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]  # Require authentication for POST
        return [AllowAny()]  # Allow anyone to access GET
    

# Retrieve, Update, and Delete a specific HonourBoard entry
class HonourBoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [IsAuthenticated]
    queryset = HonourBoard.objects.all()
    serializer_class = HonourBoardSerializer
    
    
from rest_framework.generics import ListCreateAPIView
class UserRegistrationView(ListCreateAPIView):
    permission_classes=[AllowAny]
    queryset = User.objects.all()  # Replace `User` with your model name
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        print("Received data:", request.data)  # Log received data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"message": "Registration successful"},
            status=status.HTTP_201_CREATED
        )



class StaffListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    queryset = User.objects.all()
    serializer_class = StaffApproveSerializer

class StaffApproveView(generics.UpdateAPIView):
    permission_classes = [IsAdmin] 
    queryset = User.objects.all()
    serializer_class = StaffApproveSerializer

    def update(self, request, *args, **kwargs):
        user = self.get_object()  # Get the specific User instance
        user.is_approved = request.data.get('is_approved', user.is_approved)  # Update is_approved field
        user.save()  # Save the updated user instance
        return Response({"message": f"User {user.username} approval status updated successfully."}, status=status.HTTP_200_OK)
    def delete(self,request,*args,**kwargs):
        try:
            user=self.get_object()
            user.delete()
            return Response({"message": f"User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"error":"User doesn't exist"},status=status.HTTP_404_NOT_FOUND )

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request):
            serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                # Change password logic
                request.user.set_password(serializer.validated_data['new_password'])
                request.user.save()
                return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]  
    
    def get(self, request):
        user = request.user 
        print(user)
        serializer = UserProfileSerializer(user) 
        return Response(serializer.data)
    
class ForgotPasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        email = request.data.get("email")
        username = request.data.get("username")
        print(username)
        print(email)

        if not email:
            raise ValidationError("Email is required.")

        try:
            user = User.objects.get(username = username)
        except User.DoesNotExist:
            raise ValidationError("User with this email does not exist.")

        # Generate a token for the password reset
        token = default_token_generator.make_token(user)

        # Send email with password reset link
        reset_url = f"http://{get_current_site(request).domain}/reset-password-link/{urlsafe_base64_encode(str(user.pk).encode())}/{token}/"
        send_mail(
            subject="Password Reset Request",
            message=f"Click the link below to reset your password:\n{reset_url}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )

        return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)


class ContactView(APIView):
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve all contact submissions.
        """
        contacts = Contact.objects.all().order_by('-created_at')  # Fetch contacts, newest first
        serializer = ContactSerializer(contacts, many=True)  # Serialize the data
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def post(self, request, *args, **kwargs):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            contact = serializer.save()
            # Send an email
            try:
                # Custom reply to the user
                user_message = (
                        f"Hi {contact.name},\n\n"
                        "Thanks for reaching us. Please contact us at 02477762486 for more information.\n\n"
                        "We are happy to assist you!\n\n"
                        "Best regards,\n"
                        "Jashore Circuit House"
                    )

                send_mail(
                    subject="Thank You for Contacting Us!",
                    message=user_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[contact.email],  # Send to the user's email
                    fail_silently=False,
                )
                return Response({"message": "Contact form submitted and email sent successfully."}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": f"Contact form saved, but failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class StaffProfileView(generics.ListCreateAPIView):
    queryset = StaffProfile.objects.all()
    serializer_class = StaffProfileSerializer

class MediaAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
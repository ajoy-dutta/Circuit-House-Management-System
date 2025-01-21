from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('honour-board/', HonourBoardListCreateView.as_view(), name='honourboard-list-create'),
    # Retrieve, update, or delete a specific HonourBoard entry by ID
    path('honour-board/<int:pk>/', HonourBoardDetailView.as_view(), name='honourboard-detail'),
    path('register/',UserRegistrationView.as_view(),name='register'),
    path('approve_staff/', StaffListCreateView.as_view(), name='approve_staff'),
    path('approve_staff/<int:pk>/', StaffApproveView.as_view(), name='approve-staff'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('change-password/',PasswordChangeView.as_view(),name='change-password'),
    path('user/', UserProfileView.as_view(), name='user-profile'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password-link/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),name='reset-password-link'),
    path('password_reset_complete/',auth_views.PasswordResetCompleteView.as_view(),name='password-reset-complete'),
    path('contact/', ContactView.as_view(), name='contact'),
     path('staff-profile/', StaffProfileView.as_view(), name='staff-profile'),
        path('media/',MediaAPIView.as_view(),name='media'),

]


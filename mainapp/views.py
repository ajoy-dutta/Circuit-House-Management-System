from django.shortcuts import render
from rest_framework import generics,viewsets
from .models import *
from .serializers import *
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated
import datetime
from django.template.loader import render_to_string
from rest_framework import generics, status
from rest_framework.response import Response

class RoomListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    # def get_permissions(self):
    #     """Override to set different permissions for GET and POST methods"""
    #     if self.request.method == 'POST':
    #         return [IsAuthenticated()]  # Only authenticated users can create rooms
    #     return [AllowAny()]  # Allow everyone to view rooms

class RoomRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [IsAuthenticated]  # Only authenticated users can modify or view room details
    queryset = Room.objects.all()
    serializer_class = RoomSerializer



class PricingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access
    queryset = Pricing.objects.all()
    serializer_class = PriceSerializer
    
from django.core.mail import EmailMultiAlternatives 
class BookAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access
 
    # queryset = Guest.objects.filter()
    serializer_class = BookSerializer
    
    def get_queryset(self):
        return Guest.objects.exclude(
            id__in=CheckoutSummary.objects.values_list('guest_id', flat=True)
        )
    
    def perform_create(self, serializer):
        
        guest = serializer.save()
        check_in_date = serializer.validated_data.get('check_in_date')
        check_out_date = serializer.validated_data.get('check_out_date')

        # Adjust times
        if check_in_date:
            check_in_date = check_in_date.replace(hour=12, minute=0, second=0)
        if check_out_date:
            check_out_date = check_out_date.replace(hour=11, minute=59, second=0)

        # Save with updated times
        serializer.save(
            check_in_date=check_in_date,
            check_out_date=check_out_date
        )
        room = guest.room  
        room.availability_status = 'Booked'
        room.save()

        # Send a confirmation email
        self.send_confirmation_email(guest)
        

    def send_confirmation_email(self, guest):
        
        context = {
        'guest': guest,
        'current_time': datetime.datetime.now()
         }

        html_content = render_to_string(
            'Home/email_msg.html',
            context
        )
        subject = "Room Booking Confirmation"
        text_content = f"""
        Dear {guest.name},\n\n" "Your room booking at the Circuit House is confirmed. We look forward to hosting you.
        \n\n" "Best regards,\nCircuit House Management"
        {datetime.datetime.now()}
        """
        
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [guest.email]
        msg = EmailMultiAlternatives(subject, text_content, from_email,recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        
       
class BookRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Guest.objects.all()
    serializer_class = BookSerializer
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        previous_room = instance.room 

        response = super().update(request, *args, **kwargs)

        updated_guest = self.get_object()
        updated_room = updated_guest.room

        if previous_room and previous_room != updated_room:
            previous_room.availability_status = 'Vacant'
            previous_room.save()

        if updated_room:
            updated_room.availability_status = 'Booked'
            updated_room.save()

        return response
         
class CheckOutView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = CheckoutSummary.objects.all().order_by('-created_at')
    serializer_class = CheckoutSummarySerializer

    def create(self, request, *args, **kwargs):
        try:
            guest_id = request.data.get("guest_id")
            payment_status = request.data.get("paymentStatus")
            bill_by = request.data.get("username")

            print(guest_id, payment_status) 

            guest = Guest.objects.get(id=guest_id)

            # Create CheckoutSummary instance
            checkout_summary = CheckoutSummary.objects.create(
                guest=guest,
                payment_status=payment_status,
                bill_by = bill_by
            )

            self.perform_create(checkout_summary)

            serializer = self.get_serializer(checkout_summary)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Guest.DoesNotExist:
            return Response({"error": "Guest not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, checkout_summary):
        
        guest = checkout_summary.guest
        room = guest.room  
        room.availability_status = 'Needs Housekeeping'
        room.save()

        # Send a confirmation email
        self.send_confirmation_email(guest)
        

    def send_confirmation_email(self, guest):
        
        context = {
        'guest': guest,
        'current_time': datetime.datetime.now()
         }

        html_content = render_to_string(
            'Home/checkout_email.html',
            context
        )
        subject = "Checkout Confirmation"

        text_content = f"""
        Dear {guest.name},\n\n" "Your room booking at the Circuit House is confirmed. We look forward to hosting you.
        \n\n" "Best regards,\nCircuit House Management"
        {datetime.datetime.now()}
        """
        
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [guest.email]
        msg = EmailMultiAlternatives(subject, text_content, from_email,recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    

class FoodOrderAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    queryset = Food.objects.all()
    serializer_class = FoodSerializer

    def perform_create(self, serializer):
        serializer.save(date=date.today())  # Automatically set the current date

class OtherCostAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    queryset = OtherCost.objects.all()
    serializer_class = OtherCostSerializer
    # permission_classes = [IsAuthenticated]  # Require authentication for ordering food

    def perform_create(self, serializer):
        serializer.save(date=date.today())  # Automatically set the current date


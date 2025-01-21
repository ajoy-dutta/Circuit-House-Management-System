from .models import *
from rest_framework import serializers

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
        
    # def validate(self, data):
    #     if data['availability_status'] == 'Vacant' and not data.get('room_type'):
    #         raise serializers.ValidationError("Room type is required when status is 'Vacant'.")
    #     return data
    
    def perform_create(self, serializer):
        try:
            serializer.save()
        except serializers.ValidationError as e:
            print(e.detail)  # Logs validation errors
            raise

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing
        fields ='__all__'
    
    def validate_days(self,value):
        if self.initial_data.get('user_type') != 'Private Sector Employee' and not value:
            raise serializers.ValidationError("This field is required for the selected user type.")
        return value
    
class BookSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room.room_name', read_only=True)  # Get room_name from related Room model
    total_food_cost = serializers.SerializerMethodField()
    total_other_cost = serializers.SerializerMethodField()
    
    class Meta:
        model = Guest
        fields = '__all__'
        
        
    def get_total_food_cost(self, obj):
        return sum(food.price for food in Food.objects.filter(guest=obj))

    def get_total_other_cost(self, obj):
        return sum(cost.price for cost in OtherCost.objects.filter(guest=obj))
        
        
class CheckoutSummarySerializer(serializers.ModelSerializer):
    guest = BookSerializer()
    
    class Meta:
        model = CheckoutSummary
        fields = "__all__"

    


class FoodSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(write_only=True)  # Accept room_name as input
    guest_name = serializers.SerializerMethodField(read_only=True)  # Display guest_name in response
    room_display_name = serializers.SerializerMethodField(read_only=True)  # Show room_name in response

    class Meta:
        model = Food
        fields = ['date', 'food_menu', 'Order_time', 'price', 'room_name', 'room_display_name', 'guest_name']

    def get_room_display_name(self, obj):
        """Get the room name from the Room instance."""
        return obj.room.room_name if obj.room else None
    def get_guest_name(self,obj):
        return obj.guest.name if obj.guest else None

    def validate(self, data):
        room_name = data.get('room_name')  # Get the room name from input
        room = Room.objects.get(room_name=room_name) 
        # Ensure a guest is currently staying in the room
        try:
            guest = Guest.objects.get(room=room, check_out_date__gte=date.today())
        except Guest.DoesNotExist:
            raise serializers.ValidationError({'room_name': 'No guest is currently staying in this room.'})

        # Map room and guest to validated data
        data['room'] = room
        data['guest_name'] = guest
        return data

    def create(self, validated_data):
        room = validated_data['room']  # Room is now mapped from room_name
        guest_name = validated_data['guest_name']
        food_order = Food.objects.create(
            room=room,
            guest=guest_name,
            date=validated_data.get('date', date.today()),
            food_menu=validated_data['food_menu'],
            Order_time=validated_data['Order_time'],
            price=validated_data['price']
        )
        return food_order

class OtherCostSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(write_only=True)  # Accept room_name as input
    guest_name = serializers.SerializerMethodField(read_only=True)  # Display guest_name in response
    room_display_name = serializers.SerializerMethodField(read_only=True)  # Show room_name in response

    class Meta:
        model = OtherCost
        fields = ['date', 'item', 'price', 'room_name', 'room_display_name', 'guest_name']

    def get_room_display_name(self, obj):
        """Get the room name from the Room instance."""
        return obj.room.room_name if obj.room else None
    def get_guest_name(self,obj):
        return obj.guest.name if obj.guest else None

    def validate(self, data):
        room_name = data.get('room_name')  # Get the room name from input
        room = Room.objects.get(room_name=room_name) 
        # Ensure a guest is currently staying in the room
        try:
            guest = Guest.objects.get(room=room, check_out_date__gte=date.today())
        except Guest.DoesNotExist:
            raise serializers.ValidationError({'room_name': 'No guest is currently staying in this room.'})

        # Map room and guest to validated data
        data['room'] = room
        data['guest_name'] = guest
        return data

    def create(self, validated_data):
        room = validated_data['room']  # Room is now mapped from room_name
        guest_name = validated_data['guest_name']
        other_cost = OtherCost.objects.create(
            room=room,
            guest=guest_name,
            date=validated_data.get('date', date.today()),
            item=validated_data['item'],
            price=validated_data['price']
        )
        return other_cost


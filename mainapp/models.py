from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date,datetime


class Room(models.Model):
    STATUS_CHOICES = [
        ('Vacant', 'Vacant'),
        ('Booked', 'Booked'),
        ('Occupied', 'Occupied'),
        ('Needs Housekeeping', 'Needs Housekeeping'),
        ('Needs verify', 'Needs verify'),
        ('Locked', 'Locked'),
    ]
    
    ROOM_TYPE_CHOICES = [
        ('One King Size Bed', 'One King Size Bed'),
        ('Two King Size Beds', 'Two King Size Beds')
    ]
    
    Room_Category_Choices = [
        ('Regular', 'Regular'),
        ('VIP', 'VIP'),
        ('VVIP', 'VVIP'),
    ]
    
    Building_Choices = [
        ('New Building', 'New Building'),
        ('Old Building', 'Old Building'),
    ]
    
    Floor_Choices = [
        ('Ground Floor', 'Ground Floor'),
        ('First Floor', 'First Floor'),
        ('Second Floor', 'Second Floor'),
        
    ]
    
    room_name = models.CharField(max_length=50)
    room_type = models.CharField(max_length=50, choices=ROOM_TYPE_CHOICES) 
    room_category = models.CharField(max_length=50, choices=Room_Category_Choices, default='Regular')
    availability_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Vacant')
    building = models.CharField(max_length=50, choices=Building_Choices, default='New Building') 
    floor = models.CharField(max_length=50, choices=Floor_Choices, default='First Floor')  
    
    def __str__(self):
        return self.room_name

     
# Pricing Table
class Pricing(models.Model):
    USER_TYPE_CHOICES = [
        ('Government Official', 'Govt. Official(Existing/Retd.)'),
        # ('Reference', 'Reference'),
        ('Autonomous','Autonomous/Statutary Organization'),
        ('Private Sector Employee', 'Private Sector Employee/Others'),
    ]
    
    ROOM_TYPE_CHOICES = [
        ('One King Size Bed', 'One King Size Bed'),
        ('Two King Size Beds', 'Two King Size Beds')
    ]
    
    user_type = models.CharField(max_length=30, choices=USER_TYPE_CHOICES)
    room_type = models.CharField(max_length=50, choices=ROOM_TYPE_CHOICES)
    days_range = models.CharField(max_length=10, blank=True, null=True, help_text="e.g., 1-3, 4-7, or 7+")
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ('user_type', 'room_type', 'days_range')
    
    def __str__(self):
        return f"{self.user_type} , {self.room_type} , {self.days_range}: {self.price_per_day}"


# Guest Table
class Guest(models.Model):
    USER_TYPE_CHOICES = [
        ('Government Official', 'Govt. Official(Existing/Retd.)'),
        # ('Reference', 'Reference'),
        ('Autonomous','Autonomous/Statutary Organization'),
        ('Private Sector Employee', 'Private Sector Employee/Others'),

    ]
    
    name = models.CharField(max_length=100)
    office=models.CharField(max_length=100, blank=True, null=True)
    designation=models.CharField(max_length=50, blank=True, null=True)
    user_type = models.CharField(max_length=30, choices=USER_TYPE_CHOICES, default='Government Official')
    nid = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=50, null=True, blank =True)
    phone = models.CharField(max_length=20, blank=True, null= True)
    check_in_date = models.DateTimeField(blank=True, null=True)
    check_out_date = models.DateTimeField(blank=True, null=True)
    total_person = models.IntegerField(blank=True, null=True)
    motive_of_visiting = models.TextField(blank=True, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    total_days = models.IntegerField(editable=False, null=True, blank=True)
    total_rental_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)
    comment = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        
        # Step 1: Calculate total days
        if self.check_in_date and self.check_out_date:
            self.total_days = (self.check_out_date - self.check_in_date).days+1

        # Step 2: Calculate rental price
        if self.room and self.user_type:
            room_type = self.room.room_type
            user_type = self.user_type

            # Fetch matching pricing entries ordered by 'days_range'
            pricing_entries = Pricing.objects.filter(
                user_type=user_type, room_type=room_type
            ).order_by('days_range')

            total_cost = 0
            remaining_days = self.total_days

            # Iterate over the pricing entries
            for pricing in pricing_entries:
                days_range = pricing.days_range

                price_per_day = pricing.price_per_day
                
                # Skip entries with a None value for days_range
                if user_type == 'Private Sector Employee':
                    total_cost += price_per_day * remaining_days
                    break

                # Handle ranged pricing: '1-3', '4-7', '7+'
                if '-' in days_range:  # Example: '1-3'
                    min_days, max_days = map(int, days_range.split('-'))
                    days_in_range = min(max_days - min_days + 1, remaining_days)
                else:  # Open-ended range like '7+'
                    min_days = int(days_range.rstrip('+'))
                    days_in_range = remaining_days

                # Calculate the cost for this range
                if days_in_range > 0:
                    chargeable_days = min(days_in_range, remaining_days)
                    total_cost += price_per_day * chargeable_days
                    remaining_days -= chargeable_days

                # Stop if all days are calculated
                if remaining_days <= 0:
                    break

            # Assign the calculated total rental price
            self.total_rental_price = total_cost
            print(self.total_rental_price)
            
        super(Guest, self).save(*args, **kwargs)
        

# Food Table
class Food(models.Model):
    TIME_CHOICES = [
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
    ]
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    room=models.ForeignKey(Room,on_delete=models.CASCADE)
    date = models.DateField()
    food_menu = models.TextField()
    Order_time = models.CharField(max_length=20, choices=TIME_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    

class OtherCost(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE,null=True,blank=True)
    room=models.ForeignKey(Room,on_delete=models.CASCADE)
    date = models.DateField()
    item = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.item} - {self.price} ({self.date})"


class CheckoutSummary(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    total_rental_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    total_food_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    total_other_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    payment_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    bill_by = models.CharField(max_length=100, blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate total costs
        self.total_rental_cost = self.guest.total_rental_price
        self.total_food_cost = sum([food.price for food in Food.objects.filter(guest=self.guest)])  # Assuming the food cost is stored in the Food model
        self.total_other_cost = sum([cost.price for cost in OtherCost.objects.filter(guest=self.guest)])
        if not self.payment_id:
                current_date = datetime.now().strftime("%d%m%y")
                last_id = CheckoutSummary.objects.latest('id').id if CheckoutSummary.objects.exists() else 0
                unique_id = f"{current_date}.{last_id + 1}"
                self.payment_id = unique_id
                print(f"Generated payment_id: {self.payment_id}")
        # Calculate the grand total including the other cost
        self.grand_total = self.total_rental_cost + self.total_food_cost + self.total_other_cost
        super(CheckoutSummary, self).save(*args, **kwargs)



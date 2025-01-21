from django.contrib import admin
from .models import*
# Register your models here.

admin.site.register(Room)
admin.site.register(Pricing)
admin.site.register(Food)
admin.site.register(OtherCost)
admin.site.register(CheckoutSummary)

# class GuestAdmin(admin.ModelAdmin):
#     readonly_fields = ('total_days', 'total_rental_price')  
#     list_display = ('name', 'total_days', 'total_rental_price')  

admin.site.register(Guest)

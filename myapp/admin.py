from django.contrib import admin
from .models import *

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('uuid','name', 'status', 'from_place', 'to_place', 'created_at', 'payment_status')
    search_fields = ['name', 'first_name', 'email']
    list_filter = ('payment_status', 'created_at',)

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('user','uuid')
    search_fields = ['user','uuid']
    list_filter = ('user','uuid')

admin.site.register(Reservation, ReservationAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(VehicleType)
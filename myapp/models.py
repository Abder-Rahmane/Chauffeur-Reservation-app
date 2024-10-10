# Create your models here.
from django.db import models
import uuid
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

from datetime import time

class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True)
    url_website = models.CharField(max_length=200, blank=True, null=True)
    online_payment = models.BooleanField(default=True)
    cash_payment = models.BooleanField(default=True)
    stripe_public_key = models.CharField(max_length=200, blank=True, null=True)
    stripe_secret_key = models.CharField(max_length=200, blank=True, null=True)
    google_maps_key = models.CharField(max_length=200, blank=True, null=True)
    notifications_active = models.BooleanField(default=False)


    online_payment_start_time = models.TimeField(default=time(1, 0))  # 01:00
    online_payment_end_time = models.TimeField(default=time(6, 0))    # 06:00

class VehicleType(models.Model):
    VEHICLE_CHOICES = [
        ("economique", "Économique"),
        ("berline", "Berline"),
        ("premium", "Premium"),
        ("van", "Van"),
        ("minibus", "Minibus"),
    ]

    name = models.CharField(max_length=50, choices=VEHICLE_CHOICES)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="vehicle_types")
    active = models.BooleanField(default=True)
    cost_per_km = models.DecimalField(max_digits=5, decimal_places=2, default=1.5)
    cost_per_minute = models.DecimalField(max_digits=5, decimal_places=2, default=0.20)
    minimum_cost = models.DecimalField(max_digits=5, decimal_places=2,default=20)
    night_fare_increase = models.IntegerField(default=10)  
    night_start_time = models.TimeField(default=time(0, 0))  # 00:00
    night_end_time = models.TimeField(default=time(5, 0)) 
    orly_fare = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=70)
    cdg_fare = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=50)
    seats = models.IntegerField(default=4)
    baggage = models.IntegerField(default=2)

@receiver(post_save, sender=CustomUser)
def create_vehicle_types(sender, instance, created, **kwargs):
    if created:
        for vehicle_type in VehicleType.VEHICLE_CHOICES:
            VehicleType.objects.create(name=vehicle_type[0], user=instance)

class Reservation(models.Model):
    CustomUser = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, null=True)
    PICKUP = 'PU'
    DESTINATION = 'DE'
    ADDRESS_TYPES = [
        (PICKUP, 'Pickup'),
        (DESTINATION, 'Destination'),
    ]
    
    # Address
    from_place = models.CharField(max_length=255, verbose_name="Lieu de prise en charge")
    to_place = models.CharField(max_length=255, verbose_name="Destination")
    step_place = models.CharField(max_length=255, verbose_name="Etape" , null=True, blank=True)

    #Go and back
    is_round_trip = models.BooleanField(default=False, verbose_name="Aller-retour", null=True, blank=True)
    step_on_return = models.BooleanField(default=False, verbose_name="Avec étape au retour", null=True , blank=True)

    # Date and time
    reservation_date = models.DateField(verbose_name="Date de réservation", null=True)
    reservation_time = models.TimeField(verbose_name="Heure de réservation", null=True)

    # Vehicle
    vehicle_type = models.CharField(max_length=20, choices=[
        ('economique', 'Economique'),
        ('berline', 'Berline'),
        ("premium", "Premium"),
        ('van', 'Van'),
        ("minibus", "Minibus"),
    ], verbose_name="Type de véhicule")
    
    # User info
    name = models.CharField(max_length=255, verbose_name="Nom")
    first_name = models.CharField(max_length=255, verbose_name="Prénom")
    phone_number = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    email = models.EmailField(verbose_name="Email")

    # Additional info
    passengers = models.IntegerField(verbose_name="Nombre de passagers")
    vol = models.CharField(max_length=255, verbose_name="Numéro de réservation", null=True, blank=True,)
    assistance = models.CharField(max_length=255, verbose_name="Assistance", null=True, blank=True,)
    special_requests = models.TextField(null=True, blank=True, verbose_name="Demandes spéciales")
    
    # Payment
    payment_method = models.CharField(max_length=20, choices=[
        ('cash', 'Sur place'),
        ('online', 'En ligne')
    ], verbose_name="Méthode de paiement")
    payment_status = models.BooleanField(default=False, verbose_name="Statut du paiement")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix", null=True)
    stripe_session_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="Stripe Session ID")
    reservation_id = models.CharField(max_length=5, unique=True, verbose_name="ID de Réservation", null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    # Status
    IN_PROGRESS = 'IP'
    COMPLETED = 'CP'
    STATUS_CHOICES = [
        (IN_PROGRESS, 'En cours'),
        (COMPLETED, 'Complété'),
    ]
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=IN_PROGRESS, verbose_name="Statut")

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"

    def __str__(self):
        return f"{self.name} {self.first_name} - {self.from_place} à {self.to_place}"

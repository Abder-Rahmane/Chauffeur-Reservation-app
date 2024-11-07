from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'from_place', 'to_place', 'vehicle_type',
            'name', 'first_name', 'phone_number', 'email',
            'passengers', 'special_requests',
            'payment_method', 'stripe_session_id',
            'reservation_date', 'reservation_time', 'price',
            'vol', 'assistance', 'step_place', 'is_round_trip', 'step_on_return'
        ]

import uuid
import stripe
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from .forms import ReservationForm
from .models import *
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib import messages
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import transaction

import logging

logger = logging.getLogger(__name__)


# stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your views here.


def convert_time_to_24h(time_obj):
    return time_obj.strftime("%H:%M")


def index(request, uuid):
    custom_user = get_object_or_404(CustomUser, uuid=uuid)

    vehicle_types = VehicleType.objects.filter(user=custom_user, active=True).values()
    
    vehicle_types_list = list(vehicle_types)
    
    for vehicle_type in vehicle_types_list:
        vehicle_type['night_start_time'] = convert_time_to_24h(vehicle_type['night_start_time'])
        vehicle_type['night_end_time'] = convert_time_to_24h(vehicle_type['night_end_time'])
    
    now_time = datetime.now().time()
    if custom_user.online_payment_start_time < custom_user.online_payment_end_time:
        show_online_payment = custom_user.online_payment and (custom_user.online_payment_start_time <= now_time <= custom_user.online_payment_end_time)
    else:
        show_online_payment = custom_user.online_payment and (custom_user.online_payment_start_time <= now_time or now_time <= custom_user.online_payment_end_time)
    
    context = {
        'uuid': uuid,
        'user_uuid': uuid,
        'stripe_public_key': custom_user.stripe_public_key,
        'google_maps_key': custom_user.google_maps_key, 
        'vehicle_types': vehicle_types_list, 
        'show_online_payment': show_online_payment,
        'show_cash_payment': custom_user.cash_payment,  
    }
    return render(request, 'form.html', context)

@login_required(login_url='login')
def courses(request):
    if request.user.is_authenticated:
        custom_user = CustomUser.objects.get(user=request.user)
        
        
        user_reservations = Reservation.objects.filter(CustomUser=custom_user, status=Reservation.IN_PROGRESS).order_by('-created_at')

        

        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)

        for reservation in user_reservations:
            reservation_date = reservation.reservation_date
            if reservation_date == today:
                reservation.display_date = "Aujourd'hui"
            elif reservation_date == tomorrow:
                reservation.display_date = "Demain"
            else:
                reservation.display_date = reservation_date.strftime("%d/%m/%Y")


        context = {
            'user_reservations': user_reservations,
            'custom_user' : custom_user
        }
        return render(request, 'dashboard/courses.html', context)



@login_required(login_url='login')
def setting(request):
    vehicle_types = ["Économique", "Berline", "Premium", "Minibus", "Van"]
    with transaction.atomic():
         user_settings = CustomUser.objects.select_for_update().get_or_create(user=request.user)[0]
         custom_user = CustomUser.objects.get(user=request.user)
     
         if request.method == 'POST':
             form_type = request.POST.get('form_type')
             if form_type == 'payment_method':
                 user_settings.online_payment = 'online_payment' in request.POST
                 user_settings.cash_payment = 'cash_payment' in request.POST
                 
                 online_payment_start_time = request.POST.get('online_payment_start_time')
                 online_payment_end_time = request.POST.get('online_payment_end_time')
                 
                 if online_payment_start_time and online_payment_end_time:  
                     user_settings.online_payment_start_time = online_payment_start_time
                     user_settings.online_payment_end_time = online_payment_end_time
             
                 
                 user_settings.save()
     
     
             elif form_type == 'redirection_url':
                 user_settings.url_website = request.POST.get('url_website')
                 user_settings.save()
                 messages.success(request, 'URL de redirection mise à jour avec succès !')
     
             elif form_type == 'vehicle_type':
                  for vehicle_type in user_settings.vehicle_types.all():
                      vehicle_type_form_prefix = vehicle_type.name  
          
                      try:
                          vehicle_type.active = f"{vehicle_type_form_prefix}_active" in request.POST
                          vehicle_type.cost_per_km = Decimal(request.POST.get(f"{vehicle_type_form_prefix}_cost_per_km", "0"))
                          vehicle_type.cost_per_minute = Decimal(request.POST.get(f"{vehicle_type_form_prefix}_cost_per_minute", "0"))
                          vehicle_type.minimum_cost = Decimal(request.POST.get(f"{vehicle_type_form_prefix}_minimum_cost", "0"))
                          vehicle_type.night_fare_increase = Decimal(request.POST.get(f"{vehicle_type_form_prefix}_night_fare_increase", "0"))
                          vehicle_type.night_start_time = request.POST.get(f"{vehicle_type_form_prefix}_night_start_time")
                          vehicle_type.night_end_time = request.POST.get(f"{vehicle_type_form_prefix}_night_end_time")
                          vehicle_type.orly_fare = Decimal(request.POST.get(f"{vehicle_type_form_prefix}_orly_fare", "0"))
                          vehicle_type.cdg_fare = Decimal(request.POST.get(f"{vehicle_type_form_prefix}_cdg_fare", "0"))
          
                          if not(vehicle_type.night_start_time and vehicle_type.night_end_time):
                              raise ValueError("Invalid time values")
          
                          vehicle_type.save()
                          
                      except InvalidOperation:
                          continue  
                      except ValueError as e:
                          continue
          
                  messages.success(request, 'Paramètres mis à jour avec succès !')
                  return redirect('setting')
     
         context = {
             'custom_user': custom_user,
             'vehicle_types': vehicle_types,
             'user_settings': user_settings,
             'vehicle_types': user_settings.vehicle_types.all(),
         }
    return render(request, 'dashboard/setting.html', context)


@login_required(login_url='login')
def other_settings(request):
    custom_user = CustomUser.objects.get(user=request.user)
    with transaction.atomic():
        user_settings = CustomUser.objects.select_for_update().get_or_create(user=request.user)[0]
        
        if request.method == 'POST':
            form_type = request.POST.get('form_type')

            if form_type == 'api_keys':
                user_settings.stripe_public_key = request.POST.get('stripe_public_key')
                user_settings.stripe_secret_key = request.POST.get('stripe_secret_key')
                user_settings.google_maps_key = request.POST.get('google_maps_key')

            elif form_type == 'notifications':
                user_settings.notifications_active = 'notifications_active' in request.POST

            user_settings.save()
            messages.success(request, 'Paramètres mis à jour avec succès !')
            return redirect('other_settings')

    context = {
        'user_settings': user_settings,
        'custom_user' : custom_user
               }
    return render(request, 'dashboard/other_settings.html', context)

class MakeReservation(View):
    def post(self, request, user_uuid, *args, **kwargs):

        try:
            custom_user = CustomUser.objects.get(uuid=user_uuid)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        is_round_trip = request.POST.get('is_round_trip', 'No') == 'Yes'
        step_on_return = request.POST.get('step_on_return', 'No') == 'Yes'

        form = ReservationForm(request.POST)
        print(request.POST)
        if form.is_valid():
            reservation_id = str(uuid.uuid4())[:5]
            reservation = form.save(commit=False)
            
            reservation.CustomUser = custom_user  
            reservation.reservation_id = reservation_id
            
            reservation.is_round_trip = is_round_trip
            reservation.step_on_return = step_on_return
            
            reservation.save()

            reservation_data = {
                'reservation_id': reservation.reservation_id,
                'name': reservation.name,
                'first_name': reservation.first_name,
                'phone_number': reservation.phone_number,
                'email': reservation.email,
                'from_place': reservation.from_place,
                'to_place': reservation.to_place,
                'step_place': reservation.step_place,
                'is_round_trip': reservation.is_round_trip,
                'step_on_return': reservation.step_on_return,
                'vehicle_type': reservation.vehicle_type,
                'vol': reservation.vol,
                'assistance': reservation.assistance,
                'passengers': reservation.passengers,
                'special_requests': reservation.special_requests,
                'payment_method': reservation.payment_method,
                'price': reservation.price,
                'reservation_date': reservation.reservation_date.strftime('%d %B %Y'),
                'reservation_time': reservation.reservation_time.strftime('%H:%M'),
            }

            if reservation.payment_method == 'online':
                try:
                    stripe.api_key = custom_user.stripe_secret_key
                    checkout_session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=[{
                            'price_data': {
                                'currency': 'eur',
                                'product_data': {
                                    'name': 'Réservation',
                                },
                                'unit_amount': int(reservation.price * 100),
                            },
                            'quantity': 1,
                        }],
                        mode='payment',
                        invoice_creation={
                             "enabled": True 
                         },
                        success_url=request.build_absolute_uri(f'/form_success/{reservation.uuid}/'),
                        cancel_url=request.build_absolute_uri(f'/form_error/{reservation.uuid}/'),
                    )
                    reservation.stripe_session_id = checkout_session['id']
                    reservation.save()

                    return JsonResponse({
                        'success': True,
                        'stripe_session_id': checkout_session['id'],
                        'reservation': reservation_data,
                    }, status=200)
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=400)

            return JsonResponse({
                'success': True,
                'reservation': reservation_data,
                'uuid': str(reservation.uuid)  
            }, status=200)
        else:
            return JsonResponse({'error': form.errors}, status=400)
        
def form_error(request, uuid):
    reservation = get_object_or_404(Reservation, uuid=uuid)

    if reservation.payment_status or reservation.payment_method == 'cash':
        return redirect('form_success', reservation_uuid=uuid)
    
    stripe_public_key = reservation.CustomUser.stripe_public_key
    
    if request.method == 'POST':
        try:
            reservation.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    context = {
        'reservation': reservation,
        'stripe_public_key': stripe_public_key,
    }

    return render(request, 'form_error.html', context)


def form_success(request, reservation_uuid):
    reservation = get_object_or_404(Reservation, uuid=reservation_uuid)
    stripe_session_url = ""
    invoice_url = ""
    if reservation.payment_method == "online" and reservation.payment_status==False:
        return redirect('form_error', uuid=reservation_uuid)

    custom_user = reservation.CustomUser
    stripe.api_key = custom_user.stripe_secret_key

    if reservation.payment_method == "online" and reservation.stripe_session_id:
        try:
            session = stripe.checkout.Session.retrieve(reservation.stripe_session_id)
            stripe_session_url = session.url

            if session.get('invoice'):
                invoice = stripe.Invoice.retrieve(session['invoice'])
                invoice_url = invoice['hosted_invoice_url']
            
            print("Stripe Session URL: ", stripe_session_url)
            print("Stripe Invoice URL: ", invoice_url)
        except stripe.error.StripeError as e:
            print(f"Stripe error: {str(e)}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
        
    uuid = reservation.CustomUser.uuid

    context = {
        'reservation': reservation,
        'stripe_session_url': stripe_session_url,
        'invoice_url': invoice_url,
        'uuid': uuid
    }
    return render(request, 'form_success.html', context)


@csrf_exempt
def stripe_webhook(request):
    endpoint_stripe = 'whsec_3e75aa3cdfb827c84115281ab3659fbc3f5189a962badfa826807f0c39dbcb82'
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_stripe
        )
    except ValueError as e:
        print("Invalid payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print("Invalid signature")
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        handle_payment_success(session)

    return HttpResponse(status=200)

def handle_payment_success(session):
    reservation = Reservation.objects.get(stripe_session_id=session.id)
    reservation.payment_status = True
    reservation.save()




class RetryPayment(View):
    def post(self, request, reservation_uuid, *args, **kwargs):
        reservation = get_object_or_404(Reservation, uuid=reservation_uuid)
        
        if 'payment_method' in request.POST and request.POST['payment_method'] == 'cash':
            reservation.payment_method = 'cash'
            reservation.save()
            
            redirect_url = reverse('form_success', kwargs={'reservation_uuid': reservation.uuid})
            return JsonResponse({
                'success': True,
                'redirect_url': request.build_absolute_uri(redirect_url)
            }, status=200)
        

        elif reservation.payment_method == 'online':
            try:
                stripe_secret_key = reservation.CustomUser.stripe_secret_key
                stripe.api_key = stripe_secret_key
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'eur',
                            'product_data': {
                                'name': 'Réservation',
                            },
                            'unit_amount': int(reservation.price * 100),
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    invoice_creation={
                             "enabled": True 
                         },
                    success_url=request.build_absolute_uri(f'/form_success/{reservation.uuid}/'),
                    cancel_url=request.build_absolute_uri(f'/form_error/{reservation.uuid}/'),
                )
                reservation.stripe_session_id = checkout_session['id']
                reservation.save()

                return JsonResponse({
                    'success': True,
                    'stripe_session_id': checkout_session['id'],
                }, status=200)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        else:
            return JsonResponse({'error': "Invalid payment method"}, status=400)
        



def login_view(request):
    if request.user.is_authenticated:
        return redirect('courses')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('courses')
        else:
            messages.error(request, 'Erreur d\'identification')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('/login')  


def custom_404_view(request, exception):
    return render(request, '404.html', {}, status=404)




@login_required(login_url='login')
def historique(request):
    if request.user.is_authenticated:
        custom_user = CustomUser.objects.get(user=request.user)
        
        user_reservations = Reservation.objects.filter(CustomUser=custom_user, status=Reservation.COMPLETED).order_by('-created_at')
        

        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)

        for reservation in user_reservations:
            reservation_date = reservation.reservation_date
            if reservation_date == today:
                reservation.display_date = "Aujourd'hui"
            elif reservation_date == tomorrow:
                reservation.display_date = "Demain"
            else:
                reservation.display_date = reservation_date.strftime("%d/%m/%Y")


        context = {
            'user_reservations': user_reservations,
        }
        return render(request, 'dashboard/historique.html', context)
    


@login_required(login_url='login')
def update_reservation(request):
    if request.method == "POST":
        reservation_id = request.POST.get('reservation_id')
        try:
            reservation = Reservation.objects.get(id=reservation_id)
            reservation.status = Reservation.COMPLETED
            reservation.save()
            messages.success(request, 'Reservation marked as completed.')
            return redirect('courses')  
        except Reservation.DoesNotExist:
            messages.error(request, 'Reservation not found.')
            return redirect('courses') 
    return redirect('courses')  


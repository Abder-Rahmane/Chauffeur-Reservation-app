"""
URL configuration for reservch project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views
from myapp.views import MakeReservation,RetryPayment
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('<uuid:uuid>', views.index, name="index"),
    path('<uuid:user_uuid>/make_reservation/', csrf_exempt(MakeReservation.as_view()), name='make_reservation'),
    path('form_error/<uuid:uuid>/', views.form_error, name='form_error'),
    path('form_success/<uuid:reservation_uuid>/', views.form_success, name='form_success'),
    path('stripe_webhook/', views.stripe_webhook, name='stripe-webhook'),
    path('retry_payment/<uuid:reservation_uuid>/', RetryPayment.as_view(), name='retry_payment'),
    path('dashboard/courses/', views.courses, name='courses'),
    path('dashboard/courses/historique', views.historique, name='historique'),
    path('dashboard/setting/', views.setting, name='setting'),
    path('dashboard/other_settings/', views.other_settings, name='other_settings'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/update-reservation/', views.update_reservation, name='update_reservation'),
    # path('update_vehicle_type/<int:pk>/', views.update_vehicle_type, name='update_vehicle_type'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

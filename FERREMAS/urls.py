from django.contrib import admin
from django.urls import path, include
from app.views import error_404_view  #  importante manejo error 404

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    # RUTA PARA RECIBIR IPN DE PayPal
    path('paypal/', include('paypal.standard.ipn.urls')),
    
]

# 👇 importante: debe ir FUERA del urlpatterns
handler404 = error_404_view

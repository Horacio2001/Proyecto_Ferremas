# app/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import Cliente

class ClienteCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    email = forms.EmailField(required=True, label='Correo electrónico')
    suscribir_noticias = forms.BooleanField(required=False, label='Suscribirme al newsletter')
    telefono = forms.CharField(max_length=20, required=False, label='Teléfono')
    direccion = forms.CharField(max_length=255, required=False, label='Dirección')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        # Creamos el User
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Luego, creamos el perfil Cliente
            Cliente.objects.create(
                user=user,
                suscribir_noticias=self.cleaned_data['suscribir_noticias'],
                telefono=self.cleaned_data['telefono'],
                direccion=self.cleaned_data['direccion']
            )
        return user

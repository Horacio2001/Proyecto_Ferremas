from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.templatetags.static import static






# LOGIN
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, "Credenciales incorrectas.")
    return render(request, 'app/registration/login.html')


#REGISTRAR UN NUEVO CLIENTE
class ClienteCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    suscribir_noticias = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'suscribir_noticias')

def registro_cliente(request):
    if request.method == 'POST':
        form = ClienteCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Aquí podrías guardar el valor de suscribir_noticias en un perfil
            return redirect('login')
    else:
        form = ClienteCreationForm()
    return render(request, 'app/registration/registro_cliente.html', {'form': form})



# Página principal
def index(request):
    return render(request, 'app/index.html')

# CLIENTE

def detalle_producto(request):
    return render(request, 'app/cliente/detalle_producto.html')



def catalogo_cliente(request):
    return render(request, 'app/cliente/catalogo.html')

def carrito_cliente(request):
    return render(request, 'app/cliente/carrito.html')



def checkout(request):
    return render(request, 'app/cliente/checkout.html')

def pago_cliente(request):
    return render(request, 'app/cliente/pago.html')

# VENDEDOR
def pedidos_vendedor(request):
    return render(request, 'app/vendedor/pedidos_vendedor.html')

def aprobar_pedido(request):
    return render(request, 'app/vendedor/aprobar_pedido.html')

def orden_pedido(request):
    return render(request, 'app/vendedor/orden_bodega.html')

# BODEGUERO
def ordenes_bodeguero(request):
    return render(request, 'app/bodeguero/ordenes_bodeguero.html')

def preparar_pedido(request):
    return render(request, 'app/bodeguero/preparar_pedido.html')

# CONTADOR
def pagos_contador(request):
    return render(request, 'app/contador/pagos_contador.html')

def confirmar_pago(request):
    return render(request, 'app/contador/confirmar_pago.html')

def registro_entrega(request):
    return render(request, 'app/contador/registro_entrega.html')

# ADMIN
def dashboard_admin(request):


    # Ejemplo de datos para el gráfico
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
    pedidos_por_mes = [45, 60, 30, 75, 50, 90]

    context = {
        
        'meses': meses,
        'pedidos_por_mes': pedidos_por_mes,
    }

    return render(request, 'app/admin/dashboard_admin.html', context)

def usuarios_admin(request):
    return render(request, 'app/admin/usuarios_admin.html')

def pedidos_admin(request):
    return render(request, 'app/admin/pedidos_admin.html')

def inventario_admin(request):
    return render(request, 'app/admin/inventario_admin.html')

#INFORMACION

def contactanos(request):
    return render(request, 'app/informacion/contactanos.html')

def somos(request):
    return render(request, 'app/informacion/somos.html')

def terminos(request):
    return render(request, 'app/informacion/terminos.html')




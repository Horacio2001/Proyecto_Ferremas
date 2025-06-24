
import os
import requests # type: ignore
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login ,logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django.contrib.auth.models import User
from django.templatetags.static import static
from .decorators import rol_requerido, cliente_requerido
from .forms import ClienteCreationForm
from .models import Producto, Rol, Empleado, EstadoPedido, TipoPago, Pago, Pedido, DetallePedido, Cliente
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm  # type: ignore
from weasyprint import HTML
from django.template.loader import render_to_string
from django.http import HttpResponse
import tempfile
from django.core.files.storage import default_storage
from django.urls import reverse
from django.urls import reverse
from .models import Pedido, EstadoPedido, Pago, PedidoHistorial
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib import messages


def cliente_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        usuario = request.session.get('usuario')
        if not usuario or usuario.get('rol') != 'cliente':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def vendedor_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        usuario = request.session.get('usuario')
        if not usuario or usuario.get('rol') != 'vendedor':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def bodeguero_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        usuario = request.session.get('usuario')
        if not usuario or usuario.get('rol') != 'bodeguero':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def contador_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        usuario = request.session.get('usuario')
        if not usuario or usuario.get('rol') != 'contador':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def administrador_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        usuario = request.session.get('usuario')
        if not usuario or usuario.get('rol') != 'administrador':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

#-------------------------------------------



def redirect_por_rol(user):
    rol = user.get("rol", "").lower()

    if rol == "admin":
        if not user.get("cambio_contrasena", True):
            return 'cambiar_contrasena'
        return 'pedidos_admin'
    elif rol == "contador":
        return 'pagos_contador'
    elif rol == "bodeguero":
        return 'ordenes_bodeguero'
    elif rol == "vendedor":
        return 'pedidos_vendedor'
    elif rol == "cliente":
        return 'catalogo_cliente'
    else:
        return 'index'
    


def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasena = request.POST.get('contrasena')
        payload = {'usuario': usuario, 'contrasena': contrasena}

        # 1) Intentar login como CLIENTE
        try:
            response = requests.post('http://127.0.0.1:8000/cliente/login', params=payload)
            if response.status_code == 200:
                data = response.json()
                # data debería incluir: {"id_cliente": 82, "rol": "cliente", "nombre": "Charles", ...}
                # Guardamos solo lo que necesitamos en sesión:
                request.session['usuario'] = {
                    'id_cliente': data['id_cliente'],
                    'rol': data['rol'],        # “cliente”
                    'nombre': data.get('nombre', ''),
                }
                messages.success(request, f"¡Bienvenido {data.get('nombre','')}!")
                return redirect(redirect_por_rol(request.session['usuario']))

        except requests.exceptions.RequestException:
            # Si falla el POST al endpoint /cliente/login
            messages.error(request, "Error al conectar con el servidor de autenticación.")
            return render(request, 'app/registration/login.html')

        # 2) Si no es cliente, intentamos login como EMPLEADO
        try:
            response = requests.post('http://127.0.0.1:8000/empleado/login', params=payload)
            if response.status_code == 200:
                data = response.json()
                # data incluye: {"id_empleado": 3, "rol": "vendedor", "nombre": "Julianno", ...}
                request.session['usuario'] = {
                    'id_empleado': data['id_empleado'],
                    'rol': data['rol'],        # “vendedor”, “bodeguero”, “contador”, etc.
                    'nombre': data.get('nombre', ''),
                }
                messages.success(request, f"¡Bienvenido {data.get('nombre','')}!")
                return redirect(redirect_por_rol(request.session['usuario']))
        except requests.exceptions.RequestException:
            messages.error(request, "Error al conectar con el servidor de autenticación.")
            return render(request, 'app/registration/login.html')

        # 3) Si ninguno devolvió 200#
        messages.error(request, "Usuario o contraseña incorrectos.")
    return render(request, 'app/registration/login.html')



def logout_view(request):
    request.session.flush()  # Borra toda la sesión
    return redirect('login')

# REGISTRO CLIENTE
def registro_cliente(request):
    pass
    if request.user.is_authenticated:
        return redirect(redirect_por_rol(request.user))

    if request.method == 'POST':
        form = ClienteCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = ClienteCreationForm()
    return render(request, 'app/registration/registro_cliente.html', {'form': form})

#@login_required
def cambiar_contrasena(request):
    # Sólo empleados que no han cambiado contraseña deben entrar aquí
    if not hasattr(request.user, 'perfil_empleado') or request.user.perfil_empleado.cambio_contrasena:
        return redirect(redirect_por_rol(request.user))

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            empleado = request.user.perfil_empleado
            empleado.cambio_contrasena = True
            empleado.save()
            return redirect(redirect_por_rol(user))
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'app/registration/cambiar_contrasena.html', {'form': form})





# Página principal
def index(request):
    return render(request, 'app/index.html')


# CLIENTE--------------------------------------------------------------------------------------------------------------------------------------------------------------

def catalogo_cliente(request):
    try:
        response = requests.get('http://127.0.0.1:8000/producto/productos-con-stock')
        response.raise_for_status()
        productos_api = response.json()
        
        # Adaptar la estructura de la API a lo que espera el template
        productos = []
        for prod in productos_api:
            productos.append({
                'id': prod['id_producto'],  # Mapear id_producto a id
                'nombre': prod.get('nombre', ''),
                'descripcion': prod.get('descripcion', ''),
                'precio': prod.get('precio', 0),
                'marca': prod.get('marca', ''),
                'stock': prod.get('stock', 1)  # Asumo que si está en la API tiene stock
            })
        
        print(">>> Productos adaptados:", productos)
    except requests.RequestException as e:
        print(">>> ERROR al consumir la API:", e)
        productos = []
    
    return render(request, 'app/cliente/catalogo.html', {'productos': productos})

#@cliente_requerido
def detalle_producto(request):
    """
    Obtiene el parámetro 'id' de la query string: /cliente/detalle/?id=<producto_id>
    y pasa ese Producto al template. Si no hay 'id', redirige al catálogo.
    """
    pid = request.GET.get('id')
    if not pid:
        return redirect('catalogo_cliente')

    producto = get_object_or_404(Producto, id=pid)
    return render(request, 'app/cliente/detalle_producto.html', {'producto': producto})

#CRUD CARRITO
#@cliente_requerido
def carrito_cliente(request):
    """
    Versión que no hace GET /producto/{id} (405), sino un único GET a productos-con-stock
    y luego filtra en Python.
    """
    carrito = request.session.get('carrito', {})  # ej. {'3': 2, '7': 1}
    carrito_items = []
    total_clp = 0.0

    if not carrito:
        # Carrito vacío: renderizamos directamente sin llamadas a la API
        return render(request, 'app/cliente/carrito.html', {'carrito_items': [], 'total': 0})

    # 1) Traer TODOS los productos con stock de una sola vez
    try:
        resp = requests.get('http://127.0.0.1:8000/producto/productos-con-stock')
        resp.raise_for_status()
        lista_productos = resp.json()  # lista de dicts con claves: 'id_producto', 'nombre', 'precio', 'stock', etc.
    except requests.RequestException as e:
        # Si falla esta llamada, no podemos mostrar el carrito
        messages.error(request, "Error al obtener productos de la API. Inténtalo más tarde.")
        return render(request, 'app/cliente/carrito.html', {'carrito_items': [], 'total': 0})

    # 2) Convertimos lista_productos en un diccionario para acceso rápido por ID
    productos_por_id = {}
    for p in lista_productos:
        # asumo que cada p tiene 'id_producto', 'nombre', 'precio', 'stock'
        productos_por_id[p['id_producto']] = {
            'id': p['id_producto'],
            'nombre': p.get('nombre', 'Sin nombre'),
            'precio': float(p.get('precio', 0)),
            'stock': int(p.get('stock', 0)),
            # Si hubiera URL de imagen en el JSON: 'imagen_url': p.get('imagen_url')
        }

    # 3) Ahora iteramos sobre el carrito en sesión
    for prod_id_str, cantidad in carrito.items():
        try:
            prod_id = int(prod_id_str)
        except ValueError:
            continue

        # Obtenemos el dict de producto desde productos_por_id
        producto_data = productos_por_id.get(prod_id)
        if not producto_data:
            # Si ese ID no está en productos_con_stock, lo omitimos
            continue

        # Ajustar cantidad si supera stock
        if cantidad > producto_data['stock']:
            cantidad = producto_data['stock']

        subtotal = producto_data['precio'] * cantidad
        total_clp += subtotal

        carrito_items.append({
            'producto':      producto_data,
            'cantidad':      cantidad,
            'precio_unidad': producto_data['precio'],
            'subtotal':      subtotal,
        })

    contexto = {
        'carrito_items': carrito_items,
        'total': total_clp,
    }
    return render(request, 'app/cliente/carrito.html', contexto)

def agregar_al_carrito(request, producto_id):
    """
    Añade un producto al carrito en sesión usando solo el ID.
    No dependemos del ORM de Django (Producto), sino que confiamos en que el ID existe en la API.
    """

    # 1) Obtenemos (o creamos) el carrito de la sesión:
    carrito = request.session.get('carrito', {})  # e.g. {'3': 2, '7': 1}

    prod_id_str = str(producto_id)
    cantidad_actual = carrito.get(prod_id_str, 0)
    carrito[prod_id_str] = cantidad_actual + 1

    # 2) Guardamos de vuelta en sesión:
    request.session['carrito'] = carrito

    # 3) Redirigimos a la vista del carrito:
    return redirect('carrito_cliente')

def eliminar_del_carrito(request, producto_id):
    """
    Elimina por completo el producto del carrito en sesión.
    """
    carrito = request.session.get('carrito', {})
    prod_id_str = str(producto_id)
    if prod_id_str in carrito:
        carrito.pop(prod_id_str)
        request.session['carrito'] = carrito
    return redirect('carrito_cliente')

def actualizar_cantidad(request, producto_id):
    """
    Actualiza la cantidad de un producto en el carrito sin validar contra el modelo Django.
    La validación de stock real se hará luego al renderizar el carrito consumiendo la API.
    """
    if request.method == 'POST':
        try:
            cantidad_nueva = int(request.POST.get('cantidad', 1))
        except ValueError:
            cantidad_nueva = 1

        if cantidad_nueva < 1:
            cantidad_nueva = 1

        carrito = request.session.get('carrito', {})
        carrito[str(producto_id)] = cantidad_nueva
        request.session['carrito'] = carrito

    return redirect('carrito_cliente')





@cliente_login_required
def checkout(request):
    # 1) Levantamos el carrito de sesión
    carrito = request.session.get('carrito', {})
    carrito_items = []
    total_clp = 0.0

    # Si el carrito está vacío, redirigimos al catálogo
    if not carrito:
        messages.info(request, "Tu carrito está vacío. Agrega productos antes de continuar.")
        return redirect('catalogo_cliente')

    # 2) Traemos todos los productos con stock (una sola llamada a la API)
    try:
        resp = requests.get('http://127.0.0.1:8000/producto/productos-con-stock')
        resp.raise_for_status()
        lista_productos = resp.json()
    except requests.RequestException:
        messages.error(request, "Error al obtener los productos de la API. Inténtalo más tarde.")
        return redirect('carrito_cliente')

    # 3) Dict auxiliar {id_producto: {...}}
    productos_por_id = {
        p['id_producto']: {
            'id': p['id_producto'],
            'nombre': p.get('nombre', 'Sin nombre'),
            'precio': float(p.get('precio', 0)),
            'stock': int(p.get('stock', 0)),
        }
        for p in lista_productos
    }

    # 4) Recorremos los ítems del carrito
    for prod_id_str, cantidad in carrito.items():
        try:
            prod_id = int(prod_id_str)
        except ValueError:
            continue

        producto_data = productos_por_id.get(prod_id)
        if not producto_data:
            continue

        if cantidad > producto_data['stock']:
            cantidad = producto_data['stock']

        subtotal = producto_data['precio'] * cantidad
        total_clp += subtotal

        carrito_items.append({
            'producto': producto_data,
            'cantidad': cantidad,
            'precio_unidad': producto_data['precio'],
            'subtotal': subtotal,
        })

    # 5) Si ya no quedó nada válido en el carrito
    if not carrito_items:
        messages.info(request, "Los productos en tu carrito ya no están disponibles.")
        request.session['carrito'] = {}
        return redirect('catalogo_cliente')

    # 6) GET → mostrar checkout
    if request.method == 'GET':
        return render(request, 'app/cliente/checkout.html', {
            'carrito_items': carrito_items,
            'total_clp': total_clp,
        })

    # 7) POST → procesar formulario
    direccion = request.POST.get('direccion', '').strip()
    metodo_pago = request.POST.get('pago')
    tipo_entrega = request.POST.get('entrega')

    if tipo_entrega not in ('retiro', 'despacho'):
        messages.error(request, "Por favor selecciona un método de entrega.")
        return redirect('checkout')

    if tipo_entrega == 'despacho':
        total_clp += 2990

    if metodo_pago not in ('tarjeta', 'transferencia') or (tipo_entrega == 'despacho' and not direccion):
        messages.error(request, "Ingresa la dirección (si es despacho) y un método de pago válido.")
        return render(request, 'app/cliente/checkout.html', {
            'carrito_items': carrito_items,
            'total_clp': total_clp,
            'direccion_prev': direccion,
            'pago_prev': metodo_pago,
            'entrega_prev': tipo_entrega,
        })

    # ------------------------------------------------------------------
    # 8) Obtenemos (o creamos) el perfil de cliente
    # ------------------------------------------------------------------
    usuario_session = request.session.get('usuario')
    if usuario_session is None:
        messages.error(request, "Debes iniciar sesión para finalizar la compra.")
        return redirect('login')

    cliente_id = usuario_session.get('id_cliente')

    try:
        cliente_obj = Cliente.objects.get(id=cliente_id)
    except Cliente.DoesNotExist:
        try:
            response = requests.get(f'http://127.0.0.1:8000/cliente/{cliente_id}/')
            if response.status_code == 200:
                datos = response.json()
            else:
                messages.error(request, "El cliente no existe en la API.")
                return redirect('catalogo_cliente')
        except Exception as e:
            messages.error(request, f"Error al conectar con la API: {str(e)}")
            return redirect('catalogo_cliente')

        user, created = User.objects.get_or_create(
            id=cliente_id,
            defaults={
                'username': datos['usuario'],
                'first_name': datos['nombre'],
                'last_name': datos['apellido'],
                'email': datos['correo'],
            }
        )
        if created:
            user.set_password('hola123')
            user.save()

        cliente_obj, _ = Cliente.objects.get_or_create(
            id=cliente_id,
            defaults={
                'user': user,
                'direccion': datos.get('direccion', ''),
            }
        )

    # ------------------------------------------------------------------
    # 9) Obtenemos (o creamos) un Empleado con rol="Vendedor"
    # ------------------------------------------------------------------
    estado_ped, _ = EstadoPedido.objects.get_or_create(desc_estado='Pendiente')
    empleado_vendedor = Empleado.objects.filter(rol__nombre_rol='Vendedor').first()

    if not empleado_vendedor:
        try:
            resp_emp = requests.get('http://127.0.0.1:8000/empleado/')
            resp_emp.raise_for_status()
            lista_emps = resp_emp.json()
            
            datos_vendedor = next((e for e in lista_emps if e.get('rol', '').lower() == 'vendedor'), None)
            if not datos_vendedor:
                messages.error(request, "No se encontró ningún empleado con rol 'vendedor' en la API.")
                return redirect('carrito_cliente')

            rol_vendedor, _ = Rol.objects.get_or_create(nombre_rol='Vendedor')
            
            user_v, created = User.objects.get_or_create(
                id=datos_vendedor['id_empleado'],
                defaults={
                    'username': datos_vendedor['usuario'],
                    'first_name': datos_vendedor.get('nombre', ''),
                    'last_name': datos_vendedor.get('apellido', ''),
                    'email': datos_vendedor.get('correo', '')
                }
            )
            if created:
                user_v.set_password(datos_vendedor.get('contrasena', 'hola123'))
                user_v.save()

            empleado_vendedor, _ = Empleado.objects.get_or_create(
                id=datos_vendedor['id_empleado'],
                defaults={
                    'user': user_v,
                    'rut': datos_vendedor.get('rut', ''),
                    'rol': rol_vendedor,
                }
            )
        except Exception as e:
            messages.error(request, f"No se pudo obtener datos de empleados: {str(e)}")
            return redirect('carrito_cliente')

    # ------------------------------------------------------------------
    # 10) Pago con TARJETA (PayPal)
    # ------------------------------------------------------------------
    if metodo_pago == 'tarjeta':
        try:
            valor_dolar_clp = requests.get('https://mindicador.cl/api/dolar').json()['serie'][0]['valor']
        except Exception:
            messages.error(request, "No se pudo obtener el valor del dólar. Inténtalo más tarde.")
            return redirect('carrito_cliente')

        total_usd = round(total_clp / float(valor_dolar_clp), 2)
        tipo_pago_obj, _ = TipoPago.objects.get_or_create(tipo_pago='tarjeta')
        pago_obj = Pago.objects.create(estado_pago='Pendiente', tipo_pago=tipo_pago_obj)

        nuevo_pedido = Pedido.objects.create(
            tipo_entrega='Despacho a domicilio' if tipo_entrega == 'despacho' else 'Retiro en tienda',
            cliente=cliente_obj,
            estado_pedido=estado_ped,
            pago=pago_obj,
            empleado=empleado_vendedor
        )

        for item in carrito_items:
            # Obtener o crear el producto en la base de datos local
            producto_obj, _ = Producto.objects.get_or_create(
                id=item['producto']['id'],
                defaults={
                    'nombre': item['producto']['nombre'],
                    'precio': item['producto']['precio'],
                    # Agrega otros campos necesarios de tu modelo Producto
                }
            )
            
            DetallePedido.objects.create(
                cantidad=item['cantidad'],
                precio_unidad=item['precio_unidad'],
                producto=producto_obj,
                pedido=nuevo_pedido
            )

        request.session['carrito'] = {}
        request.session['ultimo_pedido_id'] = nuevo_pedido.id

        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': f"{total_usd:.2f}",
            'item_name': f'Pedido #{nuevo_pedido.id}',
            'invoice': str(nuevo_pedido.id),
            'currency_code': 'USD',
            'notify_url': request.build_absolute_uri('/paypal/'),
            'return_url': request.build_absolute_uri('/cliente/pago/'),
            'cancel_return': request.build_absolute_uri('/cliente/carrito/'),
        }
        form = PayPalPaymentsForm(initial=paypal_dict)
        return render(request, 'app/cliente/paypal_payment.html', {'form': form})

    # ------------------------------------------------------------------
    # 11) Pago por TRANSFERENCIA
    # ------------------------------------------------------------------
    tipo_pago_obj, _ = TipoPago.objects.get_or_create(tipo_pago='transferencia')
    pago_obj = Pago.objects.create(estado_pago='Pendiente', tipo_pago=tipo_pago_obj)

    nuevo_pedido = Pedido.objects.create(
        tipo_entrega='Despacho a domicilio' if tipo_entrega == 'despacho' else 'Retiro en tienda',
        cliente=cliente_obj,
        estado_pedido=estado_ped,
        pago=pago_obj,
        empleado=empleado_vendedor
    )

    for item in carrito_items:
        producto_obj, _ = Producto.objects.get_or_create(
            id=item['producto']['id'],
            defaults={
                'nombre': item['producto']['nombre'],
                'precio': item['producto']['precio'],
            }
        )
        
        DetallePedido.objects.create(
            cantidad=item['cantidad'],
            precio_unidad=item['precio_unidad'],
            producto=producto_obj,
            pedido=nuevo_pedido
        )

    request.session['carrito'] = {}
    request.session['ultimo_pedido_id'] = nuevo_pedido.id
    return redirect('pago_cliente')

#------------------------------------------------------------------------------------------- #




@cliente_login_required
def pago_cliente(request):
    """
    Muestra la pantalla de confirmación de pago:
      - Si el pedido es por PayPal (tarjeta), ya estará pagado y se muestra “Pago Confirmado”.
      - Si es transferencia, se muestran los datos bancarios y el formulario para subir comprobante.
    """
    pedido_id = request.session.get('ultimo_pedido_id')
    if not pedido_id:
        messages.error(request, "No se encontró ningún pedido reciente.")
        return redirect('catalogo_cliente')

    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalle_items = pedido.detalles.all()  # asumiendo related_name='detalles'
    total_final = sum(item.precio_unidad * item.cantidad for item in detalle_items)
    if pedido.tipo_entrega == 'Despacho a domicilio':
        total_final += 2990

    contexto = {
        'pedido': pedido,
        'detalle_items': detalle_items,
        'total_final': total_final,
    }
    return render(request, 'app/cliente/pago.html', contexto)


@cliente_login_required
def subir_comprobante(request, pedido_id):
    """
    Recibe el POST del formulario de transferencia:
    - Guarda la imagen en Pago.comprobante_transferencia
    - Cambia estado_pago a “En revisión”
    - Redirige nuevamente a pago_cliente
    """
    if request.method != 'POST':
        return redirect('pago_cliente')

    pedido = get_object_or_404(Pedido, id=pedido_id)
    pago = pedido.pago  # relación ForeignKey

    archivo = request.FILES.get('comprobante')
    if not archivo:
        messages.error(request, "No se seleccionó ningún archivo.")
        return redirect('pago_cliente')

    # Guardar el archivo en el campo ImageField
    pago.comprobante_transferencia = archivo
    # Cambiar estado del pago a “En revisión” (o como prefieras)
    pago.estado_pago = 'En revisión'
    pedido.save()
    print(f'Pedido creado: {pedido.id}')


    messages.success(request, "¡Comprobante subido con éxito! El contador lo revisará pronto.")
    return redirect('pago_cliente')

def descargar_comprobante_pdf(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)
    detalle_items = DetallePedido.objects.filter(pedido=pedido)

    total = sum(item.subtotal() for item in detalle_items)
    if pedido.tipo_despacho == 'despacho':
        total_final = total + 2990
    else:
        total_final = total

    html_string = render_to_string('app/comprobante_pdf.html', {
        'pedido': pedido,
        'detalle_items': detalle_items,
        'total_final': total_final,
    })

    html = HTML(string=html_string)
    result = html.write_pdf()

    response = HttpResponse(result, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=comprobante_pedido_{pedido.id}.pdf'
    return response







# CONTADOR ---------------------------------------------------------------------------------------------------------------------------------------

#@rol_requerido(['Contador'])
def pagos_contador(request):
    """
    Trae todos los Pagos y para cada uno calcula el total (suma de detalles + despacho si aplica).
    Devuelve al template una lista de diccionarios: {'pago': Pago, 'pedido': Pedido, 'total': monto}.
    """
    # Obtener todos los pagos ordenados por fecha (más reciente primero)
    pagos = Pago.objects.all().order_by('-fecha_pago')
    pagos_data = []

    for pago in pagos:
        # (Asumimos que cada Pago tiene exactamente un Pedido relacionado; si hay más, tomamos el primero)
        pedido = pago.pedidos.first()
        if pedido:
            # Sumar todos los detalles de ese Pedido
            subtotal = sum(d.precio_unidad * d.cantidad for d in pedido.detalles.all())
            # Si el pedido es "Despacho a domicilio", agregamos 2.990 CLP
            if pedido.tipo_entrega.lower().startswith('despacho'):
                total = subtotal + 2990
            else:
                total = subtotal
        else:
            total = 0

        pagos_data.append({
            'pago': pago,
            'pedido': pedido,
            'total': total,
        })

    # Configurar la paginación - 10 elementos por página
    paginator = Paginator(pagos_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'app/contador/pagos_contador.html', {
        'page_obj': page_obj,
        'pagos_data': page_obj.object_list  # Mantenemos ambos por compatibilidad
    })


#@rol_requerido(['Contador'])
def confirmar_pago(request, pago_id):
    # 1) Obtener el objeto Pago (o 404 si no existe)
    pago = get_object_or_404(Pago, id=pago_id)

    # 2) Verificar si se pidió rechazar via query string
    rechazar = request.GET.get('rechazar', None)

    if pago.estado_pago != 'Pendiente':
        messages.info(request, f"El pago #{pago.id} ya fue procesado.")
        return redirect('pagos_contador')

    # 3) Dependiendo de si viene ?rechazar=1 o no
    if rechazar:
        pago.estado_pago = 'Rechazado'
        pago.save()
        # Opcional: poner el estado del pedido a “Rechazado” o similar
        # (asumimos que existe un EstadoPedido con desc_estado='Rechazado')
        estado_rechazado, _ = EstadoPedido.objects.get_or_create(desc_estado='Rechazado')
        # Actualizar todos los pedidos asociados a este Pago
        for ped in pago.pedidos.all():
            ped.estado_pedido = estado_rechazado
            ped.save()

        messages.success(request, f"Pago #{pago.id} RECHAZADO correctamente.")
        return redirect('pagos_contador')

    # 4) Si no viene “rechazar”, lo confirmamos
    pago.estado_pago = 'Confirmado'
    pago.save()

    # Cambiar el estado del Pedido a “Pagado” (o como lo llames)
    estado_pagado, _ = EstadoPedido.objects.get_or_create(desc_estado='Pagado')
    for ped in pago.pedidos.all():
        ped.estado_pedido = estado_pagado
        ped.save()

    messages.success(request, f"Pago #{pago.id} confirmado con éxito.")
    return redirect('pagos_contador')


#@rol_requerido(['Contador'])
def registro_entrega(request):
    return render(request, 'app/contador/registro_entrega.html')



# VENDEDOR --------------------------------------------------------------------
#@login_required
def pedidos_vendedor(request):
    """
    Muestra pedidos en estado 'Pagado' para aprobar/rechazar
    """
    estado_pagado = get_object_or_404(EstadoPedido, desc_estado='Pagado')
    pedidos = Pedido.objects.filter(
        estado_pedido=estado_pagado
    ).exclude(
        estado_pedido__desc_estado__in=['En preparación', 'Rechazado']
    ).order_by('-fecha')

    pedidos_data = []
    for pedido in pedidos:
        pedidos_data.append({
            'pedido': pedido,
            'cliente': pedido.cliente.user.get_full_name() or pedido.cliente.user.username,
            'total': pedido.get_total_con_despacho(),
            'fecha': pedido.fecha.strftime('%d/%m/%Y'),
        })

    return render(request, 'app/vendedor/pedidos_vendedor.html', {
        'pedidos_data': pedidos_data
    })

#@login_required
def gestionar_pedido_vendedor(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if pedido.estado_pedido.desc_estado != 'Pagado':
        messages.warning(request, "Este pedido no está listo para aprobación.")
        return redirect('pedidos_vendedor')

    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'aprobar':
            estado_preparacion, _ = EstadoPedido.objects.get_or_create(desc_estado='En preparación')
            pedido.estado_pedido = estado_preparacion
            pedido.save()

            if request.user.is_authenticated:
                PedidoHistorial.objects.create(
                    pedido=pedido,
                    usuario=request.user,
                    accion="Aprobado por vendedor",
                    estado_anterior="Pagado",
                    estado_nuevo="En preparación"
                )
            messages.success(request, f"Pedido #{pedido.id} enviado a bodega.")
            return redirect('pedidos_vendedor')

        elif accion == 'rechazar':
            motivo = request.POST.get('motivo', '').strip()
            if not motivo:
                messages.error(request, "Debe ingresar un motivo para rechazar el pedido.")
                return redirect('pedidos_vendedor')

            estado_rechazado, _ = EstadoPedido.objects.get_or_create(desc_estado='Rechazado')
            pedido.estado_pedido = estado_rechazado
            pedido.motivo_rechazo = motivo
            pedido.save()

            if request.user.is_authenticated:
                PedidoHistorial.objects.create(
                    pedido=pedido,
                    usuario=request.user,
                    accion="Rechazado por vendedor",
                    estado_anterior="Pagado",
                    estado_nuevo="Rechazado",
                    comentario=motivo
                )
            messages.success(request, f"Pedido #{pedido.id} rechazado correctamente.")
            return redirect('pedidos_vendedor')

    return redirect('pedidos_vendedor')

#@login_required
def pedidos_preparados(request):
    """
    Vista para mostrar pedidos en estado 'Preparado' listos para despacho
    """
    estado_preparado = get_object_or_404(EstadoPedido, desc_estado='Preparado')
    pedidos = Pedido.objects.filter(estado_pedido=estado_preparado).order_by('-fecha')

    pedidos_data = []
    for pedido in pedidos:
        pedidos_data.append({
            'pedido': pedido,
            'cliente': pedido.cliente.user.get_full_name() or pedido.cliente.user.username,
            'total': pedido.get_total_con_despacho(),
            'fecha': pedido.fecha.strftime('%d/%m/%Y'),
            'estado': pedido.estado_pedido.desc_estado,
        })

    return render(request, 'app/vendedor/pedidos_preparados.html', {
        'pedidos_data': pedidos_data
    })
    
    #@login_required
def marcar_como_despachado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if pedido.estado_pedido.desc_estado == 'Preparado':
        estado_despachado, _ = EstadoPedido.objects.get_or_create(desc_estado='Despachado')
        pedido.estado_pedido = estado_despachado
        pedido.save()

        if request.user.is_authenticated:
            PedidoHistorial.objects.create(
                pedido=pedido,
                usuario=request.user,
                accion="Despachado por vendedor",
                estado_anterior="Preparado",
                estado_nuevo="Despachado"
            )
        messages.success(request, f"Pedido #{pedido.id} marcado como despachado.")
    return redirect('pedidos_preparados')
# BODEGUERO ----------------------------------------------------------------------------------------------------------------------------

#@login_required
def ordenes_bodeguero(request):
    """
    Muestra los pedidos en estado 'En preparación'
    """
    estado_en_preparacion = get_object_or_404(EstadoPedido, desc_estado='En preparación')
    pedidos = Pedido.objects.filter(estado_pedido=estado_en_preparacion).order_by('-fecha')

    pedidos_data = []
    for pedido in pedidos:
        pedidos_data.append({
            'pedido': pedido,
            'cliente': f"{pedido.cliente.user.first_name} {pedido.cliente.user.last_name}",
            'total': pedido.get_total_con_despacho(),
            'fecha': pedido.fecha.strftime('%d/%m/%Y'),
            'estado': pedido.estado_pedido.desc_estado,
        })

    return render(request, 'app/bodeguero/ordenes_bodeguero.html', {
        'pedidos_data': pedidos_data
    })

#@login_required
def preparar_pedido(request, pedido_id):
    """
    Marca un pedido como 'Preparado'.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if pedido.estado_pedido.desc_estado == 'En preparación':
        estado_preparado, _ = EstadoPedido.objects.get_or_create(desc_estado='Preparado')
        pedido.estado_pedido = estado_preparado
        pedido.save()

        # Solo registrar historial si el usuario está autenticado
        if request.user.is_authenticated:
            PedidoHistorial.objects.create(
                pedido=pedido,
                usuario=request.user,
                accion="Preparado en bodega",
                estado_anterior="En preparación",
                estado_nuevo="Preparado"
            )
        messages.success(request, f"Pedido #{pedido.id} marcado como preparado.")
    else:
        messages.warning(request, "Solo se pueden preparar pedidos en estado 'En preparación'.")
    return redirect('ordenes_bodeguero')

# ADMIN----------------------------------------------------------------------------------------------------------------------------

#@rol_requerido(['Administrador'])
def dashboard_admin(request):
    # Opcional: datos de ejemplo para el gráfico
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
    pedidos_por_mes = [45, 60, 30, 75, 50, 90]
    context = {
        'meses': meses,
        'pedidos_por_mes': pedidos_por_mes,
    }
    return render(request, 'app/admin/dashboard_admin.html', context)

#@rol_requerido(['Administrador'])
def usuarios_admin(request):
    return render(request, 'app/admin/usuarios_admin.html')

#@rol_requerido(['Administrador'])
def pedidos_admin(request):
    return render(request, 'app/admin/pedidos_admin.html')

#@rol_requerido(['Administrador'])
def inventario_admin(request):
    return render(request, 'app/admin/inventario_admin.html')


#INFORMACION-------------------------------------------------------------------------------------------------------------------------------------------

def contactanos(request):
    return render(request, 'app/informacion/contactanos.html')

def somos(request):
    return render(request, 'app/informacion/somos.html')

def terminos(request):
    return render(request, 'app/informacion/terminos.html')

def error_404_view(request, exception):
    return render(request, 'app/informacion/404.html', status=404)


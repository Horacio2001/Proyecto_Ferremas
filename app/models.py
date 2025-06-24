from django.db import models
from django.contrib.auth.models import User

class Marca(models.Model):
    nombre = models.CharField(max_length=60)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name='productos')
    stock = models.IntegerField(default=0)   # Cantidad disponible

    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_cliente')
    suscribir_noticias = models.BooleanField(default=False)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} ({self.user.email})'

class Rol(models.Model):
    nombre_rol = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_rol

class Empleado(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_empleado')
    rut = models.CharField(max_length=20, unique=True)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, related_name='empleados')
    cambio_contrasena = models.BooleanField(default=False)  # Para “primer login” del admin

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} ({self.rol.nombre_rol})'

class EstadoPedido(models.Model):
    desc_estado = models.CharField(max_length=50)  # Ej: 'Pagado', 'Aprobado Vendedor', 'En preparación', 'En camino', 'Entregado'

    def __str__(self):
        return self.desc_estado

class TipoPago(models.Model):
    tipo_pago = models.CharField(max_length=50)

    def __str__(self):
        return self.tipo_pago

class Pago(models.Model):
    estado_pago = models.CharField(max_length=50)
    fecha_pago = models.DateField(auto_now_add=True)
    tipo_pago = models.ForeignKey(TipoPago, on_delete=models.PROTECT, related_name='pagos')
    comprobante_transferencia = models.ImageField(
        upload_to='comprobantes/', null=True, blank=True
    )

    def __str__(self):
        return f'Pago #{self.id} → {self.estado_pago}'

class Pedido(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    tipo_entrega = models.CharField(max_length=50)  # “Retiro en tienda” o “Despacho a domicilio”
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos')
    estado_pedido = models.ForeignKey(EstadoPedido, on_delete=models.PROTECT, related_name='pedidos')
    pago = models.ForeignKey(Pago, on_delete=models.PROTECT, related_name='pedidos')
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT, related_name='pedidos')
    motivo_rechazo = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f'Pedido #{self.id} → {self.cliente.user.first_name} {self.cliente.user.last_name}'
    def get_total(self):
        # Suma precio_unidad * cantidad para cada detalle
        return sum(detalle.precio_unidad * detalle.cantidad for detalle in self.detalles.all())

    def get_total_con_despacho(self):
        total = self.get_total()
        if self.tipo_entrega == 'Despacho a domicilio':
            total += 2990
        return total

class DetallePedido(models.Model):
    cantidad = models.IntegerField()
    precio_unidad = models.DecimalField(max_digits=10, decimal_places=2)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='detalles')
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')

    def __str__(self):
        return f'{self.cantidad}×{self.producto.nombre} (Pedido #{self.pedido.id})'
    
class PedidoHistorial(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    usuario = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,  # Si se elimina el usuario, se pondrá NULL
        null=True,                  # Permite valores NULL en la base de datos
        blank=True,                 # Permite dejar el campo vacío en formularios
        verbose_name="Usuario responsable"
    )
    fecha = models.DateTimeField(auto_now_add=True)
    accion = models.CharField(max_length=100)
    estado_anterior = models.CharField(max_length=50)
    estado_nuevo = models.CharField(max_length=50)
    comentario = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Historial de pedido"
        verbose_name_plural = "Historiales de pedidos"

    def __str__(self):
        return f"Historial #{self.id} - Pedido {self.pedido.id} ({self.accion})"

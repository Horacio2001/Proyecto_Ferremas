from django.contrib import admin
from .models import (
    Marca, Producto, Cliente,
    Rol, Empleado, EstadoPedido,
    TipoPago, Pago, Pedido, DetallePedido
)

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio', 'marca', 'stock')
    list_filter = ('marca',)
    search_fields = ('nombre',)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    # Mostramos User (username), nombre y apellido desde el user, y el email
    list_display = ('id', 'usuario_username', 'usuario_first_name',
                    'usuario_last_name', 'usuario_email', 'suscribir_noticias')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')

    # Métodos para mostrar datos anidados de user
    def usuario_username(self, obj):
        return obj.user.username
    usuario_username.short_description = 'Usuario'

    def usuario_first_name(self, obj):
        return obj.user.first_name
    usuario_first_name.short_description = 'Nombre'

    def usuario_last_name(self, obj):
        return obj.user.last_name
    usuario_last_name.short_description = 'Apellido'

    def usuario_email(self, obj):
        return obj.user.email
    usuario_email.short_description = 'Correo'

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_rol')
    search_fields = ('nombre_rol',)

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    # Mostramos user.username, user.first_name, user.last_name, rut y rol
    list_display = ('id', 'usuario_username', 'usuario_first_name',
                    'usuario_last_name', 'rut', 'rol', 'cambio_contrasena')
    list_filter = ('rol',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'rut')

    def usuario_username(self, obj):
        return obj.user.username
    usuario_username.short_description = 'Usuario'

    def usuario_first_name(self, obj):
        return obj.user.first_name
    usuario_first_name.short_description = 'Nombre'

    def usuario_last_name(self, obj):
        return obj.user.last_name
    usuario_last_name.short_description = 'Apellido'

@admin.register(EstadoPedido)
class EstadoPedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'desc_estado')
    search_fields = ('desc_estado',)

@admin.register(TipoPago)
class TipoPagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_pago')
    search_fields = ('tipo_pago',)

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'estado_pago', 'tipo_pago', 'fecha_pago')
    list_filter = ('estado_pago', 'tipo_pago')
    search_fields = ('estado_pago',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_usuario', 'estado_pedido', 'pago', 'empleado_usuario', 'fecha')
    list_filter = ('estado_pedido', 'tipo_entrega')
    search_fields = ('cliente__user__email',)

    def cliente_usuario(self, obj):
        return obj.cliente.user.username
    cliente_usuario.short_description = 'Cliente'

    def empleado_usuario(self, obj):
        return obj.empleado.user.username
    empleado_usuario.short_description = 'Empleado'

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'producto', 'cantidad', 'precio_unidad')
    list_filter = ('pedido',)
    search_fields = ('producto__nombre',)

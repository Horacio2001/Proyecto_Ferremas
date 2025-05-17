from django.urls import path
from . import views

urlpatterns = [
    # Página principal e index
    path('', views.index, name='index'),
    path('inicio/', views.index, name='inicio'),

    # Login y registro
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_cliente, name='registro_cliente'),


    # Cliente
    path('cliente/catalogo/', views.catalogo_cliente, name='catalogo_cliente'),
    path('cliente/carrito/', views.carrito_cliente, name='carrito_cliente'),
    path('cliente/detalle/', views.detalle_producto, name='detalle_producto'),
    path('cliente/checkout/', views.checkout, name='checkout'),
    path('cliente/pago/', views.pago_cliente, name='pago_cliente'),

    # Vendedor
    path('vendedor/pedidos/', views.pedidos_vendedor, name='pedidos_vendedor'),
    path('vendedor/aprobar/', views.aprobar_pedido, name='aprobar_pedido'),
    path('vendedor/orden/', views.orden_pedido, name='orden_pedido'),
    

    # Bodeguero
    path('bodeguero/ordenes/', views.ordenes_bodeguero, name='ordenes_bodeguero'),
    path('bodeguero/preparar/', views.preparar_pedido, name='preparar_pedido'),

    # Contador
    path('contador/pagos/', views.pagos_contador, name='pagos_contador'),
    path('contador/confirmar/', views.confirmar_pago, name='confirmar_pago'),
    path('contador/registros/', views.registro_entrega, name='registro_entrega'),

    # Admin
    path('panel/dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('panel/usuarios/', views.usuarios_admin, name='usuarios_admin'),
    path('panel/pedidos/', views.pedidos_admin, name='pedidos_admin'),
    path('panel/inventario/', views.inventario_admin, name='inventario_admin'),
]

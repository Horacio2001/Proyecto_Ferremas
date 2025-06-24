from django.urls import path
from . import views

urlpatterns = [
    # Página principal e index
    path('', views.index, name='index'),
    path('inicio/', views.index, name='inicio'),

    # Login y registro
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_cliente, name='registro_cliente'),
    path('cambiar_contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),


    # Cliente
    path('cliente/catalogo/', views.catalogo_cliente, name='catalogo_cliente'),
    path('cliente/detalle/', views.detalle_producto, name='detalle_producto'),
    path('cliente/carrito/', views.carrito_cliente, name='carrito_cliente'),
    path('cliente/carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('cliente/carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('cliente/carrito/actualizar/<int:producto_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('cliente/checkout/', views.checkout, name='checkout'),
    path('cliente/pago/', views.pago_cliente, name='pago_cliente'),
    path('descargar-comprobante/<int:pedido_id>/', views.descargar_comprobante_pdf, name='descargar_comprobante'),
    path('subir-comprobante/<int:pedido_id>/', views.subir_comprobante, name='subir_comprobante'),



      # Bodeguero
    path('bodeguero/ordenes/', views.ordenes_bodeguero, name='ordenes_bodeguero'),
    path('bodeguero/preparar/<int:pedido_id>/', views.preparar_pedido, name='preparar_pedido'),
    
    # Vendedor
    path('vendedor/pedidos/', views.pedidos_vendedor, name='pedidos_vendedor'),
    path('vendedor/gestionar/<int:pedido_id>/', views.gestionar_pedido_vendedor, name='gestionar_pedido_vendedor'),
    path('vendedor/pedidos-preparados/', views.pedidos_preparados, name='pedidos_preparados'),
    path('vendedor/marcar-despachado/<int:pedido_id>/', views.marcar_como_despachado, name='marcar_como_despachado'),


    # Contador
    path('contador/pagos/', views.pagos_contador, name='pagos_contador'),
    path('contador/confirmar/<int:pago_id>/', views.confirmar_pago, name='confirmar_pago'),
    path('contador/registros/', views.registro_entrega, name='registro_entrega'),

    # Admin
    path('panel/dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('panel/usuarios/', views.usuarios_admin, name='usuarios_admin'),
    path('panel/pedidos/', views.pedidos_admin, name='pedidos_admin'),
    path('panel/inventario/', views.inventario_admin, name='inventario_admin'),

    #INFORMACION
    path('informacion/contactanos/', views.contactanos, name='contactanos'),
    path('informacion/somos/', views.somos, name='somos'),
    path('informacion/terminos/', views.terminos, name='terminos'),
]

# Esto sirve para que Django sirva MEDIA_URL en modo DEBUG (dev server)
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# app/decorators.py

from django.shortcuts import redirect
from functools import wraps

def login_required_view(func):
    """
    Si el usuario no está autenticado, lo manda a 'login'.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return func(request, *args, **kwargs)
    return wrapper

def rol_requerido(roles_permitidos=[]):
    """
    Permite solo a usuarios con perfil_empleado cuyo rol esté en roles_permitidos.
    roles_permitidos: lista de nombres de rol, p. ej. ['Administrador','Contador'].
    """
    def decorador(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # 1) Si no está autenticado, redirigir a login
            if not request.user.is_authenticated:
                return redirect('login')
            # 2) Si no tiene perfil_empleado (es cliente), bloquear
            if not hasattr(request.user, 'perfil_empleado'):
                return redirect('index')
            # 3) Extraer nombre del rol
            nombre_rol = request.user.perfil_empleado.rol.nombre_rol
            # 4) Si está en la lista, permitir; sino, redirigir a index
            if nombre_rol in roles_permitidos:
                return func(request, *args, **kwargs)
            return redirect('index')
        return wrapper
    return decorador

def cliente_requerido(func):
    """
    Sólo permite a usuarios que NO tengan perfil_empleado (es decir, un Cliente normal).
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        # Si tiene atributo perfil_empleado, entonces no es Cliente
        if hasattr(request.user, 'perfil_empleado'):
            return redirect('index')
        return func(request, *args, **kwargs)
    return wrapper

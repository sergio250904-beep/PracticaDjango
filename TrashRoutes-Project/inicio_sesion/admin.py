from django.contrib import admin
from .models import Usuario


class UsuarioAdmin(admin.ModelAdmin):
    # Columnas que se mostrarán en la tabla del panel de administración
    list_display = ('id', 'nombre', 'correo_electronico',
                    'is_active', 'is_staff')

    # Campos por los que podrás buscar usuarios desde el buscador del admin
    search_fields = ('nombre', 'correo_electronico')

    # Filtros laterales para organizar los registros
    list_filter = ('is_active', 'is_staff')


# Registramos el modelo utilizando la configuración personalizada
admin.site.register(Usuario, UsuarioAdmin)

from django.urls import path
from .views import LoginView, RegistroView, GuardarUbiUsuario, GuardarReporte, MostrarReportes, ObtenerUbicacion, VermiPerfil, UsuarioTieneUbicacion, EmitirAlerta, ConsultarAlertas, ObtenerRutasCamion, ObtenerUbicacionCamion

urlpatterns = [
     path('login/', LoginView.as_view(), name='login'),
     path('registro/', RegistroView.as_view(), name='registro'),
     path('guardar-ubi-usuario/', GuardarUbiUsuario.as_view(),
          name='guardar-ubi-usuario'),
     path('guardar-reporte/', GuardarReporte.as_view(), name='guardar-reporte'),
     path('listar-reporte/', MostrarReportes.as_view(), name='listar-reporte'),
     path('obtener-reporte-ubicacion/', ObtenerUbicacion.as_view(),
          name='obtener-reporte-ubicacion'),
     path('ver-mi-perfil/', VermiPerfil.as_view(), name='ver-mi-perfil'),
     path('usuario-tiene-ubicacion/', UsuarioTieneUbicacion.as_view(),
          name='usuario-tiene-ubicacion'),
     path('emitir-alerta/', EmitirAlerta.as_view(), name = 'emitir-alerta'),
     path('consultar-alertas/', ConsultarAlertas.as_view(), name='consultar-alertas'),
     path('obtener-rutas-camion/', ObtenerRutasCamion.as_view(), name='obtener-rutas'),
     path('obtener-ubicacion-camion/', ObtenerUbicacionCamion.as_view(), name="obtener-ubicacion-camion")
]

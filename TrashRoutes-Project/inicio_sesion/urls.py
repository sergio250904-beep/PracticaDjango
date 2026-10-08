from django.urls import path
from .views import LoginView, RegistroView, GuardarUbiUsuario

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('registro/', RegistroView.as_view(), name='registro'),
    path('guardar-ubi-usuario/', GuardarUbiUsuario.as_view(),
         name='guardar-ubi-usuario')
]

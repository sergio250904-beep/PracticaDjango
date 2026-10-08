from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import User
from django.conf import settings


class UsuarioManager(BaseUserManager):
    def create_user(self, correo_electronico, nombre, password=None):
        if not correo_electronico:
            raise ValueError('El usuario debe tener un correo electrónico')

        usuario = self.model(
            correo_electronico=self.normalize_email(correo_electronico),
            nombre=nombre,
        )
        # Selecciona estas 4 líneas en tu editor y presiona la tecla "Tab" una vez
        # para que queden alineadas con el bloque de arriba.
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, correo_electronico, nombre, password=None):
        usuario = self.create_user(
            correo_electronico,
            nombre=nombre,
            password=password,
        )
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.save(using=self._db)
        return usuario


class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=100)
    correo_electronico = models.EmailField(unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UsuarioManager()

    USERNAME_FIELD = 'correo_electronico'
    REQUIRED_FIELDS = ['nombre']

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.nombre


class UsuarioUbicacion(models.Model):
    # Relacionamos con tu usuario autenticado
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ubicacion')
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    address_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        # Usamos correo_electronico ya que vi que lo usas en tu RegistroView
        return f"Ubicación de {self.user.correo_electronico}, {self.longitude}, {self.latitude}"

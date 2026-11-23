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
    # Relacionamos con usuario autenticado
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ubicacion')
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    codigo_postal = models.CharField(max_length=6, blank=True, null=True)
    calle = models.CharField(max_length=50, blank=True, null=True)
    # Cuando agreguemos campos nuevos a un modelo que ya existia agregamos blank=True, null= True en los CharField
    colonia = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Ubicación de {self.user.correo_electronico}, {self.longitude}, {self.latitude}"


class ReporteGenerado(models.Model):
    user = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, verbose_name="Usuario")
    fecha_publicado = models.DateTimeField(auto_now_add=True)
    texto = models.TextField()
    titulo_reporte = models.CharField()
    codigo_postal = models.CharField(max_length=6, blank=True, null=True)
    calle = models.CharField(max_length=50, blank=True, null=True)
    colonia = models.CharField(max_length=50, blank=True, null=True)
    imagen = models.ImageField(
        blank=True, null=True, upload_to='imagenes_reportes')

    def __str__(self):
        return f"{self.titulo_reporte}"

    class Meta:
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"


class AlertaChofer(models.Model):
    codigo_postal = models.CharField(max_length=10)
    incidencia = models.CharField(max_length=50)
    mensaje = models.TextField()
    fecha_emision = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)

class Ruta(models.Model):
    id_ruta = models.CharField(max_length=4)
    nombre_ruta = models.CharField(max_length=50)
    hora_inicio = models.TimeField()
    hora_final = models.TimeField()
    centro_mapa = models.JSONField()
    rutas_coordenadas = models.JSONField()

    def __str__(self):
        return f"{self.nombre_ruta}"

    class Meta:
        verbose_name = "Ruta"
        verbose_name_plural = "Rutas"    
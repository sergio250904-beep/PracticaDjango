from rest_framework import serializers
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'correo_electronico', 'password']
        # Bloqueamos la contraseña para que nunca viaje de regreso a React
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Usamos tu UsuarioManager para que encripte la contraseña correctamente
        usuario = Usuario.objects.create_user(
            correo_electronico=validated_data['correo_electronico'],
            nombre=validated_data['nombre'],
            password=validated_data['password']
        )
        return usuario

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import UsuarioSerializer


class RegistroView(APIView):
    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            # Generamos su token al instante
            token, _ = Token.objects.get_or_create(user=usuario)
            return Response({
                'token': token.key,
                'nombre': usuario.nombre,
                'correo': usuario.correo_electronico
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        correo = request.data.get('correo_electronico')
        password = request.data.get('password')

        # Django verifica si existe el correo y si la contraseña coincide
        usuario = authenticate(correo_electronico=correo, password=password)

        if usuario:
            token, _ = Token.objects.get_or_create(user=usuario)
            return Response({
                'token': token.key,
                'nombre': usuario.nombre,
                'correo': usuario.correo_electronico
            })
        return Response({'error': 'Correo o contraseña incorrectos'}, status=status.HTTP_401_UNAUTHORIZED)

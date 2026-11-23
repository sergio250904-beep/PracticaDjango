from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser


from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.middleware.csrf import get_token

from django.core.exceptions import ObjectDoesNotExist


from .serializers import UsuarioSerializer
from .serializers import UsuarioSerializer, UsuarioUbicacionSerializer

import json
import base64
import uuid


from .models import Usuario, UsuarioUbicacion, ReporteGenerado, AlertaChofer, Ruta


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
            es_chofer = 'matamoros.limpio' in usuario.correo_electronico.lower()

            return Response({
                'token': token.key,
                'nombre': usuario.nombre,
                'correo': usuario.correo_electronico,
                'es_chofer': es_chofer
            })
        return Response({'error': 'Correo o contraseña incorrectos'}, status=status.HTTP_401_UNAUTHORIZED)


class GuardarUbiUsuario(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        longitud = request.data.get("longitud")
        latitud = request.data.get("latitud")
        colonia = request.data.get("colonia")
        calle = request.data.get("calle")
        codigo_postal = request.data.get("codigopostal")

        usuario = request.user

        usuarioUbicacion, created = UsuarioUbicacion.objects.get_or_create(
            user=usuario
        )
        usuarioUbicacion.user = usuario
        usuarioUbicacion.longitude = longitud
        usuarioUbicacion.latitude = latitud
        usuarioUbicacion.colonia = colonia
        usuarioUbicacion.calle = calle
        usuarioUbicacion.codigo_postal = codigo_postal
        usuarioUbicacion.save()
        return Response('OK', status=status.HTTP_200_OK)

# Pendiente de revisar si al cerrar sesion se guarda la ubicacion del usuario al volver a iniciar sesion, si no se guarda, se tendria que hacer un metodo para guardar la ubicacion del usuario al cerrar sesion
class ObtenerUbicacion(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        ubicacion = getattr(user, 'ubicacion', None) or getattr(user, 'usuarioubicacion', None)

        if ubicacion:
            diccionario_datos = {
                "longitud": ubicacion.longitude,
                "latitud": ubicacion.latitude,
                "colonia": ubicacion.colonia,
                "calle": ubicacion.calle,
                "codigo_postal": ubicacion.codigo_postal
            }
        else:
            diccionario_datos = {
                "longitud": None,
                "latitud": None,
                "colonia": None,
                "calle": None,
                "codigo_postal": None
            }

        return Response(diccionario_datos, status=status.HTTP_200_OK)


# def guardar_reporte():
#     try:
#         data = json.loads(request.body)

#         usuario = data.get("usuario")
#         fecha_pub = data.get("fecha")
#         texto = data.get("texto")
#         titulo = data.get("titulo")

#         if not usuario or texto or titulo is None:

#             return JsonResponse(
#                 {"error": "usuario, imagen, texto y titulo son obligatorios"},
#                 status=400
#             )

#         reporte = ReporteGenerado.objects.create(
#             user=usuario,
#             fecha_publicado=fecha_pub,
#             texto=texto,
#             titulo_reporte=titulo
#         )

#         return JsonResponse({
#             "mensaje": "Reporte generado correctamente"
#         }, status=201)

#     except (json.JSONDecodeError, TypeError, ValueError):
#         return JsonResponse(
#             {"error": "JSON inválido"},
#             status=400
#         )


class GuardarReporte(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # 1. Verificar si el usuario tiene ubicación asignada en la BD
        if not hasattr(request.user, 'ubicacion'):
            return Response(
                {
                    "requiere_ubicacion": True,
                    "mensaje": "Debes registrar tu ubicación antes de publicar un reporte."
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        
        titulo = request.data.get("titulo")
        texto = request.data.get("texto")
        imagen_base64 = request.data.get("imagen")


        colonia = request.user.ubicacion.colonia
        calle = request.user.ubicacion.calle
        codigo_postal = request.user.ubicacion.codigo_postal
        
        if not imagen_base64:
            return Response({"mensaje": "La imagen es obligatoria."}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Decodificar la imagen Base64
        if ';base64,' in imagen_base64:
            formato, cadena_img = imagen_base64.split(';base64,')
            ext = formato.split('/')[-1]
        else:
            cadena_img = imagen_base64
            ext = 'jpg'

        try:
            datos_imagen = base64.b64decode(cadena_img)
            nombre_archivo = f"reporte_{uuid.uuid4().hex[:8]}.{ext}"
            archivo_imagen = ContentFile(datos_imagen, name=nombre_archivo)
        except Exception as e:
            return Response({"mensaje": "Error procesando la imagen."}, status=status.HTTP_400_BAD_REQUEST)

        # # Generamos un nombre aleatorio único para el archivo (ej. reporte_a1b2c3d4.png)
        # nombre_archivo = f"reporte_{uuid.uuid4().hex[:8]}.{ext}"

        # Creamos el archivo compatible con Django
        archivo_imagen = ContentFile(datos_imagen, name=nombre_archivo)

        ReporteGenerado.objects.create(
            user=request.user,
            texto=texto,
            titulo_reporte=titulo,
            colonia=colonia,
            calle=calle,
            codigo_postal=codigo_postal,
            imagen=archivo_imagen,
        )

        return Response("Ok", status=status.HTTP_201_CREATED)


"""Recupera todos los reportes generados y los devuelve en un formato JSON"""


class MostrarReportes(APIView):
    def get(self, request):

        lista_retornar = []
        reportes = ReporteGenerado.objects.all().order_by("-fecha_publicado")

        for reporte_actual in reportes:

            # host = request.get_host()
            # # Resultado: "127.0.0.1:8000"
            # # host = "10.175.6.177:8000"

            diccionario_reporte_actual = {
                "titulo": reporte_actual.titulo_reporte,
                "texto": reporte_actual.texto,
                "fechaPublicado": reporte_actual.fecha_publicado.strftime("%d/%b/%y %I:%M %p"),
                "usuario": reporte_actual.user.id,
                "nombreUsuario": reporte_actual.user.nombre,
                "id": reporte_actual.id,
                "calle": reporte_actual.calle,
                "imagen": reporte_actual.imagen.url if reporte_actual.imagen else None,

            }
            lista_retornar.append(diccionario_reporte_actual)
        return Response(lista_retornar, status=status.HTTP_200_OK)

class VermiPerfil(APIView):
    # Permite al usuario ver su perfil y la información asociada a él
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        usuario = request.user

        #verificar si tiene una ubicacion registrada
        try:
            ubicacion = usuario.ubicacion
            if not ubicacion:
                return Response(
                    {   
                        "requiere_ubicacion": True,
                        "mensaje": "Debe registrar una ubicación en el mapa antes de ver su perfil."
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ObjectDoesNotExist, AttributeError):
            return Response(
                {   
                    "requiere_ubicacion": True,
                    "mensaje": "Debe registrar una ubicación en el mapa antes de ver su perfil."
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        #obtener el historico de reportes del usuario
        reportes_usuario = ReporteGenerado.objects.filter(user=usuario).order_by("-fecha_publicado")

        historial_reportes = []
        for reporte in reportes_usuario:
            historial_reportes.append({
                "titulo": reporte.titulo_reporte,
                "imagen": request.build_absolute_uri(reporte.imagen.url)
                if reporte.imagen
                else None,
                "texto":reporte.texto,
                "fecha":reporte.fecha_publicado,
                "calle":reporte.calle,
           })


        #Obtenemos los datos base del usuario
        datos_perfil = {
            "nombre": getattr(usuario, "nombre", "Usuario"),
            "correo_electronico":getattr(usuario, "correo_electronico", "Sin correo"),
            "direccion": {
                "calle": usuario.ubicacion.calle,
                "codigo_postal": usuario.ubicacion.codigo_postal,
        },
        "reportes": historial_reportes
        }

        return Response(datos_perfil, status=status.HTTP_200_OK)

class UsuarioTieneUbicacion(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        
        usuario = request.user

        if hasattr(usuario, 'ubicacion'):

            tieneUbicacionUsuario = True

        else:
            tieneUbicacionUsuario = False

        # tiene_ubicacion = hasattr(usuario, 'ubicacion') and usuario.ubicacion is not None
        return Response({"tiene_ubicacion": tieneUbicacionUsuario}, status=status.HTTP_200_OK)
    

class UsuarioTieneUbicacionAlternativo(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        
        usuario = request.user

        # Buscando si en la tabla de ubicaciones hay filas para este usuario
        ubicacionesUsuario = UsuarioUbicacion.objects.filter(user = usuario)

        if ubicacionesUsuario.count() > 0:

            tieneUbicacionUsuario = True

        else:

            tieneUbicacionUsuario = False

        # tiene_ubicacion = hasattr(usuario, 'ubicacion') and usuario.ubicacion is not None
        return Response({"tiene_ubicacion": tieneUbicacionUsuario}, status=status.HTTP_200_OK)

# class UsuarioTieneReportes(APIView):

#     parser_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]

#     def get(self, request):

#         usuario = request.user

#         reportesUsuario = ReporteGenerado.objects.filter(user = usuario)

#         if reportesUsuario.count() > 0:

#             tieneReportesUsuario = True

#         else:

#             tieneReportesUsuario = False
#         return Response({"tiene_reporte": tieneReportesUsuario}, status=status.HTTP_200_OK)
        

class EmitirAlerta(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1. Seguridad en Backend: Validamos que el Token corresponda a un chofer
        if 'matamoros.limpio' not in request.user.correo_electronico.lower():
            return Response(
                {"error": "Acceso denegado. Esta acción requiere credenciales de chofer."},
                status=status.HTTP_403_FORBIDDEN
            )

        codigo_postal = request.data.get("codigo_postal")
        incidencia = request.data.get("incidencia")
        mensaje = request.data.get("mensaje", "Retraso en la ruta.")

        # Guardamos la alerta en la base de datos
        AlertaChofer.objects.create(
            codigo_postal=codigo_postal,
            incidencia=incidencia,
            mensaje=mensaje
        )

        usuarios_afectados = UsuarioUbicacion.objects.filter(codigo_postal=codigo_postal).count()

        return Response({
            "status": "OK",
            "notificados": usuarios_afectados,
            "mensaje": f"Alerta procesada para el CP {codigo_postal}"
        }, status=status.HTTP_200_OK)

class ConsultarAlertas(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Buscamos el CP del ciudadano que está preguntando
            ubicacion = UsuarioUbicacion.objects.get(user=request.user)
            cp_usuario = ubicacion.codigo_postal
            
            # Buscamos la alerta más reciente para su CP que siga activa
            alerta = AlertaChofer.objects.filter(codigo_postal=cp_usuario, activa=True).order_by('-fecha_emision').first()

            if alerta:
                return Response({
                    "hay_alerta": True,
                    "incidencia": alerta.incidencia,
                    "mensaje": alerta.mensaje
                }, status=status.HTTP_200_OK)
            
        except UsuarioUbicacion.DoesNotExist:
            pass
            
        return Response({"hay_alerta": False}, status=status.HTTP_200_OK)

class ObtenerRutasCamion(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    def get(self, request):

        lista_ruta = []
        rutas = Ruta.objects.all()

        for ruta in rutas:
            diccionario_ruta_actual = {
                "id_ruta" : ruta.id_ruta,
                "mombre_ruta": ruta.nombre_ruta,
                "hora_inicio": ruta.hora_inicio,
                "hora_final": ruta.hora_final,
                "centro_mapa": ruta.centro_mapa,
                "ruta_coordenadas": ruta.rutas_coordenadas,
            }
            lista_ruta.append(diccionario_ruta_actual)
        return Response({"lista_ruta":lista_ruta}, status=status.HTTP_200_OK)

class ObtenerUbicacionCamion(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            chofer = Usuario.objects.filter(correo_electronico__icontains='matamoros.limpio').first()
            if chofer and hasattr(chofer, 'ubicacion'):
                return Response({
                    "latitud": chofer.ubicacion.latitude,
                    "longitud": chofer.ubicacion.longitude
                }, status=status.HTTP_200_OK)
        except Exception as e:
            pass

        return Response({"latitud":None, "longitud":None}, status=status.HTTP_200_OK)

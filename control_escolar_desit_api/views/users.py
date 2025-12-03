from django.db.models import *
from django.db import transaction
from control_escolar_desit_api.serializers import UserSerializer
from control_escolar_desit_api.serializers import *
from control_escolar_desit_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
import json

class AdminAll(generics.CreateAPIView):
    #esta funcion es esencial para todo donde se requiera autorizacion de inicio de sesion "token"
    permission_classes = (permissions.IsAuthenticated,)

    #hacemos la peticion GET
    def get(self, request, *args, **kwargs):
        user = request.user
        
        #creamos el objeto admin para hacer la consulta
        admin = Administradores.objects.filter(user__is_active = 1).order_by("id")
        lista = AdminSerializer(admin, many = True).data
        return Response(lista, 200)

class AdminView(generics.CreateAPIView):
    # Permisos por método (sobrescribe el comportamiento default)
    # Verifica que el usuario esté autenticado para las peticiones GET, PUT y DELETE
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []  # POST no requiere autenticación

    #Obtiene el usuario por ID
    def get(self, request, *args, **kwargs):
        admin = get_object_or_404(Administradores, id = request.GET.get("id"))
        admin = AdminSerializer(admin, many=False).data
        # Si todo es correcto, regresamos la información
        return Response(admin, 200)

    #registra nuevos usuarios
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        #Serializamos los datos del administrador para volverlo otra vez JSON
        user = UserSerializer(data = request.data)

        user = UserSerializer(data=request.data)
        if user.is_valid():
            #Grabar datos de administrador
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']

            #valida si existe el usuario o el email registrados
            existing_user = User.objects.filter(email=email).first()

            #si el usuario existe recoge los datos si no manda un error de bad request
            if existing_user:
                return Response({"message":"Username "+email+", is already taken"},400)

            #se reasignan las datos que cachamos en el serializador
            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)

            #se guarda la contraseña y se cifra con set_password
            user.save()
            user.set_password(password)
            user.save()

            #se verifica en que grupo esta el usuario y se guarda en la tabla
            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            group.save()


            #se guardan los datos adicionales del administrador
            admin = Administradores.objects.create(user = user,
                                                   clave_admin = request.data["clave_admin"],
                                                   telefono = request.data["telefono"],
                                                   rfc = request.data["rfc"].upper(),
                                                   edad = request.data["edad"],
                                                   ocupacion = request.data["ocupacion"])
            admin.save()

            #si los datos son correctos se manda un mensaje de creacion_id
            return Response({"admin_created_id":admin.id }, 201)

        #si no se pueden validar los datos, se manda un error de bad request
        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)

    # Actualizar datos del administrador
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        permission_classes = (permissions.IsAuthenticated,)

        # Primero obtenemos el administrador a actualizar
        admin = get_object_or_404(Administradores, id=request.data["id"])
        admin.clave_admin = request.data["clave_admin"]
        admin.telefono = request.data["telefono"]
        admin.rfc = request.data["rfc"]
        admin.edad = request.data["edad"]
        admin.ocupacion = request.data["ocupacion"]
        admin.save()
        
        # Actualizamos los datos del usuario asociado (tabla auth_user de Django)
        user = admin.user
        user.first_name = request.data["first_name"]
        user.last_name = request.data["last_name"]
        user.save()
        
        return Response({"message": "Administrador actualizado correctamente", "admin": AdminSerializer(admin).data}, 200)
        # return Response(user,200)

   #Eliminar administrador con delete (Borrar realmente)
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            admin = get_object_or_404(Administradores, id=request.GET.get("id"))
            admin.user.delete()
            return Response({"details":"Administrador eliminado"},200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"},400)

        #Eliminar administrador (Desactivar usuario)
        # @transaction.atomic
        # def delete(self, request, *args, **kwargs):
        #     id_admin = kwargs.get('id_admin', None)
        #     if id_admin:
        #         try:
        #             admin = Administradores.objects.get(id=id_admin)
        #             user = admin.user
        #             user.is_active = 0
        #             user.save()
        #             return Response({"message":"Administrador con ID "+str(id_admin)+" eliminado correctamente."},200)
        #         except Administradores.DoesNotExist:
        #             return Response({"message":"Administrador con ID "+str(id_admin)+" no encontrado."},404)
        #     return Response({"message":"Se necesita el ID del administrador."},400)     


class TotalUsers(generics.CreateAPIView):
    #Contar el total de cada tipo de usuarios
    def get(self, request, *args, **kwargs):
        # TOTAL ADMINISTRADORES
        admin_qs = Administradores.objects.filter(user__is_active=True)
        total_admins = admin_qs.count()

        # TOTAL MAESTROS
        maestros_qs = Maestros.objects.filter(user__is_active=True)
        lista_maestros = MaestroSerializer(maestros_qs, many=True).data

        # Convertir materias_json solo si existen maestros
        for maestro in lista_maestros:
            try:
                maestro["materias_json"] = json.loads(maestro["materias_json"])
            except Exception:
                maestro["materias_json"] = []  # fallback seguro

        total_maestros = maestros_qs.count()

        # TOTAL ALUMNOS
        alumnos_qs = Alumnos.objects.filter(user__is_active=True)
        total_alumnos = alumnos_qs.count()

        # Respuesta final SIEMPRE válida
        return Response(
            {
                "admins": total_admins,
                "maestros": total_maestros,
                "alumnos": total_alumnos
            },
            status=200
        )
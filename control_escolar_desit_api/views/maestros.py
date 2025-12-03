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
import json
from django.shortcuts import get_object_or_404

class MaestrosAll(generics.CreateAPIView):
    # Necesita permisos de autenticación de usuario para poder acceder a la petición
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        #Aqui filtramos a todos los usuarios que esten activos y los ordena
        maestros = Maestros.objects.filter(user__is_active=1).order_by("id")

        #obtiene los objetos de la base de datos primero y luego los serializa
        lista = MaestroSerializer(maestros, many=True).data
        
        #aqui se vuelve a convertir a json el arreglo de materias
        for maestro in lista:
            if isinstance(maestro, dict) and "materias_json" in maestro:
                try:
                    # Convierte el string JSON a un objeto 
                    maestro["materias_json"] = json.loads(maestro["materias_json"])
                except Exception:
                    # Si falla asigna una lista vacía
                    maestro["materias_json"] = []
                    
        return Response(lista, 200)


class MaestrosView(generics.CreateAPIView):
    # Permisos por método (sobrescribe el comportamiento default)
    # Verifica que el usuario esté autenticado para las peticiones GET, PUT y DELETE
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []  # POST no requiere autenticación

    #Obtiene el maestro por ID
    def get(self, request, *args, **kwargs):
        # Asumiendo que tu modelo se llama 'Maestros'
        maestro = get_object_or_404(Maestros, id = request.GET.get("id"))
        # Asumiendo que tu serializador se llama 'MaestroSerializer'
        maestro = MaestroSerializer(maestro, many=False).data
        # Si todo es correcto, regresamos la información
        return Response(maestro, 200)
    
    #registro para un nuevo usuario maestro
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        #Serializamos los datos del administrador para volverlo otra vez JSON
        user = UserSerializer(data=request.data)
        if user.is_valid():
            # Datos del maestro
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']

            #valida si existe el usuario o el email registrados
            existing_user = User.objects.filter(email=email).first()

            #si el usuario existe recoge los datos si no manda un error de bad request
            if existing_user:
                return Response({"message": f"Username {email}, is already taken"}, 400)

            #se reasignan las datos que cachamos en el serializador
            user = User.objects.create(username=email,
                                       email=email,
                                       first_name=first_name,
                                       last_name=last_name,
                                       is_active=1)
            
            #se guarda la contraseña y se cifra con set_password
            user.save()
            user.set_password(password)
            user.save()

            #se verifica en que grupo esta el usuario y se guarda en la tabla
            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            group.save()

            #se guardan los datos adicionales del maestro
            maestro = Maestros.objects.create(user=user,
                                              id_trabajador=request.data["id_trabajador"],
                                              fecha_nacimiento=request.data["fecha_nacimiento"], 
                                              telefono=request.data["telefono"],
                                              rfc = request.data["rfc"].upper(),
                                              cubiculo=request.data["cubiculo"],               
                                              area_investigacion=request.data["area_investigacion"], 
                                              materias_json=request.data["materias_json"])     
            maestro.save()

            #si los datos son correctos se manda un mensaje de creacion_id
            return Response({"maestro_created_id": maestro.id}, 201)

        #si no se pueden validar los datos, se manda un error de bad request
        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
    
     # Actualizar datos del maestro
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        permission_classes = (permissions.IsAuthenticated,)

        # Primero obtenemos el maestro a actualizar
        maestro = get_object_or_404(Maestros, id=request.data["id"])
        
        # Actualizamos los campos específicos de Maestro
        maestro.id_trabajador = request.data["id_trabajador"]
        maestro.fecha_nacimiento = request.data["fecha_nacimiento"]
        maestro.telefono = request.data["telefono"]
        maestro.rfc = request.data["rfc"]
        maestro.cubiculo = request.data["cubiculo"]
        maestro.area_investigacion = request.data["area_investigacion"]
        maestro.save()
        
        # Actualizamos los datos del usuario asociado (tabla auth_user)
        user = maestro.user
        user.first_name = request.data["first_name"]
        user.last_name = request.data["last_name"]
        user.save()
        
        # Asumo que tu serializador se llama 'MaestroSerializer'
        return Response({"message": "Maestro actualizado correctamente", "maestro": MaestroSerializer(maestro).data}, 200)
        # return Response(user,200)

    #Eliminar maestro con delete (Borrar realmente)
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            maestro = get_object_or_404(Maestros, id=request.GET.get("id"))
            maestro.user.delete()
            return Response({"details":"Maestro eliminado"},200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"},400)

        #Eliminar maestro (Desactivar usuario)
        # @transaction.atomic
        # def delete(self, request, *args, **kwargs):
        #     id_maestro = kwargs.get('id_maestro', None)
        #     if id_maestro:
        #         try:
        #             maestro = Maestros.objects.get(id=id_maestro)
        #             user = maestro.user
        #             user.is_active = 0
        #             user.save()
        #             return Response({"message":"Maestro con ID "+str(id_maestro)+" eliminado correctamente."},200)
        #         except Maestros.DoesNotExist:
        #             return Response({"message":"Maestro con ID "+str(id_maestro)+" no encontrado."},404)
        #     return Response({"message":"Se necesita el ID del maestro."},400)   

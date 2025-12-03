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

class AlumnosAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
            #Filtramos a todos los alumnos que esten activos y los ordena
            alumnos = Alumnos.objects.filter(user__is_active=1).order_by("id")

            #Obtiene los objetos de la base de datos y los serializa
            lista = AlumnoSerializer(alumnos, many=True).data

            #Retornamos la lista completa de alumnos
            return Response(lista, 200)


class AlumnosView(generics.CreateAPIView):
    # Permisos por método (sobrescribe el comportamiento default)
    # Verifica que el usuario esté autenticado para las peticiones GET, PUT y DELETE
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []  # POST no requiere autenticación
    
    #Obtiene el alumno por ID
    def get(self, request, *args, **kwargs):
        # Asumiendo que tu modelo se llama 'Alumnos'
        alumno = get_object_or_404(Alumnos, id = request.GET.get("id"))
        # Asumiendo que tu serializador se llama 'AlumnoSerializer'
        alumno = AlumnoSerializer(alumno, many=False).data
        # Si todo es correcto, regresamos la información
        return Response(alumno, 200)

    #registra nuevos usuarios
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        #Serializamos los datos del administrador para volverlo otra vez JSON
        user = UserSerializer(data=request.data)
        if user.is_valid():
            # Datos del alumno
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

            #se guardan los datos adicionales del alumno
            alumno = Alumnos.objects.create(user=user,
                                            matricula=request.data["matricula"],
                                            fecha_nacimiento=request.data["fecha_nacimiento"],
                                            curp=request.data["curp"],                         
                                            rfc=request.data["rfc"].upper(),
                                            edad=request.data["edad"],
                                            telefono=request.data["telefono"],
                                            ocupacion=request.data["ocupacion"])
            alumno.save()

            #si los datos son correctos se manda un mensaje de creacion_id
            return Response({"alumno_created_id": alumno.id}, 201)

        #si no se pueden validar los datos, se manda un error de bad request
        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Actualizar datos del alumno
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        permission_classes = (permissions.IsAuthenticated,)

        # Primero obtenemos el alumno a actualizar
        alumno = get_object_or_404(Alumnos, id=request.data["id"])
        
        # Actualizamos los campos específicos de Alumno
        alumno.matricula = request.data["matricula"]
        alumno.fecha_nacimiento = request.data["fecha_nacimiento"]
        alumno.telefono = request.data["telefono"]
        alumno.curp = request.data["curp"]
        alumno.rfc = request.data["rfc"]
        alumno.save()
        
        # Actualizamos los datos del usuario asociado (tabla auth_user)
        user = alumno.user
        user.first_name = request.data["first_name"]
        user.last_name = request.data["last_name"]
        user.save()
        
        # Asumo que tu serializador se llama 'AlumnoSerializer'
        return Response({"message": "Alumno actualizado correctamente", "alumno": AlumnoSerializer(alumno).data}, 200)
        # return Response(user,200)

    #Eliminar alumno con delete (Borrar realmente)
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            alumno = get_object_or_404(Alumnos, id=request.GET.get("id"))
            alumno.user.delete()
            return Response({"details":"Alumno eliminado"},200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"},400)

        #Eliminar alumno (Desactivar usuario)
        # @transaction.atomic
        # def delete(self, request, *args, **kwargs):
        #     id_alumno = kwargs.get('id_alumno', None)
        #     if id_alumno:
        #         try:
        #             alumno = Alumnos.objects.get(id=id_alumno)
        #             user = alumno.user
        #             user.is_active = 0
        #             user.save()
        #             return Response({"message":"Alumno con ID "+str(id_alumno)+" eliminado correctamente."},200)
        #         except Alumnos.DoesNotExist:
        #             return Response({"message":"Alumno con ID "+str(id_alumno)+" no encontrado."},404)
        #     return Response({"message":"Se necesita el ID del alumno."},400)

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *

#esta clase es la que trae los datos de la tabla aut_user
class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only = True)
    first_name = serializers.CharField(required = True)
    last_name = serializers.CharField(required = True)
    email = serializers.CharField(required = True)

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email")

# Serializamos al usuario para obtener los datos de autenticacion
class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    #con la clase meta, obtenemos ya todos los datos
    class Meta:
        model = Administradores
        fields = "__all__"

#TODO: Declarar los serializadores para los perfiles de alumnos y maestros

class MaestroSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Maestros
        fields = "__all__"


#serializador de alumnos
class AlumnoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Alumnos
        fields = "__all__"

#serializador de materias
class MateriasSerializer(serializers.ModelSerializer):
    maestro_data = MaestroSerializer(source='profesor',read_only=True,  required=False, allow_null=True)

    class Meta:
        model = Materias
        fields = "__all__"

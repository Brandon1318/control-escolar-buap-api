from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication

class BearerTokenAuthentication(TokenAuthentication):
    keyword = "Bearer"

#tabla para el formulario de administradores
class Administradores(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    clave_admin = models.CharField(max_length = 255, null=True, blank=True)
    telefono = models.CharField(max_length = 255, null=True, blank=True)
    rfc = models.CharField(max_length = 255, null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    ocupacion = models.CharField(max_length = 255, null=True, blank=True)
    #utilizamos creation para llevar un control de las fechas de registros
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    #sirve para mostrar los usuarios actualizados
    update = models.DateTimeField(null=True, blank=True)

#esta funcion manda los datos del usuario
    def __str__(self):
        return f"Perfil de {self.user.first_name} {self.user.last_name}"

# TODO: Agregar perfiles para estudiantes y profesores

# Tabla para alumnos
class Alumnos(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='alumno',  null=True, blank=True)
    matricula = models.CharField(max_length=50, unique=True, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    curp = models.CharField(max_length=18, unique=True, null=True, blank=True)
    rfc = models.CharField(max_length=13, unique=True, null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    ocupacion = models.CharField(max_length=255, null=True, blank=True)
    #utilizamos creation para llevar un control de las fechas de registros
    creation = models.DateTimeField(auto_now_add=True)
    #sirve para mostrar los usuarios actualizados
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.matricula}"

# Tabla para maestros
class Maestros(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='maestro', null=True, blank=True)
    id_trabajador = models.CharField(max_length=50, unique=True, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    rfc = models.CharField(max_length=13, unique=True, null=True, blank=True)
    cubiculo = models.CharField(max_length=100, null=True, blank=True)
    area_investigacion = models.CharField(max_length=255, null=True, blank=True)
    #aqui guardamos la lista de materias
    materias_json = models.JSONField(null=True, blank=True) 
    #utilizamos creation para llevar un control de las fechas de registros
    creation = models.DateTimeField(auto_now_add=True)
    #sirve para mostrar los usuarios actualizados
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.id_trabajador}"

# Tabla para Materias
class Materias(models.Model):
    id = models.BigAutoField(primary_key=True)
    nrc = models.CharField(max_length=10, unique=True, null=True, blank=True)
    nombre = models.CharField(max_length=255, null=True, blank=True)
    seccion = models.CharField(max_length=5, null=True, blank=True)
    dias = models.JSONField(null=True, blank=True, default=list) 
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_final = models.TimeField(null=True, blank=True)
    salon = models.CharField(max_length=50, null=True, blank=True)
    programa_educativo = models.CharField(max_length=255, null=True, blank=True)
    creditos = models.IntegerField(null=True, blank=True)
    #relacion para conectar con la tabla maestros
    profesor = models.ForeignKey(Maestros, on_delete=models.CASCADE, related_name='materias_impartidas', null=True, blank=True)
    #utilizamos creation para llevar un control de las fechas de registros
    creation = models.DateTimeField(auto_now_add=True)
    #sirve para mostrar los usuarios actualizados
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} - {self.nrc}"
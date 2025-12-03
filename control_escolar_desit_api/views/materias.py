from django.db.models import *
from django.db import transaction
from control_escolar_desit_api.serializers import MateriasSerializer
from control_escolar_desit_api.models import Materias, Maestros
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class MateriasAll(generics.CreateAPIView):
    # Necesita permisos de autenticación de usuario
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # Solución: Asegurar que se obtengan TODAS las materias, sin filtros de usuario
        materias = Materias.objects.all().order_by("id")

        # Obtiene los objetos y los serializa
        lista = MateriasSerializer(materias, many=True).data
        
        return Response(lista, 200)


class MateriasView(generics.CreateAPIView):
    # Permisos por método
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []

    # Obtiene la materia por ID
    def get(self, request, *args, **kwargs):
        materia = get_object_or_404(Materias, id=request.GET.get("id"))
        materia_data = MateriasSerializer(materia, many=False).data
        return Response(materia_data, 200)
    
    # Registro de una nueva materia
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = MateriasSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                profesor_instancia = Maestros.objects.get(id=request.data["profesor"])
            except Maestros.DoesNotExist:
                return Response({"message": "El profesor seleccionado no existe"}, 400)

            materia = Materias.objects.create(
                nrc=request.data["nrc"],
                nombre=request.data["nombre"],
                seccion=request.data["seccion"],
                dias=request.data["dias"],
                hora_inicio=request.data["hora_inicio"],
                hora_final=request.data["hora_final"],
                salon=request.data["salon"],
                programa_educativo=request.data["programa_educativo"],
                creditos=request.data["creditos"],
                profesor=profesor_instancia
            )
            
            materia.save()

            return Response({"materia_created_id": materia.id}, 201)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Actualizar datos de la materia
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        materia = get_object_or_404(Materias, id=request.data["id"])
        
        if "profesor" in request.data:
            try:
                profesor_instancia = Maestros.objects.get(id=request.data["profesor"])
                materia.profesor = profesor_instancia
            except Maestros.DoesNotExist:
                return Response({"message": "El profesor seleccionado no existe"}, 400)

        materia.nrc = request.data["nrc"]
        materia.nombre = request.data["nombre"]
        materia.seccion = request.data["seccion"]
        materia.dias = request.data["dias"]
        materia.hora_inicio = request.data["hora_inicio"]
        materia.hora_final = request.data["hora_final"]
        materia.salon = request.data["salon"]
        materia.programa_educativo = request.data["programa_educativo"]
        materia.creditos = request.data["creditos"]
        
        materia.save()
        
        return Response({"message": "Materia actualizada correctamente", "materia": MateriasSerializer(materia).data}, 200)

    # Eliminar materia
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            materia = get_object_or_404(Materias, id=request.GET.get("id"))
            materia.delete()
            return Response({"details": "Materia eliminada correctamente"}, 200)
        except Exception as e:
            return Response({"details": "Algo pasó al eliminar"}, 400)
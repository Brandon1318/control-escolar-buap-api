from django.db.models import *
from control_escolar_desit_api.serializers import *
from control_escolar_desit_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                        context={'request': request})

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user.is_active:

            #se obtienen el perfil y los roles del usuario
            roles = user.groups.all()
            role_names = []

            #se verifica si los usuarios tienen un perfil adecuado
            for role in roles:
                role_names.append(role.name)

            #si es solo un rol especifico se asgina el elemento 0
            role_names = role_names [0].lower()

            #esta funcion genera los tokens para el inicio de sesion
            token, created = Token.objects.get_or_create(user=user)

            #verifica que tipo de usuarios son los que inician sesion
            if role_names == 'alumno':
                alumno = Alumnos.objects.filter(user=user).first()
                alumno = AlumnoSerializer(alumno).data
                alumno ["token"] = token.key
                alumno ["rol"] = "alumno"
                return Response (alumno,200)
            
            if role_names == 'maestro':
                maestro = Maestros.objects.filter(user=user).first()
                maestro = MaestroSerializer(maestro).data
                maestro ["token"] = token.key
                maestro ["rol"] = "maestro"
                return Response (maestro,200)
            
            if role_names == 'administrador':
                user = UserSerializer(user, many=False).data
                user ['token'] = token.key
                user ["rol"] = "administrador"
                return Response (user,200)
            
            else: 
                #el error 403 significa que no hay autenticacion
                return Response({"details" : "Forbidden"}, 403)
                pass
        return Response({}, status.HTTP_403_FORBIDDEN)


class Logout(generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):

        print("logout")
        user = request.user
        print(str(user))
        if user.is_active:
            token = Token.objects.get(user=user)
            token.delete()

            return Response({'logout':True})


        return Response({'logout': False})


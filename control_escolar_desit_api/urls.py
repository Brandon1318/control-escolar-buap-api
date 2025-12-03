from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views.bootstrap import VersionView
from control_escolar_desit_api.views import users
from control_escolar_desit_api.views import auth
from control_escolar_desit_api.views import bootstrap
from control_escolar_desit_api.views import alumnos
from control_escolar_desit_api.views import maestros
from control_escolar_desit_api.views import materias

#definimos las EndPoints para las conexiones front con back
urlpatterns = [
    #URL Admin
    path('admin/', users.AdminView.as_view()),
    #URL data
    path('lista-admins/', users.AdminAll.as_view()),
    #Edit Admim
    #path('admins-edits/', users.AdminViewEdit.as_view()),

    # Alumnos
    path('alumno/', alumnos.AlumnosView.as_view()),
    path('lista-alumnos/', alumnos.AlumnosAll.as_view()),

    # Maestros
    path('maestro/', maestros.MaestrosView.as_view()),
    path('lista-maestros/', maestros.MaestrosAll.as_view()),

    #total de users
    path('total-usuarios/', users.TotalUsers.as_view()),

    #materias
    path('materia/', materias.MateriasView.as_view()),      
    path('lista-materias/', materias.MateriasAll.as_view()),

    #login
    path('login/', auth.CustomAuthToken.as_view()),

    #logout
    path('logout/', auth.Logout.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

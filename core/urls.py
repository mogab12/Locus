from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('disciplinas/', views.disciplinas, name='disciplinas'),
    path('eventos/', views.eventos, name='eventos'),
    path('notificacoes/', views.notificacoes, name='notificacoes'),
    path('grade-horaria/', views.grade_horaria, name='grade_horaria'),
]
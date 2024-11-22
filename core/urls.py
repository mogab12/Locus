from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('disciplinas/', views.disciplinas, name='disciplinas'),
    path('eventos/', views.eventos, name='eventos'),
    path('notificacoes/', views.notificacoes, name='notificacoes'),
    path('grade-horaria/', views.grade_horaria, name='grade_horaria'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('disciplinas/adicionar_disciplinas', views.adicionar_disciplinas, name='adicionar_disciplinas'),
    path('disciplinas/remover_disciplinas', views.remover_disciplinas, name='remover_disciplinas'),
    path('disciplinas/<int:disciplina_id>/', views.detalhe_disciplina, name='detalhe_disciplina'),
]
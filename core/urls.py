from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('disciplinas/', views.disciplinas, name='disciplinas'),
    path('eventos/', views.lista_eventos, name='lista_eventos'),
    path('eventos/novo', views.criar_evento, name='criar_evento'),
    path('eventos/<int:evento_id>/', views.detalhe_evento, name='detalhe_evento'),
    path('eventos/<int:evento_id>/editar/', views.editar_evento, name='editar_evento'),
    path('eventos/<int:evento_id>/deletar/', views.deletar_evento, name='deletar_evento'),
    path('notificacoes/', views.notificacoes, name='notificacoes'),
    path('grade-horaria/', views.grade_horaria, name='grade_horaria'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('disciplinas/adicionar_disciplinas', views.adicionar_disciplinas, name='adicionar_disciplinas'),
    path('disciplinas/remover_disciplinas', views.remover_disciplinas, name='remover_disciplinas'),
    path('disciplinas/<int:disciplina_id>/', views.detalhe_disciplina, name='detalhe_disciplina'),
    path('disciplinas/<int:disciplina_id>/forum/', views.lista_topicos, name='lista_topicos'),
    path('disciplinas/topico/<int:topico_id>/', views.detalhe_topico, name='detalhe_topico'),
    path('disciplinas/<int:disciplina_id>/forum/novo/', views.novo_topico, name='novo_topico'),
    path('topico/<int:topico_id>/editar/', views.editar_topico, name='editar_topico'),
    path('topico/<int:topico_id>/remover/', views.remover_topico, name='remover_topico'),
    path('postagem/<int:postagem_id>/remover/', views.remover_postagem, name='remover_postagem'),
    path('perfil/<int:user_id>/', views.view_profile, name='view_profile'),
]
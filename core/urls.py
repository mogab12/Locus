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
    path('adicionar_local_evento/', views.adicionar_local_evento, name='adicionar_local_evento'),
    path('eventos/<int:evento_id>/', views.detalhe_evento, name='detalhe_evento'),
    path('eventos/<int:evento_id>/editar/', views.editar_evento, name='editar_evento'),
    path('eventos/<int:evento_id>/deletar/', views.deletar_evento, name='deletar_evento'),
    path('evento/<int:evento_id>/toggle/', views.toggle_interesse, name='toggle_interesse'),
    path('evento/<int:evento_id>/ver-local/', views.ver_local_evento, name='ver_local_evento'),
    path('notificacoes/', views.notificacoes, name='notificacoes'),
    path('notificacoes/criar/', views.criar_notificacao, name='criar_notificacao'),
    path('notificacoes/minhas/', views.minhas_notificacoes, name='minhas_notificacoes'),
    path('notificacoes/<int:notificacao_id>/editar/', views.editar_notificacao, name='editar_notificacao'),
    path('notificacoes/<int:notificacao_id>/remover/', views.remover_notificacao, name='remover_notificacao'),
    path('notificacoes/<int:notificacao_id>/excluir/', views.excluir_notificacao_recebida, name='excluir_notificacao_recebida'),
    path('grade-horaria/', views.grade_horaria, name='grade_horaria'),
    path('grade-horaria/adicionar/', views.adicionar_horario_grade, name='adicionar_horario_grade'),
    path('grade-horaria/remover/<int:horario_id>/', views.remover_horario_grade, name='remover_horario_grade'),
    path('grade-horaria/editar/<int:horario_id>/', views.editar_horario_grade, name='editar_horario_grade'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('disciplinas/adicionar_disciplinas', views.adicionar_disciplinas, name='adicionar_disciplinas'),
    path('disciplinas/remover_disciplinas', views.remover_disciplinas, name='remover_disciplinas'),
    path('disciplinas/<int:disciplina_id>/', views.detalhe_disciplina, name='detalhe_disciplina'),
    path('disciplina/<int:disciplina_id>/adicionar_local/', views.adicionar_local, name='adicionar_local'),
    path('get_salas/<int:predio_id>/', views.get_salas, name='get_salas'),
    path('disciplinas/<int:disciplina_id>/forum/', views.lista_topicos, name='lista_topicos'),
    path('disciplinas/topico/<int:topico_id>/', views.detalhe_topico, name='detalhe_topico'),
    path('disciplinas/<int:disciplina_id>/forum/novo/', views.novo_topico, name='novo_topico'),
    path('topico/<int:topico_id>/editar/', views.editar_topico, name='editar_topico'),
    path('topico/<int:topico_id>/remover/', views.remover_topico, name='remover_topico'),
    path('postagem/<int:postagem_id>/remover/', views.remover_postagem, name='remover_postagem'),
    path('perfil/<int:user_id>/', views.view_profile, name='view_profile'),
    path('search/', views.search_results, name='search_results'),
    path('mapa/<int:mapa_id>/',views.mapa_detalhe,name='mapa_detalhe'),
    path('mapa/<int:mapa_id>/2/',views.mudar_andar,name='mudar_andar'),
]
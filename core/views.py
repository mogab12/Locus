from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model
from django.db.models import Q
from django.contrib import messages
from .forms import CustomUserCreationForm, UserProfileForm, NovoTopicoForm, NovaPostagemForm
from django.http import HttpResponseForbidden
from .models import Disciplina, UserDiscipline, Topico, Postagem, CustomUser, Evento, Notificacao
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from .forms import TopicoForm, EventoForm, NotificationForm





@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            if request.POST.get('clear_foto'):
                if request.user.foto:
                    request.user.foto.delete(save=False)
                request.user.foto = None
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'core/edit_profile.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'core/home.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'core/login.html', {'error': 'Credenciais inválidas'})
    return render(request, 'core/login.html')

@login_required
def home(request):
    return render(request, 'core/home.html')

@login_required
def disciplinas(request):
    if request.user.user_type not in ['aluno', 'representante', 'professor']:
        raise PermissionDenied

    user_disciplines = UserDiscipline.objects.filter(user=request.user).select_related('disciplina')
    return render(request, 'core/disciplinas.html', {'user_disciplines': user_disciplines})
@login_required
def remover_disciplinas(request):
    if request.user.user_type not in ['aluno', 'representante', 'professor']:
        raise PermissionDenied
    user_disciplines = UserDiscipline.objects.filter(user=request.user).select_related('disciplina')

    if request.method == 'POST':
        if 'remove' in request.POST:
            disciplina_id = request.POST.get('disciplina_id')
            UserDiscipline.objects.filter(user=request.user, disciplina_id=disciplina_id).delete()
            messages.success(request, 'Disciplina removida com sucesso!')

        elif 'remover_todas' in request.POST:
            UserDiscipline.objects.filter(user=request.user).delete()
            messages.success(request, 'Todas as disciplinas foram removidas.')

    return render(request, 'core/remover_disciplinas.html', {
        'user_disciplines': user_disciplines,
    })

@login_required
def adicionar_disciplinas(request):
    if request.user.user_type not in ['aluno', 'representante', 'professor']:
        raise PermissionDenied
    search_results = []
    query = request.GET.get('q', '')

    if request.method == 'POST':
        if 'add' in request.POST:
            # Adicionar disciplina selecionada ao usuário
            disciplina_id = request.POST.get('disciplina_id')
            disciplina = Disciplina.objects.get(id=disciplina_id)
            UserDiscipline.objects.get_or_create(user=request.user, disciplina=disciplina)
            messages.success(request, 'Disciplina adicionada com sucesso!')

        elif 'importar_obrigatorias' in request.POST:
            # Importar disciplinas obrigatórias
            curso = request.user.curso
            semestre = request.user.semestre
            obrigatorias = Disciplina.objects.filter(curso=curso, semestre=semestre, tipo='Obrigatória')
            for disciplina in obrigatorias:
                UserDiscipline.objects.get_or_create(user=request.user, disciplina=disciplina)
            messages.success(request, 'Disciplinas obrigatórias importadas com sucesso!')

    if query:
        all_results = Disciplina.objects.filter(
            Q(nome__icontains=query) | Q(codigo__icontains=query)
        )

        # Remover duplicatas com base no 'codigo'
        seen_codes = set()
        for disciplina in all_results:
            if disciplina.codigo not in seen_codes:
                search_results.append(disciplina)
                seen_codes.add(disciplina.codigo)

    return render(request, 'core/adicionar_disciplinas.html', {
        'search_results': search_results,
        'query': query,
    })

User = get_user_model()

@login_required
def detalhe_disciplina(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, id=disciplina_id)

    # Filtrar apenas os professores que têm a disciplina associada
    professores = User.objects.filter(
        user_type='professor',
        userdiscipline__disciplina=disciplina
    )

    return render(request, 'core/detalhe_disciplina.html', {'disciplina': disciplina, 'professores': professores})

@login_required
def lista_topicos(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, id=disciplina_id)
    topicos = Topico.objects.filter(disciplina=disciplina).order_by('-data_criacao')
    return render(request, 'core/lista_topicos.html', {'disciplina': disciplina, 'topicos': topicos})

@login_required
def detalhe_topico(request, topico_id):
    topico = get_object_or_404(Topico, id=topico_id)
    disciplina = topico.disciplina

    if request.method == 'POST':
        form = NovaPostagemForm(request.POST)
        if form.is_valid():
            postagem = form.save(commit=False)
            postagem.topico = topico
            postagem.criado_por = request.user
            postagem.save()

            alunos = UserDiscipline.objects.filter(disciplina=disciplina).select_related('user')
            destinatarios = [ud.user for ud in alunos]

            if destinatarios:
                notificacao = Notificacao.objects.create(
                    titulo=f"Nova Postagem no Tópico: {topico.titulo}",
                    mensagem=f"Uma nova postagem foi adicionada ao tópico '{topico.titulo}' na disciplina {disciplina.nome}.",
                    criador=request.user,
                    disciplina=disciplina,
                    # Supondo que você tenha um campo ForeignKey 'topico' na Notificacao
                    topico=topico  
                )
                notificacao.destinatarios.set(destinatarios)

            return redirect('detalhe_topico', topico_id=topico.id)
    else:
        form = NovaPostagemForm()

    return render(request, 'core/detalhe_topico.html', {'topico': topico, 'form': form})

@login_required
@login_required
def novo_topico(request, disciplina_id):
    if request.user.user_type not in ['representante', 'professor']:
        return HttpResponseForbidden("Você não tem permissão para criar um tópico.")

    disciplina = get_object_or_404(Disciplina, id=disciplina_id)

    if request.method == 'POST':
        form = NovoTopicoForm(request.POST)
        if form.is_valid():
            topico = form.save(commit=False)
            topico.disciplina = disciplina
            topico.criado_por = request.user
            topico.save()

            # Recupera todos os alunos associados à disciplina
            alunos = UserDiscipline.objects.filter(disciplina=disciplina).select_related('user')
            destinatarios = [ud.user for ud in alunos]

            # Criar notificação para todos os alunos da disciplina
            if destinatarios:
                notificacao = Notificacao.objects.create(
                    titulo=f"Novo Tópico Criado: {topico.titulo}",
                    mensagem=f"Um novo tópico '{topico.titulo}' foi criado na disciplina {disciplina.nome}.",
                    criador=request.user,
                    disciplina=disciplina,
                    topico=topico  # Passando a referência para o novo campo
                )
                notificacao.destinatarios.set(destinatarios)

            return redirect('lista_topicos', disciplina_id=disciplina.id)
    else:
        form = NovoTopicoForm()

    return render(request, 'core/novo_topico.html', {'disciplina': disciplina, 'form': form})

@login_required
def editar_topico(request, topico_id):
    topico = get_object_or_404(Topico, id=topico_id)

    if request.user.user_type not in ['representante', 'professor']:
        return HttpResponseForbidden("Você não tem permissão para editar este tópico.")

    if request.method == 'POST':
        form = TopicoForm(request.POST, instance=topico)
        if form.is_valid():
            form.save()
            return redirect('detalhe_topico', topico_id=topico.id)
    else:
        form = TopicoForm(instance=topico)

    return render(request, 'core/editar_topico.html', {'form': form, 'topico': topico})
@login_required
def remover_topico(request, topico_id):
    topico = get_object_or_404(Topico, id=topico_id)

    # Verificar se o usuário é representante ou professor
    if request.user.user_type not in ['representante', 'professor']:
        return HttpResponseForbidden("Você não tem permissão para remover este tópico.")
    
    if request.method == 'POST':
        topico.delete()
        return redirect('lista_topicos', disciplina_id=topico.disciplina.id)

    return render(request, 'core/remover_topico_confirmacao.html', {'topico': topico})

@login_required
def remover_postagem(request, postagem_id):
    postagem = get_object_or_404(Postagem, id=postagem_id)
    topico = postagem.topico  # Obtenha o tópico associado à postagem

    # Verificar se o usuário é representante ou professor
    if request.user.user_type not in ['representante', 'professor']:
        return HttpResponseForbidden("Você não tem permissão para remover esta postagem.")
    
    if request.method == 'POST':
        postagem.delete()
        return redirect('detalhe_topico', topico_id=topico.id)

    return render(request, 'core/remover_postagem_confirmacao.html', {'postagem': postagem, 'topico': topico})

@login_required
def notificacoes(request):
    return render(request, 'core/notificacoes.html')

@login_required
def grade_horaria(request):
    return render(request, 'core/grade_horaria.html')

@login_required
def view_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    # Verifica se o perfil é privado e se o usuário não é o dono do perfil
    if not user.is_public_profile and request.user != user:
        context = {
            'profile_user': user,
            'is_private': True,
        }
        return render(request, 'core/view_profile.html', context)

    # Buscar disciplinas e eventos do usuário
    if user.user_type in ['aluno', 'representante', 'professor']:
        disciplinas = Disciplina.objects.filter(userdiscipline__user=user)
    else:
        disciplinas = []

    if user.user_type == 'entidade':
        eventos = Evento.objects.filter(criado_por=user)
    else:
        eventos = []

    context = {
        'profile_user': user,
        'disciplinas': disciplinas,
        'eventos': eventos,
        'is_private': False,
    }
    
    return render(request, 'core/view_profile.html', context)

@login_required
def lista_eventos(request):
    query = request.GET.get('q', '').strip()  # Garante que query seja uma string vazia se não houver valor

    eventos_interesse = Evento.objects.none()
    todos_eventos = Evento.objects.all()

    if request.user.is_authenticated:
        eventos_interesse = request.user.eventos_interesse.all()
        todos_eventos = todos_eventos.exclude(id__in=eventos_interesse.values_list('id', flat=True))

    if query:
        # Filtra eventos pelo nome do evento ou pelo nome completo do organizador
        eventos_interesse = eventos_interesse.filter(
            Q(nome__icontains=query) | Q(criado_por__first_name__icontains=query) | Q(criado_por__last_name__icontains=query)
        )
        todos_eventos = todos_eventos.filter(
            Q(nome__icontains=query) | Q(criado_por__first_name__icontains=query) | Q(criado_por__last_name__icontains=query)
        )

    context = {
        'todos_eventos': todos_eventos,
        'eventos_interesse': eventos_interesse,
        'query': query,  # Passa a consulta de pesquisa de volta ao contexto
    }
    return render(request, 'core/lista_eventos.html', context)

@login_required
def criar_evento(request):
    if request.user.user_type != 'entidade':
        return redirect('lista_eventos')  # Redireciona se o usuário não é uma entidade

    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.criado_por = request.user
            evento.save()
            return redirect('lista_eventos')
    else:
        form = EventoForm()

    return render(request, 'core/criar_evento.html', {'form': form})

@login_required
def detalhe_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    return render(request, 'core/detalhe_evento.html', {'evento': evento})

@login_required
def editar_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)

    if request.user != evento.criado_por:
        return redirect('lista_eventos')

    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            form.save()
            # Após salvar, cria uma notificação para os interessados
            interessados = evento.interessados.all()
            if interessados.exists():
                notificacao = Notificacao.objects.create(
                    titulo=f"Evento {evento.nome} foi editado",
                    mensagem=f"O evento {evento.nome} foi editado. Confira os detalhes.",
                    criador=request.user,
                    evento=evento
                )
                notificacao.destinatarios.set(interessados)
            return redirect('detalhe_evento', evento_id=evento.id)
    else:
        form = EventoForm(instance=evento)

    context = {
        'form': form,
        'evento': evento  # Passando a instância do evento para o template
    }

    return render(request, 'core/editar_evento.html', context)

@login_required
def deletar_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    
    if request.user == evento.criado_por:
        evento.delete()

    return redirect('lista_eventos')

@login_required
def toggle_interesse(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    if request.user in evento.interessados.all():
        request.user.eventos_interesse.remove(evento)
    else:
        request.user.eventos_interesse.add(evento)
    return redirect('detalhe_evento', evento_id=evento.id)


@login_required
def notificacoes(request):
    usuario = request.user
    
    # Inicialize o QuerySet de notificações vazio
    notificacoes = Notificacao.objects.none()

    if usuario.user_type in ['aluno', 'representante', 'professor']:
        # Para alunos, representantes e professores, filtrar notificações de disciplinas que possuem
        disciplinas_usuario = Disciplina.objects.filter(userdiscipline__user=usuario)
        notificacoes_disciplina = Notificacao.objects.filter(disciplina__in=disciplinas_usuario)

        # Adicione notificações de eventos de interesse
        eventos_interessados = Evento.objects.filter(interessados=usuario)
        notificacoes_eventos_interessados = Notificacao.objects.filter(evento__in=eventos_interessados)

        # Combine notificações de disciplinas e eventos de interesse
        notificacoes = notificacoes_disciplina | notificacoes_eventos_interessados

    if usuario.user_type == 'entidade':
        # Para entidades, incluir notificações de eventos que criaram ou estão interessados
        eventos_usuario = Evento.objects.filter(criado_por=usuario)
        eventos_interessados = Evento.objects.filter(interessados=usuario)
        notificacoes_evento = Notificacao.objects.filter(evento__in=eventos_usuario | eventos_interessados)

        # Combine notificações dos eventos organizados e interessados
        notificacoes = notificacoes_evento

    # Adicione notificações criadas pelo próprio usuário
    notificacoes_criadas = Notificacao.objects.filter(criador=usuario)
    notificacoes = (notificacoes | notificacoes_criadas).distinct()

    # Verifica se o usuário pode criar notificações
    pode_criar = usuario.user_type in ['professor', 'representante', 'entidade']

    context = {
        'notificacoes': notificacoes,
        'pode_criar': pode_criar,
    }
    return render(request, 'core/notificacoes.html', context)

@login_required
@login_required
def criar_notificacao(request):
    if request.user.user_type not in ['professor', 'representante', 'entidade']:
        return redirect('notificacoes')

    if request.method == 'POST':
        form = NotificationForm(request.POST, user=request.user)
        if form.is_valid():
            notificacao = form.save(commit=False)
            notificacao.criador = request.user

            # Salve só uma associação
            if request.user.user_type in ['professor', 'representante']:
                notificacao.evento = None  # Certifique-se de que evento está nulo
            elif request.user.user_type == 'entidade':
                notificacao.disciplina = None  # Certifique-se de que disciplina está nula

            notificacao.save()
            return redirect('notificacoes')
    else:
        form = NotificationForm(user=request.user)

    return render(request, 'core/criar_notificacao.html', {'form': form})

@login_required
def minhas_notificacoes(request):
    # Notificações criadas pelo usuário
    notificacoes = Notificacao.objects.filter(criador=request.user)
    return render(request, 'core/minhas_notificacoes.html', {'notificacoes': notificacoes})

@login_required
def editar_notificacao(request, notificacao_id):
    notificacao = get_object_or_404(Notificacao, id=notificacao_id, criador=request.user)
    
    if request.method == 'POST':
        form = NotificationForm(request.POST, instance=notificacao, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('minhas_notificacoes')
    else:
        form = NotificationForm(instance=notificacao, user=request.user)

    return render(request, 'core/editar_notificacao.html', {'form': form})

@login_required
def remover_notificacao(request, notificacao_id):
    notificacao = get_object_or_404(Notificacao, id=notificacao_id, criador=request.user)
    notificacao.delete()
    return redirect('minhas_notificacoes')

@login_required
def excluir_notificacao_recebida(request, notificacao_id):
    notificacao = get_object_or_404(Notificacao, id=notificacao_id)
    
    # Adiciona o usuário à lista de usuários que excluíram a notificação
    notificacao.excluidas_por.add(request.user)
    
    return redirect('notificacoes')

User = get_user_model()

def search_results(request):
    query = request.GET.get('query', '')
    filter_type = request.GET.get('filter', 'user')

    users, disciplinas, eventos = [], [], []
    
    if query:
        if filter_type == 'user':
            users = User.objects.filter(username__icontains=query)
        elif filter_type == 'disciplina':
            # Buscar disciplinas por nome e código
            disciplinas = Disciplina.objects.filter(Q(nome__icontains=query) | Q(codigo__icontains=query))
        elif filter_type == 'evento':
            eventos = Evento.objects.filter(nome__icontains=query)

    context = {
        'query': query,
        'filter': filter_type,
        'users': users,
        'disciplinas': disciplinas,
        'eventos': eventos,
    }
    return render(request, 'core/search_results.html', context)
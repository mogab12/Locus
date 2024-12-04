from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model
from django.db.models import Q
from django.contrib import messages
from .forms import CustomUserCreationForm, UserProfileForm, NovoTopicoForm, NovaPostagemForm
from django.http import HttpResponseForbidden
from .models import Disciplina, UserDiscipline, Topico, Postagem, CustomUser, Evento, Notificacao, Sala, Predio, Mapas
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from .forms import TopicoForm, EventoForm, NotificationForm, SalaForm
from django.http import JsonResponse




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
            messages.success(request, 'Registro realizado com sucesso!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Credenciais inválidas')
        else:
            messages.error(request, 'Por favor, preencha todos os campos')
    return render(request, 'core/login.html')


@login_required
def disciplinas(request):
    if request.user.user_type not in ['aluno', 'representante', 'professor']:
        raise PermissionDenied

    # Obtenha todas as disciplinas do usuário
    user_disciplines = UserDiscipline.objects.filter(user=request.user).select_related('disciplina')

    # Cria um dicionário para contar as turmas de cada disciplina
    turma_counts = {}
    for ud in user_disciplines:
        key = (ud.disciplina.nome, ud.disciplina.codigo)
        if key in turma_counts:
            turma_counts[key] += 1
        else:
            turma_counts[key] = 1

    # Crie uma lista de tuplas com a disciplina e a flag para mostrar a turma
    disciplinas_com_turmas = [
        (ud, turma_counts[(ud.disciplina.nome, ud.disciplina.codigo)] > 1)
        for ud in user_disciplines
    ]

    return render(request, 'core/disciplinas.html', {'user_disciplines': disciplinas_com_turmas})

@login_required
def remover_disciplinas(request):
    if request.user.user_type not in ['aluno', 'representante', 'professor']:
        raise PermissionDenied

    user_disciplines = UserDiscipline.objects.filter(user=request.user).select_related('disciplina')

    # Cria um dicionário para contar as turmas de cada disciplina
    turma_counts = {}
    for ud in user_disciplines:
        key = (ud.disciplina.nome, ud.disciplina.codigo)
        if key in turma_counts:
            turma_counts[key] += 1
        else:
            turma_counts[key] = 1

    # Crie uma lista de tuplas com a disciplina e a flag para mostrar a turma
    disciplinas_com_turmas = [
        (ud, turma_counts[(ud.disciplina.nome, ud.disciplina.codigo)] > 1)
        for ud in user_disciplines
    ]

    if request.method == 'POST':
        if 'remove' in request.POST:
            disciplina_id = request.POST.get('disciplina_id')
            UserDiscipline.objects.filter(user=request.user, disciplina_id=disciplina_id).delete()
            messages.success(request, 'Disciplina removida com sucesso!')

        elif 'remover_todas' in request.POST:
            UserDiscipline.objects.filter(user=request.user).delete()
            messages.success(request, 'Todas as disciplinas foram removidas.')

    return render(request, 'core/remover_disciplinas.html', {
        'user_disciplines': disciplinas_com_turmas,
    })

@login_required
def adicionar_disciplinas(request):
    if request.user.user_type not in ['aluno', 'representante', 'professor']:
        raise PermissionDenied

    search_results = []
    query = request.GET.get('q', '')

    if request.method == 'POST':
        if 'add' in request.POST:
            # Adicionar a disciplina selecionada ao usuário
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
        # Recuperar todas as disciplinas que correspondem à busca
        all_results = Disciplina.objects.filter(
            Q(nome__icontains=query) | Q(codigo__icontains=query)
        )

        # Obter disciplinas que o usuário já adicionou
        disciplinas_usuario = UserDiscipline.objects.filter(user=request.user).values_list('disciplina_id', flat=True)

        # Filtrar disciplinas que o usuário ainda não adicionou
        search_results = all_results.exclude(id__in=disciplinas_usuario)

        # Verificar quantas turmas existem para exibir a turma quando apropriado
        turma_counts = {}
        for disciplina in search_results:
            key = (disciplina.nome, disciplina.codigo)
            if key in turma_counts:
                turma_counts[key] += 1
            else:
                turma_counts[key] = 1

        # Atualizar search_results com a lógica de exibição de turma
        search_results = [
            (disciplina, turma_counts[(disciplina.nome, disciplina.codigo)] > 1)
            for disciplina in search_results
        ]

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
        return redirect('lista_eventos')

    # Recupera dados do formulário da sessão se existirem
    form_data = request.session.get('form_data', {})
    latitude = request.session.pop('latitude', None)
    longitude = request.session.pop('longitude', None)

    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.criado_por = request.user
            evento.save()
            # Limpa dados da sessão ao salvar
            request.session.pop('form_data', None)
            return redirect('lista_eventos')
    else:
        # Adiciona coordenadas à inicialização se existirem
        if latitude and longitude:
            form_data.update({'latitude': latitude, 'longitude': longitude})
        form = EventoForm(initial=form_data)

    return render(request, 'core/criar_evento.html', {'form': form})

def adicionar_local_evento(request):
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        # Armazena as coordenadas na sessão
        request.session['latitude'] = latitude
        request.session['longitude'] = longitude
        
        # Armazena dados do formulário na sessão
        form_data = {key: request.POST.get(key) for key in request.POST if key != 'csrfmiddlewaretoken'}
        request.session['form_data'] = form_data
        
        return redirect('criar_evento')
    
    return render(request, 'core/adicionar_local_evento.html')

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

from .models import HorarioGrade, Disciplina
from .forms import HorarioGradeForm

@login_required
def grade_horaria(request):
    # Organiza horários por dia da semana
    horarios = request.user.horarios_grade.all().order_by('dia_da_semana', 'horario_inicio')
    dias_da_semana = ['SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SAB', 'DOM']
    grade = {dia: [] for dia in dias_da_semana}
    
    for horario in horarios:
        grade[horario.dia_da_semana].append(horario)

    return render(request, 'core/grade_horaria.html', {'grade': grade})

@login_required
def adicionar_horario_grade(request):
    if request.method == 'POST':
        form = HorarioGradeForm(request.POST)
        # Filtra disciplinas que o usuário possui
        form.fields['disciplina'].queryset = Disciplina.objects.filter(userdiscipline__user=request.user)
        if form.is_valid():
            horario_grade = form.save(commit=False)
            horario_grade.usuario = request.user
            horario_grade.save()
            return redirect('grade_horaria')
    else:
        form = HorarioGradeForm()
        # Filtra disciplinas que o usuário possui
        form.fields['disciplina'].queryset = Disciplina.objects.filter(userdiscipline__user=request.user)

    return render(request, 'core/adicionar_horario_grade.html', {'form': form})
@login_required
def adicionar_horario_grade(request):
    if request.method == 'POST':
        form = HorarioGradeForm(request.POST)
        # Filtra disciplinas que o usuário possui
        form.fields['disciplina'].queryset = Disciplina.objects.filter(userdiscipline__user=request.user)
        if form.is_valid():
            horario_grade = form.save(commit=False)
            horario_grade.usuario = request.user
            horario_grade.save()
            return redirect('grade_horaria')
    else:
        form = HorarioGradeForm()
        # Filtra disciplinas que o usuário possui
        form.fields['disciplina'].queryset = Disciplina.objects.filter(userdiscipline__user=request.user)

    return render(request, 'core/adicionar_horario_grade.html', {'form': form})

@login_required
def remover_horario_grade(request, horario_id):
    horario = get_object_or_404(HorarioGrade, id=horario_id, usuario=request.user)
    if request.method == 'POST':
        horario.delete()
        return redirect('grade_horaria')
    return render(request, 'core/remover_horario_grade.html', {'horario': horario})

@login_required
def editar_horario_grade(request, horario_id):
    horario = get_object_or_404(HorarioGrade, id=horario_id, usuario=request.user)
    
    if request.method == 'POST':
        form = HorarioGradeForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            return redirect('grade_horaria')
    else:
        form = HorarioGradeForm(instance=horario)
        # Filtra apenas as disciplinas que o usuário possui
        form.fields['disciplina'].queryset = Disciplina.objects.filter(userdiscipline__user=request.user)

    return render(request, 'core/editar_horario_grade.html', {'form': form, 'horario': horario})

import pytz
from datetime import datetime,timedelta

def proxima_aula(usuario):
    # Obtém o horário atual no fuso horário de São Paulo
    agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
    # Mapeia os dias da semana para suas abreviações
    dias_abreviados = {
        'Monday': 'SEG',
        'Tuesday': 'TER',
        'Wednesday': 'QUA',
        'Thursday': 'QUI',
        'Friday': 'SEX',
        'Saturday': 'SAB',
        'Sunday': 'DOM'
    }
    # Obtém a abreviação do dia atual
    dia_atual = dias_abreviados[agora.strftime('%A')]
    hora_atual = agora.time()

    # Definindo a janela de 10 minutos antes e depois do início da aula
    janela_inicio = timedelta(minutes=10)

    # Filtra os horários do dia atual
    horarios_do_dia = usuario.horarios_grade.filter(dia_da_semana=dia_atual)

    for horario in horarios_do_dia:
        inicio = (datetime.combine(datetime.today(), horario.horario_inicio) - janela_inicio).time()
        fim_aviso = (datetime.combine(datetime.today(), horario.horario_inicio) + janela_inicio).time()

        # Verifica se a hora atual está dentro da janela
        if inicio <= hora_atual <= fim_aviso:
            return horario

    return None

@login_required
def adicionar_local(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, id=disciplina_id)

    if request.method == "POST":
        form = SalaForm(request.POST)
        if form.is_valid():
            disciplina.sala = form.cleaned_data['sala']
            disciplina.save()
            return redirect('detalhe_disciplina', disciplina_id=disciplina.id)
    else:
        form = SalaForm()

    return render(request, 'core/adicionar_local.html', {'form': form, 'disciplina': disciplina})

@login_required
def get_salas(request, predio_id):
    salas = Sala.objects.filter(predio_id=predio_id)
    salas_json = [{'id': s.id, 'nome': s.nome} for s in salas]
    return JsonResponse(salas_json, safe=False)


@login_required
def home(request):
    aula_proxima = proxima_aula(request.user)
    predios = Predio.objects.all()
    
    return render(request, 'core/home.html', {'aula_proxima': aula_proxima, 'predios': predios})

def ver_local_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)

    if not evento.latitude or not evento.longitude:
        # Redireciona ou exibe uma mensagem de erro apropriada se não houver coordenadas
        return render(request, 'core/no_location.html', {'evento': evento})

    context = {
        'evento': evento,
        'latitude': float(evento.latitude),  # Converte os valores para float se necessário
        'longitude': float(evento.longitude),
    }

    return render(request, 'core/ver_local_evento.html', context)



def mapa_detalhe(request,mapa_id):
    mapa = get_object_or_404(Mapas,id = mapa_id)
    aula_proxima = proxima_aula(request.user)
    context = {
        'mapa' : mapa,
        'aula_proxima' : aula_proxima,
    }
    return render(request,'core/mapa_detalhe.html',context)

def mudar_andar(request,mapa_id):
    mapa = get_object_or_404(Mapas,id = mapa_id)
    aula_proxima = proxima_aula(request.user)
    context = {
        'mapa' : mapa,
        'aula_proxima' : aula_proxima,
    }
    return render(request,'core/mudar_andar.html',context)
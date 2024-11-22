from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model
from django.db.models import Q
from django.contrib import messages
from .forms import CustomUserCreationForm, UserProfileForm, NovoTopicoForm, NovaPostagemForm
from django.http import HttpResponseForbidden
from .models import Disciplina, UserDiscipline, Topico, Postagem, CustomUser
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from .forms import TopicoForm




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
    if request.method == 'POST':
        form = NovaPostagemForm(request.POST)
        if form.is_valid():
            postagem = form.save(commit=False)
            postagem.topico = topico
            postagem.criado_por = request.user
            postagem.save()
            return redirect('detalhe_topico', topico_id=topico.id)
    else:
        form = NovaPostagemForm()
    return render(request, 'core/detalhe_topico.html', {'topico': topico, 'form': form})

@login_required
def novo_topico(request, disciplina_id):
    # Verificar se o usuário é um representante ou professor
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
def eventos(request):
    return render(request, 'core/eventos.html')

@login_required
def notificacoes(request):
    return render(request, 'core/notificacoes.html')

@login_required
def grade_horaria(request):
    return render(request, 'core/grade_horaria.html')

@login_required
def view_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Filtrar disciplinas de acordo com o tipo de usuário
    if user.user_type in ['aluno', 'representante', 'professor']:
        # Utilize a relação UserDiscipline para obter as disciplinas do aluno/representante
        disciplinas = Disciplina.objects.filter(userdiscipline__user=user)
    else:
        disciplinas = []  # Ou qualquer lógica que faça sentido para outros tipos de usuário

    context = {
        'profile_user': user,
        'disciplinas': disciplinas,
    }
    
    return render(request, 'core/view_profile.html', context)
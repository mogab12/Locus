from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.contrib import messages
from .forms import CustomUserCreationForm, UserProfileForm, NovoTopicoForm, NovaPostagemForm
from django.http import HttpResponseForbidden
from .models import Disciplina, UserDiscipline, Topico




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
    if request.user.user_type not in ['aluno', 'representante']:
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")

    user_disciplines = UserDiscipline.objects.filter(user=request.user).select_related('disciplina')
    return render(request, 'core/disciplinas.html', {
        'user_disciplines': user_disciplines,
    })

@login_required
def remover_disciplinas(request):
    if request.user.user_type not in ['aluno', 'representante']:
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")

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
    if request.user.user_type not in ['aluno', 'representante']:
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")

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

@login_required
def detalhe_disciplina(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, id=disciplina_id)
    return render(request, 'core/detalhe_disciplina.html', {'disciplina': disciplina})

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
def eventos(request):
    return render(request, 'core/eventos.html')

@login_required
def notificacoes(request):
    return render(request, 'core/notificacoes.html')

@login_required
def grade_horaria(request):
    return render(request, 'core/grade_horaria.html')
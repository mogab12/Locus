from django.shortcuts import render

def home(request):
    return render(request, 'core/home.html')

def disciplinas(request):
    return render(request, 'core/disciplinas.html')

def eventos(request):
    return render(request, 'core/eventos.html')

def notificacoes(request):
    return render(request, 'core/notificacoes.html')

def grade_horaria(request):
    return render(request, 'core/grade_horaria.html')
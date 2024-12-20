from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator
from django.contrib.auth import get_user_model
from django.conf import settings

class CustomEmailValidator(EmailValidator):
    def validate_domain_part(self, domain_part):
        return domain_part.lower().endswith('usp.br')

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('aluno', 'Aluno'),
        ('representante', 'Representante de Classe'),
        ('professor', 'Professor'),
        ('entidade', 'Entidade'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='aluno')
    curso = models.CharField(max_length=100, blank=True, null=True)
    semestre = models.CharField(max_length=3, blank=True, null=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    foto = models.ImageField(upload_to='user_photos/', blank=True, null=True, default='defaultphoto.jpg')
    email = models.EmailField(unique=True, validators=[CustomEmailValidator()])
    eventos_interesse = models.ManyToManyField('Evento', blank=True, related_name='interessados')
    is_public_profile = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

class Predio(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.nome
    

class Sala(models.Model):
    nome = models.CharField(max_length=50)
    predio = models.ForeignKey(Predio, on_delete=models.CASCADE, related_name='salas')
    pos_x = models.IntegerField(default=400)
    pos_y = models.IntegerField(default=200)
    Andar = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.nome} ({self.predio.nome})"

class Disciplina(models.Model):
    nome = models.CharField(max_length=255)
    codigo = models.CharField(max_length=10)
    curso = models.CharField(max_length=255)
    semestre = models.CharField(max_length=10)
    tipo = models.CharField(max_length=50)
    sala = models.ForeignKey(Sala, on_delete=models.SET_NULL, null=True, blank=True, related_name='disciplinas')
    professor_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'user_type': 'professor'}
    )
    turma = models.IntegerField(default=1)
    def __str__(self):
        return self.nome

User = get_user_model()

class UserDiscipline(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    disciplina = models.ForeignKey('Disciplina', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.disciplina.nome}"

class Topico(models.Model):
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    disciplina = models.ForeignKey(Disciplina, related_name='topicos', on_delete=models.CASCADE)
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)

class Postagem(models.Model):
    conteudo = models.TextField()
    topico = models.ForeignKey(Topico, related_name='postagens', on_delete=models.CASCADE)
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)
    



class Notificacao(models.Model):
    titulo = models.CharField(max_length=255)
    mensagem = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    criador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificacoes_criadas')
    destinatarios = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='notificacoes_recebidas')
    disciplina = models.ForeignKey('Disciplina', null=True, blank=True, on_delete=models.SET_NULL, related_name='notificacoes')
    evento = models.ForeignKey('Evento', null=True, blank=True, on_delete=models.SET_NULL, related_name='notificacoes')
    topico = models.ForeignKey('Topico', null=True, blank=True, on_delete=models.SET_NULL, related_name='notificacoes')  # Novo campo
    excluidas_por = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='notificacoes_excluidas', blank=True)

    def __str__(self):
        return f"{self.titulo} - {self.criador.get_full_name()}"
    
class HorarioGrade(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='horarios_grade')
    disciplina = models.ForeignKey('Disciplina', on_delete=models.CASCADE)
    dia_da_semana = models.CharField(max_length=3, choices=[
        ('SEG', 'Segunda-feira'),
        ('TER', 'Terça-feira'),
        ('QUA', 'Quarta-feira'),
        ('QUI', 'Quinta-feira'),
        ('SEX', 'Sexta-feira'),
        ('SAB', 'Sábado'),
        ('DOM', 'Domingo'),
    ])
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()

    def __str__(self):
        return f"{self.usuario} - {self.disciplina.nome} ({self.get_dia_da_semana_display()})"
    

class Evento(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField()
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    local = models.CharField(max_length=255, null=True, blank=True)  # Descrição textual do local
    latitude = models.FloatField(null=True, blank=True)  # Coordenada latitude
    longitude = models.FloatField(null=True, blank=True)  # Coordenada longitude
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'entidade'}
    )
    imagem = models.ImageField(upload_to='eventos/', null=True, blank=True)

    def __str__(self):
        return self.nome


class Interesse(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    data_interesse = models.DateTimeField(auto_now_add=True)


class Mapas(models.Model):
    nome = models.CharField(max_length=255)
    planta= models.ImageField()
    planta_2= models.ImageField(default=None)
    predio = models.ForeignKey('Predio',on_delete=models.CASCADE,related_name='mapas')
    def __str__(self):
        return self.nome
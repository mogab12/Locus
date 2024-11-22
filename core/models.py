from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator
from django.contrib.auth import get_user_model

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
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

class Disciplina(models.Model):
    nome = models.CharField(max_length=255)
    codigo = models.CharField(max_length=50)
    semestre = models.CharField(max_length=50)
    curso = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nome} ({self.codigo})"
    
User = get_user_model()

class UserDiscipline(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_disciplines')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'disciplina')

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
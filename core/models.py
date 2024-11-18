from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator

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
    foto = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    email = models.EmailField(unique=True, validators=[CustomEmailValidator()])

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
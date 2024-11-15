from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('aluno', 'Aluno'),
        ('representante', 'Representante de Classe'),
        ('professor', 'Professor'),
        ('entidade', 'Entidade'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='aluno')
    curso = models.CharField(max_length=100, blank=True, null=True)
    semestre = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
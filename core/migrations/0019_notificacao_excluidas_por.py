# Generated by Django 4.2.16 on 2024-11-24 21:16

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_alter_notificacao_disciplina_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificacao',
            name='excluidas_por',
            field=models.ManyToManyField(blank=True, related_name='notificacoes_excluidas', to=settings.AUTH_USER_MODEL),
        ),
    ]

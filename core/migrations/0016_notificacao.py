# Generated by Django 4.2.16 on 2024-11-24 20:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_customuser_is_public_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notificacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=255)),
                ('mensagem', models.TextField()),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('criador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notificacoes_criadas', to=settings.AUTH_USER_MODEL)),
                ('destinatarios', models.ManyToManyField(related_name='notificacoes_recebidas', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
# Generated by Django 4.2.16 on 2024-11-24 21:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_notificacao_excluidas_por'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificacao',
            name='topico',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notificacoes', to='core.topico'),
        ),
    ]

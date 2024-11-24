# Generated by Django 4.2.16 on 2024-11-24 20:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_notificacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificacao',
            name='disciplina',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.disciplina'),
        ),
        migrations.AddField(
            model_name='notificacao',
            name='evento',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.evento'),
        ),
    ]

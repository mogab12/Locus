# Generated by Django 4.2.16 on 2024-12-04 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_sala_pos_x_sala_pos_y'),
    ]

    operations = [
        migrations.AddField(
            model_name='sala',
            name='Andar',
            field=models.IntegerField(default=1),
        ),
    ]
# Generated by Django 4.2.16 on 2024-12-04 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_sala_andar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sala',
            name='pos_x',
            field=models.IntegerField(default=400),
        ),
        migrations.AlterField(
            model_name='sala',
            name='pos_y',
            field=models.IntegerField(default=200),
        ),
    ]

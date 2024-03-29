# Generated by Django 2.2.10 on 2023-03-03 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0308_auto_20230223_0710'),
    ]

    operations = [
        migrations.AddField(
            model_name='parametros',
            name='periodo_de_tempo_tentativas_concluir_pc',
            field=models.PositiveSmallIntegerField(default=120, verbose_name='Qual o período de tempo das tentativas de conclusão da PC (minutos)?'),
        ),
        migrations.AddField(
            model_name='parametros',
            name='quantidade_tentativas_concluir_pc',
            field=models.PositiveSmallIntegerField(default=3, verbose_name='Quantas tentativas deve-se permitir para a conclusão da PC (vezes)?'),
        ),
    ]

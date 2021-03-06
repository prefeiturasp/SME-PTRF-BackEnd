# Generated by Django 2.2.10 on 2020-06-22 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_auto_20200622_2019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membroassociacao',
            name='cargo_associacao',
            field=models.CharField(blank=True, choices=[('Presidente da diretoria executiva', 'PRESIDENTE_DIRETORIA_EXECUTIVA'), ('Vice-Presidente da diretoria executiva', 'VICE_PRESIDENTE_DIRETORIA_EXECUTIVA'), ('Secretario', 'SECRETARIO'), ('Tesoureiro', 'TESOUREIRO'), ('Vogal 1', 'VOGAL_1'), ('Vogal 2', 'VOGAL_2'), ('Vogal 3', 'VOGAL_3'), ('Vogal 4', 'VOGAL_4'), ('Vogal 5', 'VOGAL_5'), ('Presidente do conselho fiscal', 'PRESIDENTE_CONSELHO_FISCAL'), ('Conselheiro 1', 'CONSELHEIRO_1'), ('Conselheiro 2', 'CONSELHEIRO_2'), ('Conselheiro 3', 'CONSELHEIRO_3'), ('Conselheiro 4', 'CONSELHEIRO_4')], default='Presidente da diretoria executiva', max_length=65, null=True, verbose_name='Cargo Associação'),
        ),
        migrations.AlterField(
            model_name='membroassociacao',
            name='representacao',
            field=models.CharField(choices=[('Servidor', 'SERVIDOR'), ('Pai_ou_responsável', 'PAI_RESPONSAVEL'), ('Estudante', 'ESTUDANTE')], default='Servidor', max_length=25, verbose_name='Representação'),
        ),
    ]

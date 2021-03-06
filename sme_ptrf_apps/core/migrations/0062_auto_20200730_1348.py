# Generated by Django 2.2.10 on 2020-07-30 13:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0061_associacao_status_regularidade'),
    ]

    operations = [
        migrations.AddField(
            model_name='unidade',
            name='bairro',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Bairro'),
        ),
        migrations.AddField(
            model_name='unidade',
            name='cep',
            field=models.CharField(blank=True, default='', max_length=20, validators=[django.core.validators.RegexValidator(message='Digite o CEP no formato XXXXX-XXX. Com 8 digitos', regex='^\\d{5}-\\d{3}$')], verbose_name='CEP'),
        ),
        migrations.AddField(
            model_name='unidade',
            name='complemento',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Complemento'),
        ),
        migrations.AddField(
            model_name='unidade',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254, verbose_name='E-mail'),
        ),
        migrations.AddField(
            model_name='unidade',
            name='logradouro',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Logradouro'),
        ),
        migrations.AddField(
            model_name='unidade',
            name='numero',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Numero'),
        ),
        migrations.AddField(
            model_name='unidade',
            name='qtd_alunos',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Quantidade de alunos'),
        ),
        migrations.AddField(
            model_name='unidade',
            name='telefone',
            field=models.CharField(blank=True, default='', max_length=20, validators=[django.core.validators.RegexValidator(message='Digite o telefone no formato (XX) 12345-6789. Entre 8 ou 9 digitos', regex='^\\(\\d{2}\\) [\\d\\-]{9,10}$')], verbose_name='Telefone'),
        ),
        migrations.AddField(
            model_name='unidade',
            name='tipo_logradouro',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='Tipo de Logradouro'),
        ),
    ]

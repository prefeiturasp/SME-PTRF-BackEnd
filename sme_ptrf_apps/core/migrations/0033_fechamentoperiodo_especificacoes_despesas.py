# Generated by Django 2.2.10 on 2020-06-05 16:38

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_auto_20200604_1425'),
    ]

    operations = [
        migrations.AddField(
            model_name='fechamentoperiodo',
            name='especificacoes_despesas',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=[], size=None, verbose_name='especificações das despesas'),
        ),
    ]

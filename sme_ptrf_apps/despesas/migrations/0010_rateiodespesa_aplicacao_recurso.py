# Generated by Django 2.2.10 on 2020-03-24 19:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('despesas', '0009_rateiodespesa_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='rateiodespesa',
            name='aplicacao_recurso',
            field=models.CharField(choices=[('CAPITAL', 'Capital'), ('INCOMPLETO', 'Custeio')], default='INCOMPLETO',
                                   max_length=15, verbose_name='Tipo de aplicação do recurso'),
        ),
    ]

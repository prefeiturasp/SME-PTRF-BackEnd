# Generated by Django 2.2.10 on 2020-11-25 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0119_auto_20201125_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='arquivo',
            name='tipo_carga',
            field=models.CharField(choices=[('REPASSE_REALIZADO', 'Repasses realizados'), ('CARGA_PERIODO_INICIAL', 'Carga período inicial'), ('REPASSE_PREVISTO', 'Repasses previstos'), ('CARGA_ASSOCIACOES', 'Carga de Associações'), ('CARGA_USUARIOS', 'Carga de usuários'), ('CARGA_CENSO', 'Carga de censo'), ('CARGA_REPASSE_PREVISTO_SME', 'Repasses previstos sme')], default='REPASSE_REALIZADO', max_length=35, verbose_name='tipo de carga'),
        ),
    ]

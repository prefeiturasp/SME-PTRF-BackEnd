# Generated by Django 2.2.10 on 2023-01-27 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0304_auto_20230127_0652'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parametros',
            name='tempo_aguardar_conclusao_pc',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Quanto tempo deve-se aguardar a conclusão da PC (segundos)?'),
        ),
    ]

# Generated by Django 2.2.10 on 2021-03-23 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0159_auto_20210323_1357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demonstrativofinanceiro',
            name='status',
            field=models.CharField(choices=[('EM_PROCESSAMENTO', 'Em processamento'), ('CONCLUIDO', 'Geração concluída')], default='CONCLUIDO', max_length=20, verbose_name='status'),
        ),
        migrations.AlterField(
            model_name='relacaobens',
            name='status',
            field=models.CharField(choices=[('EM_PROCESSAMENTO', 'Em processamento'), ('CONCLUIDO', 'Geração concluída')], default='CONCLUIDO', max_length=20, verbose_name='status'),
        ),
    ]

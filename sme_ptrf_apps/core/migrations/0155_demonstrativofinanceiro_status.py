# Generated by Django 2.2.10 on 2021-03-23 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0154_merge_20210316_0909'),
    ]

    operations = [
        migrations.AddField(
            model_name='demonstrativofinanceiro',
            name='status',
            field=models.CharField(choices=[('EM_PROCESSAMENTO', 'Em processamento'), ('CONCLUIDO', 'Geração concluída')], default='CONCLUIDO', max_length=20, verbose_name='status'),
        ),
    ]

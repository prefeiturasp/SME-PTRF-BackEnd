# Generated by Django 2.2.10 on 2021-03-23 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0157_auto_20210323_1042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demonstrativofinanceiro',
            name='versao',
            field=models.CharField(choices=[('FINAL', 'final'), ('PREVIA', 'prévio')], default='FINAL', max_length=20, verbose_name='status'),
        ),
        migrations.AlterField(
            model_name='relacaobens',
            name='versao',
            field=models.CharField(choices=[('FINAL', 'final'), ('PREVIA', 'prévio')], default='FINAL', max_length=20, verbose_name='status'),
        ),
    ]

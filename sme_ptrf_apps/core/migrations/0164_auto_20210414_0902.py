# Generated by Django 2.2.10 on 2021-04-14 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0163_auto_20210330_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='relacaobens',
            name='arquivo_pdf',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='Relatório em PDF'),
        ),
        migrations.AlterField(
            model_name='relacaobens',
            name='arquivo',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='Relatório em XLSX'),
        ),
    ]

# Generated by Django 2.2.10 on 2020-06-26 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('despesas', '0023_auto_20200624_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='tipodocumento',
            name='apenas_digitos',
            field=models.BooleanField(default=False, verbose_name='Apenas dígitos?'),
        ),
    ]

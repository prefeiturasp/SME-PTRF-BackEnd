# Generated by Django 3.0.14 on 2023-05-10 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0329_auto_20230503_1452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unidade',
            name='observacao',
            field=models.TextField(blank=True, default='', help_text='Preencha este campo, se necessário, com informações relacionadas a unidade educacional.', max_length=600, null=True, verbose_name='Observação'),
        ),
    ]

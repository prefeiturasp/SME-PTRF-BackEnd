# Generated by Django 3.2.21 on 2023-10-06 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0353_alter_transferenciaeol_tipo_conta_transferido'),
    ]

    operations = [
        migrations.AddField(
            model_name='transferenciaeol',
            name='copiar_membros',
            field=models.BooleanField(default=False, help_text='Caso marcado, os membros da associação serão copiados para a nova associação.', verbose_name='Copiar membros?'),
        ),
    ]
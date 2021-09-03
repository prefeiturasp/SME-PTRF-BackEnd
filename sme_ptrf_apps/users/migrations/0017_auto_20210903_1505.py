# Generated by Django 2.2.10 on 2021-09-03 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_user_visoes_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='groups_log',
            field=models.TextField(blank=True, help_text='Grupos do usuário (audtilog)'),
        ),
        migrations.AddField(
            model_name='user',
            name='unidades_log',
            field=models.TextField(blank=True, help_text='Unidades do usuário (audtilog)'),
        ),
    ]

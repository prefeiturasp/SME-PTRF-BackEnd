# Generated by Django 3.1.14 on 2023-08-01 13:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0344_auto_20230727_1705'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskcelery',
            name='log',
            field=models.TextField(blank=True, default='', verbose_name='Log capturado'),
        ),
        migrations.AlterField(
            model_name='taskcelery',
            name='id_task_assincrona',
            field=models.CharField(blank=True, max_length=160, null=True, verbose_name='id task assincrona'),
        ),
        migrations.AlterField(
            model_name='taskcelery',
            name='usuario',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks_celery_do_usuario', to=settings.AUTH_USER_MODEL, verbose_name='Usuário'),
        ),
    ]

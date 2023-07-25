# Generated by Django 3.1.14 on 2023-07-21 08:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0340_merge_20230713_0649'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskCelery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alterado_em', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('id_task_assincrona', models.CharField(editable=False, max_length=160, verbose_name='id task assincrona')),
                ('nome_task', models.CharField(max_length=160, verbose_name='Nome')),
                ('data_hora_finalizacao', models.DateTimeField(blank=True, null=True, verbose_name='Data e hora de finalizacao')),
                ('finalizada', models.BooleanField(default=False, verbose_name='Finalizada ?')),
                ('finalizacao_forcada', models.BooleanField(default=False, verbose_name='Finalizada forçadamente ?')),
                ('associacao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks_celery_da_associacao', to='core.associacao', verbose_name='Associação')),
                ('periodo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='asks_celery_do_periodo', to='core.periodo')),
                ('prestacao_conta', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks_celery_da_prestacao_conta', to='core.prestacaoconta')),
                ('usuario', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks_celery_do_usuario', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Task assincrona celery',
                'verbose_name_plural': '19.1) Tasks assincronas celery',
            },
        ),
    ]

# Generated by Django 2.2.10 on 2020-11-23 18:00

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0115_devolucaoaotesouro_visao_criacao'),
    ]

    operations = [
        migrations.CreateModel(
            name='Censo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alterado_em', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('quantidade_alunos', models.IntegerField(blank=True, default=0, verbose_name='Quantidade Alunos')),
                ('ano', models.CharField(blank=True, default='', max_length=4, verbose_name='Ano')),
                ('unidade', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='censos', to='core.Unidade')),
            ],
            options={
                'verbose_name': 'Censo',
                'verbose_name_plural': 'Censos',
            },
        ),
    ]

# Generated by Django 3.1.14 on 2023-07-20 14:59

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0341_solicitacaoencerramentocontaassociacao'),
    ]

    operations = [
        migrations.CreateModel(
            name='MotivoRejeicaoEncerramentoContaAssociacao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=160, verbose_name='Nome')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alterado_em', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
            ],
            options={
                'verbose_name': 'Motivo de rejeição de encerramento de conta de associação',
                'verbose_name_plural': '07.5) Motivos de rejeição de encerramento de conta de associação',
                'unique_together': {('nome',)},
            },
        ),
    ]

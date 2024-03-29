# Generated by Django 2.2.10 on 2023-03-06 07:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0309_auto_20230303_1207'),
    ]

    operations = [
        migrations.CreateModel(
            name='FalhaGeracaoPc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alterado_em', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('data_hora_ultima_ocorrencia', models.DateTimeField(blank=True, null=True, verbose_name='Data e hora da última ocorrência')),
                ('qtd_ocorrencias_sucessivas', models.PositiveSmallIntegerField(blank=True, default=0, null=True, verbose_name='Quantidade de ocorrências sucessivas')),
                ('resolvido', models.BooleanField(default=False, verbose_name='Resolvido?')),
                ('associacao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='falhas_geracao_pc_da_associacao', to='core.Associacao', verbose_name='Associação')),
                ('periodo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='falhas_geracao_pc_do_periodo', to='core.Periodo', verbose_name='Período')),
                ('prestacao_conta', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='falhas_geracao_pc_da_prestacao', to='core.PrestacaoConta', verbose_name='Prestação de Contas')),
                ('ultimo_usuario', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='falhas_geracao_pc_do_usuario', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Falha na Geracao de PC',
                'verbose_name_plural': '19.0) Falhas na Geracao de PCs',
                'unique_together': {('prestacao_conta',)},
            },
        ),
    ]

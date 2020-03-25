# Generated by Django 2.2.10 on 2020-03-19 13:57

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20200318_1504'),
        ('despesas', '0005_especificacaomaterialservico'),
    ]

    operations = [
        migrations.CreateModel(
            name='RateioDespesa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alterado_em', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('valor_rateio', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Valor')),
                ('quantidade_itens_capital', models.PositiveSmallIntegerField(default=0, verbose_name='Quantidade de itens')),
                ('valor_item_capital', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Valor unitário ')),
                ('numero_processo_incorporacao_capital', models.CharField(blank=True, default='', max_length=100, verbose_name='Nº processo incorporação')),
                ('acao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.Acao')),
                ('associacao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='rateios_associacao', to='core.Associacao')),
                ('conta_associacao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='rateios_da_conta', to='core.ContaAssociacao')),
                ('despesa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rateios', to='despesas.Despesa')),
                ('especificacao_material_servico', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='despesas.EspecificacaoMaterialServico')),
                ('tipo_aplicacao_recurso', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='despesas.TipoAplicacaoRecurso')),
                ('tipo_custeio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='despesas.TipoCusteio')),
            ],
            options={
                'verbose_name': 'Rateio de despesa',
                'verbose_name_plural': 'Rateios de despesas',
            },
        ),
    ]

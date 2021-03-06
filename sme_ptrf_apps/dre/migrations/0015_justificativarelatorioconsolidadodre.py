# Generated by Django 2.2.10 on 2020-11-04 09:47

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0109_auto_20201030_1436'),
        ('dre', '0014_auto_20201028_1553'),
    ]

    operations = [
        migrations.CreateModel(
            name='JustificativaRelatorioConsolidadoDRE',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alterado_em', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('texto', models.TextField(blank=True, max_length=600, null=True, verbose_name='Justificativa')),
                ('dre', models.ForeignKey(blank=True, limit_choices_to={'tipo_unidade': 'DRE'}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='justificativas_relatorios_consolidados_da_dre', to='core.Unidade')),
                ('periodo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='justificativas_relatorios_consolidados_dre_do_periodo', to='core.Periodo')),
                ('tipo_conta', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.TipoConta')),
            ],
            options={
                'verbose_name': 'Justificativa de relatório consolidado DRE',
                'verbose_name_plural': 'Justificativas de relatórios consolidados DREs',
            },
        ),
    ]

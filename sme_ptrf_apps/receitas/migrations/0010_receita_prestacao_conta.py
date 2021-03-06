# Generated by Django 2.2.10 on 2020-06-10 19:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_acao_posicao_nas_pesquisas'),
        ('receitas', '0009_tiporeceita_e_rendimento'),
    ]

    operations = [
        migrations.AddField(
            model_name='receita',
            name='prestacao_conta',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='receitas_conciliadas', to='core.PrestacaoConta', verbose_name='prestação de contas de conciliação'),
        ),
    ]

# Generated by Django 2.2.10 on 2021-01-11 13:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dre', '0021_motivoaprovacaoressalva'),
        ('core', '0131_auto_20210107_1655'),
    ]

    operations = [
        migrations.AddField(
            model_name='prestacaoconta',
            name='motivo_aprovacao_ressalva',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='prestacoes_de_conta_com_o_motivo', to='dre.MotivoAprovacaoRessalva'),
        ),
    ]

# Generated by Django 2.2.10 on 2022-11-03 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0296_merge_20221031_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificacao',
            name='categoria',
            field=models.CharField(choices=[('COMENTARIO_PC', 'Comentário na prestação de contas'), ('ELABORACAO_PC', 'Elaboração de PC'), ('ANALISE_PC', 'Análise de PC'), ('DEVOLUCAO_PC', 'Devolução de PC para ajustes'), ('APROVACAO_PC', 'Aprovação de PC'), ('APROVACAO_RESSALVAS_PC', 'Aprovação de PC com ressalvas'), ('REPROVACAO_PC', 'Reprovação de PC'), ('DEVOLUCAO_CONSOLIDADO', 'Devolução de relatório consolidado'), ('COMENTARIO_CONSOLIDADO_DRE', 'Comentário no relatório consolidado')], default='COMENTARIO_PC', max_length=40, verbose_name='Categoria'),
        ),
    ]

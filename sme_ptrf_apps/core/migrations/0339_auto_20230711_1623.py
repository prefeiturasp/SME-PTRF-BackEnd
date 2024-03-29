# Generated by Django 3.1.14 on 2023-07-11 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0338_tipoconta_permite_inativacao'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='funcuerecebimentodenotificacoes',
            options={'default_permissions': (), 'managed': False, 'permissions': (('recebe_notificacao_inicio_periodo_prestacao_de_contas', '[UE] Pode receber Notificação Início Período Prestação De Contas.'), ('recebe_notificacao_pendencia_envio_prestacao_de_contas', '[UE] Pode receber Notificação pendência envio Prestação De Contas.'), ('recebe_notificacao_proximidade_inicio_prestacao_de_contas', '[UE] Pode receber Notificação Proximidade Início Prestação De Contas.'), ('recebe_notificacao_prestacao_de_contas_devolvida_para_acertos', '[UE] Pode receber Notificação Prestação de Contas Devolvida para Acertos'), ('recebe_notificacao_proximidade_fim_periodo_prestacao_de_contas', '[UE] Pode receber Notificação Proximidade Fim Período Prestação de Contas'), ('recebe_notificacao_atraso_entrega_ajustes_prestacao_de_contas', '[UE] Pode receber Notificação Atraso Entrega Ajustes Prestação de Contas'), ('recebe_notificacao_proximidade_fim_prazo_ajustes_prestacao_de_contas', '[UE] Pode receber Notificação Proximidade Fim Prazo Ajustes Prestação de Contas'), ('recebe_notificacao_comentario_em_pc', '[UE] Pode receber Notificação de Comentários'), ('recebe_notificacao_aprovacao_pc', '[UE] Pode receber Notificação Prestação de Contas Aprovada'), ('recebe_notificacao_reprovacao_pc_nao_incluindo_motivos', '[UE] Pode receber Notificação Prestação de Contas Reprovada Não Incluindo Motivos'), ('recebe_notificacao_reprovacao_pc_incluindo_motivos', '[UE] Pode receber Notificação Prestação de Contas Reprovada Incluindo Motivos'), ('recebe_notificacao_automatica_inativacao_conta', '[UE] Pode receber Notificação Encerramento de Conta Bancária')), 'verbose_name': '[UE] Recebimento de notificações', 'verbose_name_plural': '[UE] Recebimento de notificações'},
        ),
        migrations.AddField(
            model_name='parametros',
            name='numero_periodos_consecutivos',
            field=models.PositiveSmallIntegerField(default=2, verbose_name='Quantos períodos consecutivos com saldo zerado para notificar a possibilidade de inativações de contas'),
        ),
        migrations.AlterField(
            model_name='notificacao',
            name='categoria',
            field=models.CharField(choices=[('COMENTARIO_PC', 'Comentário na prestação de contas'), ('ELABORACAO_PC', 'Elaboração de PC'), ('ANALISE_PC', 'Análise de PC'), ('DEVOLUCAO_PC', 'Devolução de PC para ajustes'), ('APROVACAO_PC', 'Aprovação de PC'), ('APROVACAO_RESSALVAS_PC', 'Aprovação de PC com ressalvas'), ('REPROVACAO_PC', 'Reprovação de PC'), ('ERRO_AO_CONCLUIR_PC', 'Erro ao concluir PC'), ('DEVOLUCAO_CONSOLIDADO', 'Devolução de relatório consolidado'), ('COMENTARIO_CONSOLIDADO_DRE', 'Comentário no relatório consolidado'), ('ENCERRAMENTO_CONTA_BANCARIA', 'Encerramento de Conta Bancária')], default='COMENTARIO_PC', max_length=40, verbose_name='Categoria'),
        ),
        migrations.AlterUniqueTogether(
            name='tipoconta',
            unique_together={('nome',)},
        ),
    ]

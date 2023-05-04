from ckeditor.fields import RichTextField
from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase, SingletonModel

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class Parametros(SingletonModel, ModeloBase):
    history = AuditlogHistoryField()
    permite_saldo_conta_negativo = models.BooleanField('Permite saldo negativo em contas?', default=True)

    fique_de_olho = RichTextField(null=True)
    fique_de_olho_relatorio_dre = RichTextField(null=True, verbose_name='Fique de olho (Relatório DRE)')

    desconsiderar_associacoes_nao_iniciadas = models.BooleanField('Desconsiderar associações não iniciadas?',
                                                                  default=False)

    tempo_aguardar_conclusao_pc = models.PositiveSmallIntegerField(
        'Quanto tempo deve-se aguardar a conclusão da PC (segundos)?',
        default=1
    )

    quantidade_tentativas_concluir_pc = models.PositiveSmallIntegerField(
        'Quantas tentativas deve-se permitir para a conclusão da PC (vezes)?',
        default=3
    )

    periodo_de_tempo_tentativas_concluir_pc = models.PositiveSmallIntegerField(
        'Qual o período de tempo das tentativas de conclusão da PC (minutos)?',
        default=120
    )

    tempo_notificar_nao_demonstrados = models.PositiveSmallIntegerField(
        'Tempo para notificação de transações não demonstradas (dias)',
        default=0
    )

    dias_antes_inicio_periodo_pc_para_notificacao = models.PositiveSmallIntegerField(
        'Quantos dias antes do inicio do período de PC, os usuários serão notificados?',
        default=5
    )

    dias_antes_fim_periodo_pc_para_notificacao = models.PositiveSmallIntegerField(
        'Quantos dias antes do fim do período de PC, os usuários serão notificados?',
        default=5
    )

    dias_antes_fim_prazo_ajustes_pc_para_notificacao = models.PositiveSmallIntegerField(
        'Quantos dias antes do fim do prazo para entrega de ajustes de PC, os usuários serão notificados?',
        default=5
    )

    enviar_email_notificacao = models.BooleanField('Envia e-mails de notificação?', default=True)

    texto_pagina_suporte_dre = RichTextField(null=True, verbose_name='Texto da página de suporte (DRE)')

    texto_pagina_suporte_sme = RichTextField(null=True, verbose_name='Texto da página de suporte (SME)')

    texto_pagina_valores_reprogramados_ue = RichTextField(
        null=True, verbose_name='Texto da página de valores reprogramados (UE)')

    texto_pagina_valores_reprogramados_dre = RichTextField(
        null=True, verbose_name='Texto da página de valores reprogramados (DRE)')

    def __str__(self):
        return 'Parâmetros do PTRF'

    class Meta:
        verbose_name = "Parâmetro"
        verbose_name_plural = "01.0) Parâmetros"


auditlog.register(Parametros)

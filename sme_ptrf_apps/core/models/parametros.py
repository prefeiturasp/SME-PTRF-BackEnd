from ckeditor.fields import RichTextField
from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase, SingletonModel


class Parametros(SingletonModel, ModeloBase):
    permite_saldo_conta_negativo = models.BooleanField('Permite saldo negativo em contas?', default=True)

    fique_de_olho = RichTextField(null=True)
    fique_de_olho_relatorio_dre = RichTextField(null=True, verbose_name='Fique de olho (Relatório DRE)')

    tempo_notificar_nao_demonstrados = models.PositiveSmallIntegerField(
        'Tempo para notificação de transações não demonstradas (dias)',
        default=0
    )

    dias_antes_inicio_periodo_pc_para_notificacao = models.PositiveSmallIntegerField(
        'Quantos dias antes do inicio do período de PC, os usuários serão notificados?',
        default=5
    )

    def __str__(self):
        return 'Parâmetros do PTRF'

    class Meta:
        verbose_name = "Parâmetro"
        verbose_name_plural = "01.0) Parâmetros"

from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class ObsDevolucaoRelatorioConsolidadoDRE(ModeloBase):
    # Tipos de devolução Choice
    DEVOLUCAO_TESOURO = 'TESOURO'
    DEVOLUCAO_CONTA = 'CONTA'

    DEVOLUCAO_NOMES = {
        DEVOLUCAO_TESOURO: 'Devolução ao tesouro',
        DEVOLUCAO_CONTA: 'Devolução à conta do PTRF',
    }

    DEVOLUCAO_CHOICES = (
        (DEVOLUCAO_TESOURO, DEVOLUCAO_NOMES[DEVOLUCAO_TESOURO]),
        (DEVOLUCAO_CONTA, DEVOLUCAO_NOMES[DEVOLUCAO_CONTA]),
    )

    dre = models.ForeignKey('core.Unidade', on_delete=models.PROTECT,
                            related_name='observacoes_devolucoes_relatorios_consolidados_da_dre',
                            to_field="codigo_eol", blank=True, null=True, limit_choices_to={'tipo_unidade': 'DRE'})

    tipo_conta = models.ForeignKey('core.TipoConta', on_delete=models.PROTECT, blank=True, null=True)

    periodo = models.ForeignKey('core.Periodo', on_delete=models.PROTECT,
                                related_name='observacoes_devolucoes_relatorios_consolidados_dre_do_periodo')

    tipo_devolucao = models.CharField(
        'Categoria da receita',
        max_length=15,
        choices=DEVOLUCAO_CHOICES,
        default=DEVOLUCAO_CONTA,
        null=True,
    )

    tipo_devolucao_a_conta = models.ForeignKey('receitas.DetalheTipoReceita', on_delete=models.PROTECT,
                                               related_name='observacoes_dre_sobre_devolucoes_a_conta', blank=True,
                                               null=True)

    tipo_devolucao_ao_tesouro = models.ForeignKey('core.TipoDevolucaoAoTesouro', on_delete=models.PROTECT,
                                                  related_name='observacoes_dre_sobre_devolucoes_ao_tesouro',
                                                  blank=True,
                                                  null=True)

    observacao = models.TextField('Observação', max_length=600, blank=True, null=True)

    class Meta:
        verbose_name = 'Observação sobre devoluções de relatório consolidado DRE'
        verbose_name_plural = 'Observações sobre devoluções em relatórios consolidados DREs'

    def __str__(self):
        return self.observacao

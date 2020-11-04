
from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class JustificativaRelatorioConsolidadoDRE(ModeloBase):

    dre = models.ForeignKey('core.Unidade', on_delete=models.PROTECT, related_name='justificativas_relatorios_consolidados_da_dre',
                            to_field="codigo_eol", blank=True, null=True, limit_choices_to={'tipo_unidade': 'DRE'})

    tipo_conta = models.ForeignKey('core.TipoConta', on_delete=models.PROTECT, blank=True, null=True)

    periodo = models.ForeignKey('core.Periodo', on_delete=models.PROTECT,
                                related_name='justificativas_relatorios_consolidados_dre_do_periodo')

    texto = models.TextField('Justificativa', max_length=600, blank=True, null=True)

    class Meta:
        verbose_name = 'Justificativa de relatório consolidado DRE'
        verbose_name_plural = 'Justificativas de relatórios consolidados DREs'
        unique_together = ['dre', 'tipo_conta', 'periodo']

    def __str__(self):
        return self.texto

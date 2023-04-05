
from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class JustificativaRelatorioConsolidadoDRE(ModeloBase):
    history = AuditlogHistoryField()
    dre = models.ForeignKey('core.Unidade', on_delete=models.PROTECT, related_name='justificativas_relatorios_consolidados_da_dre',
                            to_field="codigo_eol", blank=True, null=True, limit_choices_to={'tipo_unidade': 'DRE'})

    tipo_conta = models.ForeignKey('core.TipoConta', on_delete=models.PROTECT, blank=True, null=True)

    periodo = models.ForeignKey('core.Periodo', on_delete=models.PROTECT,
                                related_name='justificativas_relatorios_consolidados_dre_do_periodo')

    texto = models.TextField('Justificativa', max_length=600, blank=True, null=True)

    consolidado_dre = models.ForeignKey('ConsolidadoDRE', on_delete=models.CASCADE,
                                        related_name='justificativas_relatorios_consolidados_dre_do_consolidado_dre',
                                        blank=True, null=True)

    eh_retificacao = models.BooleanField('É uma justificativa de retificação ?', blank=True, null=True, default=False)

    class Meta:
        verbose_name = 'Justificativa de relatório consolidado DRE'
        verbose_name_plural = 'Justificativas de relatórios consolidados DREs'

    def __str__(self):
        return self.texto


auditlog.register(JustificativaRelatorioConsolidadoDRE)

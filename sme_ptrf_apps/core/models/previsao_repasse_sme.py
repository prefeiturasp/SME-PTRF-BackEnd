from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase

# TODO Adicionar divisão livre, custeio e capital e conta


class PrevisaoRepasseSme(ModeloBase):
    history = AuditlogHistoryField()

    periodo = models.ForeignKey('Periodo', on_delete=models.PROTECT, related_name='previsoes_repasse_sme')

    associacao = models.ForeignKey('Associacao', on_delete=models.PROTECT,
                                   related_name='previsoes_de_repasse_sme_para_a_associacao',
                                   blank=True, null=True)

    valor_capital = models.DecimalField('Valor Capital', max_digits=20, decimal_places=2, default=0)

    valor_custeio = models.DecimalField('Valor Custeio', max_digits=20, decimal_places=2, default=0)

    valor_livre = models.DecimalField('Valor Livre Aplicação', max_digits=20, decimal_places=2, default=0)

    conta_associacao = models.ForeignKey('ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='previsoes_de_repasse_sme_para_a_conta', blank=True, null=True)

    @property
    def valor_total(self):
        return self.valor_custeio + self.valor_capital + self.valor_livre

    def __str__(self):
        return f"{self.periodo.referencia} - {self.associacao}"

    class Meta:
        verbose_name = "Previsão repasse SME"
        verbose_name_plural = "12.0) Previsões de repasse"
        unique_together = ['associacao', 'periodo', 'conta_associacao']


auditlog.register(PrevisaoRepasseSme)

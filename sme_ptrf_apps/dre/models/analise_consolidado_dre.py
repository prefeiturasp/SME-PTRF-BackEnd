from django.db import models
from ...core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class AnaliseConsolidadoDre(ModeloBase):
    history = AuditlogHistoryField()

    consolidado_dre = models.ForeignKey(
        'ConsolidadoDRE', on_delete=models.CASCADE,
        related_name='analises_do_consolidado_dre',
    )

    def __str__(self):
        return f"{self.consolidado_dre.dre} - {self.consolidado_dre.periodo} - Análise #{self.pk}"

    class Meta:
        verbose_name = "Análise consolidado DRE"
        verbose_name_plural = "Análises consolidados DRE"


auditlog.register(AnaliseConsolidadoDre)

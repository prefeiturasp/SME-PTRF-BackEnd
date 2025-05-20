from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class BemProduzidoDespesa(ModeloBase):
    history = AuditlogHistoryField()

    bem_produzido = models.ForeignKey(
        'BemProduzido',
        on_delete=models.CASCADE,
        related_name='despesas'
    )

    despesa = models.ForeignKey('despesas.Despesa', on_delete=models.CASCADE, related_name='despesa_bem_produzido', blank=True, null=True)

    class Meta:
        verbose_name = 'Despesa de bem produzido'
        verbose_name_plural = 'Despesas de bens produzidos'

    def __str__(self):
        return f"Despesa {self.despesa.id} do bem produzido {self.bem_produzido}"

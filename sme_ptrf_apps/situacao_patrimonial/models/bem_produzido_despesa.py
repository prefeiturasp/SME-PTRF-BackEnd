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

    despesa = models.ForeignKey('despesas.Despesa', on_delete=models.CASCADE,
                                related_name='despesa_bem_produzido', blank=True, null=True)

    valor_recurso_proprio_utilizado = models.DecimalField(
        'Valor recurso próprio utilizado', max_digits=8, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Despesa de bem produzido'
        verbose_name_plural = 'Despesas de bens produzidos'

    def __str__(self):
        return f"Despesa {self.id} - ({self.despesa.id}) do {self.bem_produzido}"


auditlog.register(BemProduzidoDespesa)

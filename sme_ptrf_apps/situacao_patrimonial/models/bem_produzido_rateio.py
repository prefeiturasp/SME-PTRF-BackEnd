from django.db import models
from django.db.models import Sum
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class BemProduzidoRateio(ModeloBase):
    history = AuditlogHistoryField()

    bem_produzido_despesa = models.ForeignKey(
        'BemProduzidoDespesa',
        on_delete=models.CASCADE,
        related_name='rateios'
    )

    rateio = models.ForeignKey(
        'despesas.RateioDespesa',
        on_delete=models.CASCADE,
        related_name='rateio_bem_produzido',
        blank=True,
        null=True
    )

    valor_utilizado = models.DecimalField('Valor utilizado', max_digits=8, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Rateio de despesa de bem produzido'
        verbose_name_plural = 'Rateios de despesa de bem produzido'

    def __str__(self):
        return f"Rateio {self.id} - ({self.rateio.id}) da {self.bem_produzido_despesa}"

    @staticmethod
    def valor_disponivel_por_rateio(rateio, bem_produzido_rateio=None):
        bem_produzido_rateios = BemProduzidoRateio.objects.filter(rateio=rateio)

        if bem_produzido_rateio:
            bem_produzido_rateios = bem_produzido_rateios.exclude(uuid=bem_produzido_rateio.uuid)

        total_utilizado = bem_produzido_rateios.aggregate(
            total=Sum('valor_utilizado')
        )['total'] or 0

        return rateio.valor_rateio - total_utilizado

    @staticmethod
    def valor_total_utilizado(bem_produzido):
        bem_produzido_rateios = BemProduzidoRateio.objects.filter(bem_produzido_despesa__bem_produzido=bem_produzido)

        total_utilizado = bem_produzido_rateios.aggregate(
            total=Sum('valor_utilizado')
        )['total'] or 0

        return total_utilizado


auditlog.register(BemProduzidoRateio)

from django.db import models
from django.db.models import Sum
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.situacao_patrimonial.models.bem_produzido_rateio import BemProduzidoRateio


class BemProduzido(ModeloBase):
    STATUS_COMPLETO = 'COMPLETO'
    STATUS_INCOMPLETO = 'INCOMPLETO'

    STATUS_NOMES = {
        STATUS_COMPLETO: 'Completo',
        STATUS_INCOMPLETO: 'Rascunho',
    }

    STATUS_CHOICES = (
        (STATUS_COMPLETO, STATUS_NOMES[STATUS_COMPLETO]),
        (STATUS_INCOMPLETO, STATUS_NOMES[STATUS_INCOMPLETO]),
    )

    history = AuditlogHistoryField()

    associacao = models.ForeignKey('core.Associacao', on_delete=models.PROTECT,
                                   related_name='bens_produzidos_associacao', blank=True, null=True)

    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_INCOMPLETO
    )

    class Meta:
        verbose_name = 'Bem produzido'
        verbose_name_plural = 'Bens produzidos'

    def __str__(self):
        return f"Bem produzido {self.pk}"

    def completar(self):
        if self.status != BemProduzido.STATUS_COMPLETO:
            self.status = BemProduzido.STATUS_COMPLETO
            self.save(update_fields=["status"])

    def rascunhar(self):
        if self.status != BemProduzido.STATUS_INCOMPLETO:
            self.status = BemProduzido.STATUS_INCOMPLETO
            self.save(update_fields=["status"])

    def valor_total_utilizado(self):
        """
        Calcula o valor total utilizado somando os valores de rateios
        e os recursos próprios utilizados.
        """

        # Total dos valores utilizados nos rateios
        total_rateios_utilizados = (
            BemProduzidoRateio.objects
            .filter(bem_produzido_despesa__bem_produzido=self)
            .aggregate(total=Sum('valor_utilizado'))
            .get('total') or 0
        )

        # Total dos valores utilizados de recursos próprios
        total_recursos_proprios_utilizados = (
            self.despesas
            .aggregate(total=Sum('valor_recurso_proprio_utilizado'))
            .get('total') or 0
        )

        return total_rateios_utilizados + total_recursos_proprios_utilizados


auditlog.register(BemProduzido)

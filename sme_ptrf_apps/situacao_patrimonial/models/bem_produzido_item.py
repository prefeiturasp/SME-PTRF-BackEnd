from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class BemProduzidoItem(ModeloBase):
    history = AuditlogHistoryField()

    bem_produzido = models.ForeignKey(
        'BemProduzido',
        on_delete=models.CASCADE,
        related_name='items'
    )

    especificacao_do_bem = models.ForeignKey(
        'despesas.EspecificacaoMaterialServico', on_delete=models.PROTECT, blank=True, null=True)

    num_processo_incorporacao = models.CharField(
        'Nº do processo de incorporação', max_length=100, default='', blank=True, null=True)

    quantidade = models.IntegerField('Quantidade', default=0, blank=True, null=True)

    valor_individual = models.DecimalField('Valor individual', max_digits=10,
                                           decimal_places=2, default=0, blank=True, null=True)

    class Meta:
        verbose_name = 'Item de bem produzido'
        verbose_name_plural = 'Itens de bens produzidos'

    def __str__(self):
        return f"Item {self.pk} do {self.bem_produzido}"

    @property
    def valor_total(self):
        if self.quantidade and self.valor_individual:
            return self.quantidade * self.valor_individual
        return None


auditlog.register(BemProduzidoItem)

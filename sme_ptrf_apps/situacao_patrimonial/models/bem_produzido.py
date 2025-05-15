from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase

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

class BemProduzido(ModeloBase):
    history = AuditlogHistoryField()

    associacao = models.ForeignKey('core.Associacao', on_delete=models.PROTECT, related_name='bens_produzidos_associacao', blank=True, null=True)

    especificacao_do_bem = models.ForeignKey('despesas.EspecificacaoMaterialServico', on_delete=models.PROTECT, blank=True, null=True)

    num_processo_incorporacao = models.CharField('Nº do processo de incorporação', max_length=100, default='', blank=True, null=True)

    quantidade = models.IntegerField('Quantidade', default=0, blank=True, null=True)

    valor_individual = models.DecimalField('Valor individual', max_digits=10, decimal_places=2, default=0, blank=True, null=True)

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


auditlog.register(BemProduzido)

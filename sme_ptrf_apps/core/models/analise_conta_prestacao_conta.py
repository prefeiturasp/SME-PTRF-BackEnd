from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class AnaliseContaPrestacaoConta(ModeloBase):
    history = AuditlogHistoryField()

    prestacao_conta = models.ForeignKey('PrestacaoConta', on_delete=models.CASCADE,
                                        related_name='analises_de_conta_da_prestacao')

    conta_associacao = models.ForeignKey('ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='analises_de_conta_da_conta', blank=True, null=True)

    data_extrato = models.DateField('data do extrato', blank=True, null=True)

    saldo_extrato = models.DecimalField('saldo do extrato', max_digits=12, decimal_places=2, blank=True, null=True)

    analise_prestacao_conta = models.ForeignKey('AnalisePrestacaoConta', on_delete=models.CASCADE,
                                                related_name='analises_de_extratos', null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.conta_associacao} - {self.data_extrato} - {self.saldo_extrato}"

    class Meta:
        verbose_name = "Análise de conta de prestação de contas"
        verbose_name_plural = "09.8) Análises de contas de prestações de contas"


auditlog.register(AnaliseContaPrestacaoConta)

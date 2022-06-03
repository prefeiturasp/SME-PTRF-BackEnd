from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class DevolucaoPrestacaoConta(ModeloBase):
    history = AuditlogHistoryField()

    prestacao_conta = models.ForeignKey('PrestacaoConta', on_delete=models.CASCADE,
                                        related_name='devolucoes_da_prestacao')

    data = models.DateField('data da devolução')

    data_limite_ue = models.DateField('data limite para a ue')

    data_retorno_ue = models.DateField('data do retorno pela ue', null=True, blank=True)

    def __str__(self):
        return f"{self.data} - {self.data_limite_ue}"

    class Meta:
        verbose_name = "Devolução de prestação de contas"
        verbose_name_plural = "09.7) Devoluções de prestações de contas"


auditlog.register(DevolucaoPrestacaoConta)

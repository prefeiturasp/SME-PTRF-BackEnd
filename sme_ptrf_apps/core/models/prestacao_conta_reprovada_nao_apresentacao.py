from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class PrestacaoContaReprovadaNaoApresentacao(ModeloBase):
    history = AuditlogHistoryField()

    periodo = models.ForeignKey(
        'Periodo',
        on_delete=models.PROTECT,
        related_name='prestacoes_de_conta_reprovadas_por_nao_apresentacao_do_periodo'
    )

    associacao = models.ForeignKey(
        'Associacao',
        on_delete=models.PROTECT,
        related_name='prestacoes_de_conta_reprovadas_por_nao_apresentacao_da_associacao',
    )

    data_de_reprovacao = models.DateTimeField(
        "Data da reprovação",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Prestação de conta reprovada não apresentação"
        verbose_name_plural = "09.0.1) Prestações de contas reprovadas não apresentação"
        unique_together = ['associacao', 'periodo']

    def __str__(self):
        return f"{self.periodo}"


auditlog.register(PrestacaoContaReprovadaNaoApresentacao)

from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class SolicitacaoDevolucaoAoTesouro(ModeloBase):
    history = AuditlogHistoryField()

    solicitacao_acerto_lancamento = models.OneToOneField(
        'SolicitacaoAcertoLancamento',
        on_delete=models.CASCADE,
        related_name='solicitacao_devolucao_ao_tesouro'
    )

    tipo = models.ForeignKey(
        'TipoDevolucaoAoTesouro',
        on_delete=models.PROTECT,
        related_name='solicitacoes_devolucoes_ao_tesouro_do_tipo'
    )

    devolucao_total = models.BooleanField('Devolução total?', default=True)

    valor = models.DecimalField('Valor', max_digits=8, decimal_places=2, default=0)

    motivo = models.TextField('Motivo', max_length=600, blank=True, null=True)

    def __str__(self):
        return f"#{self.id} {self.valor} - {self.tipo}"

    class Meta:
        verbose_name = "Solicitação de Devolução ao Tesouro"
        verbose_name_plural = "16.8) Solicitações de Devolução ao Tesouro"


auditlog.register(SolicitacaoDevolucaoAoTesouro)

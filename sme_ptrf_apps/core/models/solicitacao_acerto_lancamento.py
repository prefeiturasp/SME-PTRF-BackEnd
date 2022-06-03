from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class SolicitacaoAcertoLancamento(ModeloBase):
    history = AuditlogHistoryField()

    analise_lancamento = models.ForeignKey('AnaliseLancamentoPrestacaoConta', on_delete=models.CASCADE,
                                           related_name='solicitacoes_de_ajuste_da_analise')

    tipo_acerto = models.ForeignKey('TipoAcertoLancamento', on_delete=models.PROTECT,
                                    related_name='+')

    devolucao_ao_tesouro = models.ForeignKey('DevolucaoAoTesouro', on_delete=models.SET_NULL,
                                             related_name='solicitacao_de_ajuste_da_devolucao',
                                             null=True, blank=True)

    detalhamento = models.TextField('Motivo', max_length=600, blank=True, default="")

    def __str__(self):
        return f"{self.tipo_acerto} - {self.detalhamento}"

    class Meta:
        verbose_name = "Solicitação de acerto em lançamento"
        verbose_name_plural = "16.3) Solicitações de acertos em lançamentos"


auditlog.register(SolicitacaoAcertoLancamento)

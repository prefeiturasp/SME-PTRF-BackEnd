from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class SolicitacaoAcertoLancamento(ModeloBase):
    history = AuditlogHistoryField()

    # Status realizacao choices
    STATUS_REALIZACAO_PENDENTE = 'PENDENTE'
    STATUS_REALIZACAO_REALIZADO = 'REALIZADO'
    STATUS_REALIZACAO_JUSTIFICADO = 'JUSTIFICADO'

    STATUS_REALIZACAO_NOMES = {
        STATUS_REALIZACAO_PENDENTE: 'Pendente',
        STATUS_REALIZACAO_REALIZADO: 'Realizado',
        STATUS_REALIZACAO_JUSTIFICADO: 'Justificado'
    }

    STATUS_REALIZACAO_CHOICES = (
        (STATUS_REALIZACAO_PENDENTE, STATUS_REALIZACAO_NOMES[STATUS_REALIZACAO_PENDENTE]),
        (STATUS_REALIZACAO_REALIZADO, STATUS_REALIZACAO_NOMES[STATUS_REALIZACAO_REALIZADO]),
        (STATUS_REALIZACAO_JUSTIFICADO, STATUS_REALIZACAO_NOMES[STATUS_REALIZACAO_JUSTIFICADO])
    )

    analise_lancamento = models.ForeignKey('AnaliseLancamentoPrestacaoConta', on_delete=models.CASCADE,
                                           related_name='solicitacoes_de_ajuste_da_analise')

    tipo_acerto = models.ForeignKey('TipoAcertoLancamento', on_delete=models.PROTECT,
                                    related_name='+')

    # TODO Remover esse campo após conclusão da mudança em solicitações de dev.tesouro
    devolucao_ao_tesouro = models.ForeignKey('DevolucaoAoTesouro', on_delete=models.SET_NULL,
                                             related_name='solicitacao_de_ajuste_da_devolucao',
                                             null=True, blank=True)

    detalhamento = models.TextField('Motivo', max_length=600, blank=True, default="")

    copiado = models.BooleanField('Solicitação copiada ?', default=False)

    status_realizacao = models.CharField(
        'Status de realização',
        max_length=15,
        choices=STATUS_REALIZACAO_CHOICES,
        default=STATUS_REALIZACAO_PENDENTE
    )

    justificativa = models.TextField('Justificativa', max_length=300, blank=True, null=True, default=None)

    esclarecimentos = models.TextField('Esclarecimentos', max_length=300, blank=True, null=True, default=None)

    def __str__(self):
        return f"{self.tipo_acerto} - {self.detalhamento}"

    def altera_status_realizacao(self, novo_status, justificativa=None):
        self.justificativa = justificativa
        self.status_realizacao = novo_status
        self.save()

    class Meta:
        verbose_name = "Solicitação de acerto em lançamento"
        verbose_name_plural = "16.3) Solicitações de acertos em lançamentos"


auditlog.register(SolicitacaoAcertoLancamento)

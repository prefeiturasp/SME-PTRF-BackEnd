from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class SolicitacaoAcertoDocumento(ModeloBase):
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

    analise_documento = models.ForeignKey('AnaliseDocumentoPrestacaoConta', on_delete=models.CASCADE,
                                          related_name='solicitacoes_de_ajuste_da_analise')

    tipo_acerto = models.ForeignKey('TipoAcertoDocumento', on_delete=models.PROTECT,
                                    related_name='+')

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

    despesa_incluida = models.ForeignKey('despesas.Despesa', on_delete=models.SET_NULL,
                                         related_name='solicitacao_acerto_de_documento_que_incluiu_a_despesa',
                                         blank=True, null=True)

    receita_incluida = models.ForeignKey('receitas.Receita', on_delete=models.SET_NULL,
                                         related_name='solicitacao_acerto_de_documento_que_incluiu_a_receita',
                                         blank=True, null=True)

    def __str__(self):
        return f"{self.tipo_acerto} - {self.detalhamento}"

    def altera_status_realizacao(self, novo_status, justificativa=None):
        self.justificativa = justificativa
        self.status_realizacao = novo_status
        self.save()

    def incluir_esclarecimentos(self, esclarecimentos):
        self.esclarecimentos = esclarecimentos
        self.save()
        return self


    class Meta:
        verbose_name = "Solicitação de acerto em documento"
        verbose_name_plural = "16.7) Solicitações de acertos em documentos"


auditlog.register(SolicitacaoAcertoDocumento)

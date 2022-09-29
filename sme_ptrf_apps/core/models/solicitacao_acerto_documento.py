from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class SolicitacaoAcertoDocumento(ModeloBase):
    history = AuditlogHistoryField()

    analise_documento = models.ForeignKey('AnaliseDocumentoPrestacaoConta', on_delete=models.CASCADE,
                                          related_name='solicitacoes_de_ajuste_da_analise')

    tipo_acerto = models.ForeignKey('TipoAcertoDocumento', on_delete=models.PROTECT,
                                    related_name='+')

    detalhamento = models.TextField('Motivo', max_length=600, blank=True, default="")

    copiado = models.BooleanField('Solicitação copiada ?', default=False)

    def __str__(self):
        return f"{self.tipo_acerto} - {self.detalhamento}"

    class Meta:
        verbose_name = "Solicitação de acerto em documento"
        verbose_name_plural = "16.7) Solicitações de acertos em documentos"


auditlog.register(SolicitacaoAcertoDocumento)

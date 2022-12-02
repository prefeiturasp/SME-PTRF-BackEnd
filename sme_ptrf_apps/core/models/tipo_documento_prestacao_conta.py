from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class TipoDocumentoPrestacaoConta(ModeloIdNome):
    history = AuditlogHistoryField()

    documento_por_conta = models.BooleanField('É um documento por tipo de conta?', default=False)
    e_relacao_bens = models.BooleanField('O documento é uma Relação de Bens?', default=False)

    @classmethod
    def lista_documentos(cls):
        documentos = TipoDocumentoPrestacaoConta.objects.all().order_by('-nome').values('id', 'nome')
        return documentos

    class Meta:
        verbose_name = "Documento de prestação de contas"
        verbose_name_plural = "16.4) Documentos de prestação de contas"


auditlog.register(TipoDocumentoPrestacaoConta)

from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class TipoDocumentoPrestacaoConta(ModeloIdNome):
    history = AuditlogHistoryField()

    documento_por_conta = models.BooleanField('Documento por tipo de conta?', default=False)

    class Meta:
        verbose_name = "Documento de prestação de contas"
        verbose_name_plural = "16.4) Documentos de prestação de contas"


auditlog.register(TipoDocumentoPrestacaoConta)

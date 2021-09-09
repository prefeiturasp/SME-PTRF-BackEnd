from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from .tipo_documento_prestacao_conta import TipoDocumentoPrestacaoConta


class TipoAcertoDocumento(ModeloIdNome):
    tipos_documento_prestacao = models.ManyToManyField(TipoDocumentoPrestacaoConta, blank=True)
    history = AuditlogHistoryField()

    class Meta:
        verbose_name = "Tipo de acerto em documentos"
        verbose_name_plural = "16.5) Tipos de acerto em documentos"


auditlog.register(TipoAcertoDocumento)

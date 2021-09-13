from sme_ptrf_apps.core.models_abstracts import ModeloIdNome

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class TipoDocumentoPrestacaoConta(ModeloIdNome):
    history = AuditlogHistoryField()

    class Meta:
        verbose_name = "Documento de prestação de contas"
        verbose_name_plural = "16.4) Documentos de prestação de contas"


auditlog.register(TipoDocumentoPrestacaoConta)

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class TipoDevolucaoAoTesouro(ModeloIdNome):
    history = AuditlogHistoryField()

    class Meta:
        verbose_name = "Tipo de devolução ao tesouro"
        verbose_name_plural = "11.0) Tipos de devolução ao tesouro"


auditlog.register(TipoDevolucaoAoTesouro)

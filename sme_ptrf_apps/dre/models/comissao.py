from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class Comissao(ModeloIdNome):
    history = AuditlogHistoryField()

    class Meta:
        verbose_name = "Comissão"
        verbose_name_plural = "Comissões"


auditlog.register(Comissao)

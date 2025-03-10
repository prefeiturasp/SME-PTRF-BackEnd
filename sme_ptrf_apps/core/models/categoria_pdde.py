from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class CategoriaPdde(ModeloIdNome):
    history = AuditlogHistoryField()

    class Meta:
        verbose_name = "Categoria PDDE"
        verbose_name_plural = "20.1) Categoria PDDE"
        unique_together = ['nome',]


auditlog.register(CategoriaPdde)

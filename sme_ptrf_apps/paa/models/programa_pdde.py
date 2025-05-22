from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class ProgramaPdde(ModeloIdNome):
    history = AuditlogHistoryField()

    class Meta:
        verbose_name = "Programa PDDE"
        verbose_name_plural = "Programas PDDE"
        unique_together = ['nome',]


auditlog.register(ProgramaPdde)

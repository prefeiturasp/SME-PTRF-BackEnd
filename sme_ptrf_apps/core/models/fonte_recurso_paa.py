from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class FonteRecursoPaa(ModeloIdNome):
    history = AuditlogHistoryField()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Fonte Recursos PAA"
        verbose_name_plural = "22.0) Fonte Recursos PAA"


auditlog.register(FonteRecursoPaa)

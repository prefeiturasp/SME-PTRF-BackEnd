from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class TipoTransacao(ModeloIdNome):
    history = AuditlogHistoryField()
    tem_documento = models.BooleanField("Tem documento?", default=False)

    class Meta:
        verbose_name = "Tipo de transação"
        verbose_name_plural = "Tipos de transação"


auditlog.register(TipoTransacao)

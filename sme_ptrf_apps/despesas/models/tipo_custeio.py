from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloIdNome

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class TipoCusteio(ModeloIdNome):
    history = AuditlogHistoryField()
    eh_tributos_e_tarifas = models.BooleanField('É Tributos e Tarifas?', default=False)

    class Meta:
        verbose_name = "Tipo de despesa de custeio"
        verbose_name_plural = "Tipos de despesa de custeio"
        unique_together = ['nome', ]


auditlog.register(TipoCusteio)

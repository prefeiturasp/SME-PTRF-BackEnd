from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class MotivoPagamentoAntecipado(ModeloBase):
    history = AuditlogHistoryField()

    lookup_field = 'uuid'
    motivo = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Motivo de pagamento antecipado'
        verbose_name_plural = 'Motivos de pagamento antecipado'

    def __str__(self):
        return self.motivo


auditlog.register(MotivoPagamentoAntecipado)

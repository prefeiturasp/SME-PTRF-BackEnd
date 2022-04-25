from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class MotivoEstorno(ModeloBase):
    history = AuditlogHistoryField()
    lookup_field = 'uuid'
    motivo = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Motivo de estorno'
        verbose_name_plural = 'Motivos de estorno'
        unique_together = ['motivo', ]

    def __str__(self):
        return self.motivo


auditlog.register(MotivoEstorno)

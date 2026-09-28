from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class MotivoReprovacao(ModeloBase):
    history = AuditlogHistoryField()

    lookup_field = 'uuid'
    motivo = models.CharField(max_length=200)
    recurso = models.ForeignKey('core.Recurso', on_delete=models.PROTECT, verbose_name='recurso', related_name='motivos_reprovacao')

    class Meta:
        verbose_name = 'Motivo de rejeição'
        verbose_name_plural = 'Motivos de rejeição'
        unique_together = ['motivo', 'recurso']

    def __str__(self):
        return self.motivo


auditlog.register(MotivoReprovacao)

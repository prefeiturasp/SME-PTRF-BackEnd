from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class MotivoAprovacaoRessalva(ModeloBase):
    history = AuditlogHistoryField()
    lookup_field = 'uuid'
    motivo = models.CharField(max_length=200)
    recurso = models.ForeignKey(
        'core.Recurso',
        on_delete=models.PROTECT,
        related_name='motivo_aprovacao_ressalva_recurso',
        null=False,
        blank=False,
        verbose_name='Recurso'
    )

    class Meta:
        verbose_name = 'Motivo de aprovação com ressalva'
        verbose_name_plural = 'Motivos de aprovação com ressalva'
        unique_together = ('motivo', 'recurso')

    def __str__(self):
        return self.motivo


auditlog.register(MotivoAprovacaoRessalva)

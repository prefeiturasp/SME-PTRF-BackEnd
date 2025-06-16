from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase

class BemProduzido(ModeloBase):
    STATUS_COMPLETO = 'COMPLETO'
    STATUS_INCOMPLETO = 'INCOMPLETO'

    STATUS_NOMES = {
        STATUS_COMPLETO: 'Completo',
        STATUS_INCOMPLETO: 'Rascunho',
    }

    STATUS_CHOICES = (
        (STATUS_COMPLETO, STATUS_NOMES[STATUS_COMPLETO]),
        (STATUS_INCOMPLETO, STATUS_NOMES[STATUS_INCOMPLETO]),
    )
    
    history = AuditlogHistoryField()

    associacao = models.ForeignKey('core.Associacao', on_delete=models.PROTECT, related_name='bens_produzidos_associacao', blank=True, null=True)

    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_INCOMPLETO
    )

    class Meta:
        verbose_name = 'Bem produzido'
        verbose_name_plural = 'Bens produzidos'

    def __str__(self):
        return f"Bem produzido {self.pk}"


auditlog.register(BemProduzido)

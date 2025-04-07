from datetime import date

from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.core.models import FonteRecursoPaa, Associacao


class RecursoProprioPaa(ModeloBase):
    history = AuditlogHistoryField()
    
    fonte_recurso = models.ForeignKey(FonteRecursoPaa, on_delete=models.PROTECT, related_name='recurso_proprio')
    associacao = models.ForeignKey(Associacao, on_delete=models.PROTECT, related_name='associacao')
    data_prevista = models.DateField(default=date.today)
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField('Valor', max_digits=20, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Recurso Próprio PAA"
        verbose_name_plural = "23.0) Recursos Próprios PAA"

auditlog.register(RecursoProprioPaa)

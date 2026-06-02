from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class DetalheTipoReceita(ModeloIdNome):
    history = AuditlogHistoryField()
    tipo_receita = models.ForeignKey('TipoReceita', on_delete=models.PROTECT, blank=True, null=True,
                                     related_name='detalhes_tipo_receita')

    class Meta:
        verbose_name = 'Detalhe de tipo de receita'
        verbose_name_plural = 'Detalhes de tipos de receita'

    def __str__(self):
        return self.nome

    @classmethod
    def filter_by_recurso(cls, queryset, recurso):
        objects = queryset if queryset else cls.objects

        return objects.filter(tipo_receita__recurso=recurso)


auditlog.register(DetalheTipoReceita)

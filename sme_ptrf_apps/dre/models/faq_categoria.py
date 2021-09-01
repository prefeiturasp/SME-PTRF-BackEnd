from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class FaqCategoria(ModeloBase):
    history = AuditlogHistoryField()
    lookup_field = 'uuid'
    nome = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Faq - Categoria'
        verbose_name_plural = 'Faqs - Categorias'

    def __str__(self):
        return self.nome


auditlog.register(FaqCategoria)

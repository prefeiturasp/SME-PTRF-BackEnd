from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome


class DocumentoAdicional(ModeloIdNome):
    history = AuditlogHistoryField()

    arquivo = models.FileField(null=True, blank=True, verbose_name='Arquivo')

    class Meta:
        verbose_name = "Documento adicional"
        verbose_name_plural = "Documentos Adicionais"
        unique_together = ['nome']


auditlog.register(DocumentoAdicional)

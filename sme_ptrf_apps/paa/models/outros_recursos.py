from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class OutroRecurso(ModeloIdNome):
    history = AuditlogHistoryField()

    aceita_capital = models.BooleanField('Aceita capital?', default=False)
    aceita_custeio = models.BooleanField('Aceita custeio?', default=False)
    aceita_livre_aplicacao = models.BooleanField('Aceita livre aplicação?', default=False)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Outro Recurso"
        verbose_name_plural = "Outros Recursos"
        unique_together = ['nome',]


auditlog.register(OutroRecurso)

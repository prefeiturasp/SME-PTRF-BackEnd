from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from sme_ptrf_apps.paa.models.programa_pdde import ProgramaPdde


class AcaoPdde(ModeloIdNome):
    history = AuditlogHistoryField()
    programa = models.ForeignKey(ProgramaPdde, on_delete=models.SET_NULL, null=True, blank=True)
    aceita_capital = models.BooleanField('Aceita capital?', default=False)
    aceita_custeio = models.BooleanField('Aceita custeio?', default=False)
    aceita_livre_aplicacao = models.BooleanField('Aceita livre aplicação?', default=False)

    def programa_objeto(self):
        return self.programa

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Ação PDDE"
        verbose_name_plural = "Ações PDDE"
        unique_together = ('nome', 'programa')


auditlog.register(AcaoPdde)

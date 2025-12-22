from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from sme_ptrf_apps.paa.models.programa_pdde import ProgramaPdde


class AcaoPdde(ModeloIdNome):
    history = AuditlogHistoryField()

    # Status Choice
    STATUS_ATIVA = 'ATIVA'
    STATUS_INATIVA = 'INATIVA'

    STATUS_NOMES = {
        STATUS_ATIVA: 'Ativa',
        STATUS_INATIVA: 'Inativa',
    }
    STATUS_CHOICES = (
        (STATUS_ATIVA, STATUS_NOMES[STATUS_ATIVA]),
        (STATUS_INATIVA, STATUS_NOMES[STATUS_INATIVA]),
    )

    programa = models.ForeignKey(ProgramaPdde, on_delete=models.SET_NULL, null=True, blank=True)
    aceita_capital = models.BooleanField('Aceita capital?', default=False)
    aceita_custeio = models.BooleanField('Aceita custeio?', default=False)
    aceita_livre_aplicacao = models.BooleanField('Aceita livre aplicação?', default=False)
    status = models.CharField(
        'status',
        max_length=7,
        choices=STATUS_CHOICES,
        default=STATUS_ATIVA
    )

    def programa_objeto(self):
        return self.programa

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Ação PDDE"
        verbose_name_plural = "Ações PDDE"


auditlog.register(AcaoPdde)

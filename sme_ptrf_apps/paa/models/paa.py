from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.paa.models import PeriodoPaa


class Paa(ModeloBase):
    history = AuditlogHistoryField()
    periodo_paa = models.ForeignKey(PeriodoPaa, on_delete=models.PROTECT, verbose_name='Período PAA',
                                    blank=False, null=True)
    associacao = models.ForeignKey(Associacao, on_delete=models.PROTECT, verbose_name='Associação',
                                   blank=False, null=True)

    def periodo_paa_objeto(self):
        return self.periodo_paa

    class Meta:
        verbose_name = 'PAA'
        verbose_name_plural = 'PAA`s'
        unique_together = ('periodo_paa', 'associacao')

    def __str__(self):
        return f'{self.periodo_paa} - {self.associacao}'


auditlog.register(Paa)

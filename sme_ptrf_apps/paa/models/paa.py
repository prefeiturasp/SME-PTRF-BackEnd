from django.db import models
from datetime import datetime
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.paa.models.periodo_paa import PeriodoPaa


class Paa(ModeloBase):
    history = AuditlogHistoryField()
    periodo_paa = models.ForeignKey(PeriodoPaa, on_delete=models.PROTECT, verbose_name='Período PAA',
                                    blank=False, null=True)
    associacao = models.ForeignKey(Associacao, on_delete=models.PROTECT, verbose_name='Associação',
                                   blank=False, null=True)
    saldo_congelado_em = models.DateTimeField(
        verbose_name="Saldo congelado em", blank=True, null=True)

    def periodo_paa_objeto(self):
        return self.periodo_paa

    def set_congelar_saldo(self):
        self.saldo_congelado_em = datetime.now()
        self.save()

    def set_descongelar_saldo(self):
        self.saldo_congelado_em = None
        self.save()

    class Meta:
        verbose_name = 'PAA'
        verbose_name_plural = 'PAA`s'
        unique_together = ('periodo_paa', 'associacao')

    def __str__(self):
        return f'{self.periodo_paa} - {self.associacao}'


auditlog.register(Paa)

from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase, SingletonModel
from ..choices import Mes


class ParametroPaa(SingletonModel, ModeloBase):
    history = AuditlogHistoryField()
    mes_elaboracao_paa = models.IntegerField(choices=Mes.choices, verbose_name='Mês de elaboração do PAA',
                                             help_text='indica o mês que pode ser iniciada a elaboração do PAA',
                                             blank=False, null=True)

    class Meta:
        verbose_name = 'Parâmetro do PAA'
        verbose_name_plural = 'Parâmetros do PAA'

    def __str__(self):
        return 'Parâmetros do PAA'


auditlog.register(ParametroPaa)

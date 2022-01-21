from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase, SingletonModel

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class ParametrosDre(SingletonModel, ModeloBase):
    history = AuditlogHistoryField()
    comissao_exame_contas = models.ForeignKey('Comissao', on_delete=models.CASCADE,
                                              related_name='comissao_com_exame_contas')

    class Meta:
        verbose_name = "Parâmetro DRE"
        verbose_name_plural = "Parâmetros DRE"


auditlog.register(ParametrosDre)

from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase, SingletonModel

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class ParametrosDre(SingletonModel, ModeloBase):
    history = AuditlogHistoryField()
    comissao_exame_contas = models.ForeignKey('Comissao', on_delete=models.CASCADE,
                                              related_name='comissao_com_exame_contas')

    tipo_conta_um = models.ForeignKey('core.TipoConta', on_delete=models.CASCADE,
                                      related_name='tipo_conta_um', null=True, blank=True, default=None)

    tipo_conta_dois = models.ForeignKey('core.TipoConta', on_delete=models.CASCADE,
                                        related_name='tipo_conta_dois', null=True, blank=True, default=None)

    class Meta:
        verbose_name = "Parâmetro DRE"
        verbose_name_plural = "Parâmetros DRE"


auditlog.register(ParametrosDre)

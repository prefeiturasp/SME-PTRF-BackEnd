from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.paa.enums import TipoAtividadeEstatutariaEnum
from sme_ptrf_apps.paa.choices import Mes, StatusChoices


class AtividadeEstatutaria(ModeloBase):
    history = AuditlogHistoryField()
    nome = models.CharField('Atividade Estatutária', max_length=160, blank=False)
    tipo = models.CharField(max_length=20, null=True, blank=True,
                            default=TipoAtividadeEstatutariaEnum.ORDINARIA.name,
                            choices=TipoAtividadeEstatutariaEnum.choices())
    mes = models.IntegerField('Mês', choices=Mes.choices, blank=False, null=True)
    status = models.BooleanField(choices=StatusChoices.choices, default=StatusChoices.ATIVO)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Atividade Estatutária"
        verbose_name_plural = "Atividades Estatutárias"
        unique_together = ['nome', 'mes', 'tipo']


auditlog.register(AtividadeEstatutaria)

from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class AtividadeEstatutariaPaa(ModeloBase):
    history = AuditlogHistoryField()
    atividade_estatutaria = models.ForeignKey('paa.AtividadeEstatutaria', on_delete=models.PROTECT)
    paa = models.ForeignKey('paa.Paa', on_delete=models.PROTECT, verbose_name="PAA")
    data = models.DateField('Data da atividade', blank=False, null=False)

    def __str__(self):
        return f"{self.atividade_estatutaria.nome} - {self.data.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Atividade Estatutária PAA"
        verbose_name_plural = "Atividades Estatutárias PAA"
        unique_together = ['atividade_estatutaria', 'paa', 'data']


auditlog.register(AtividadeEstatutariaPaa)

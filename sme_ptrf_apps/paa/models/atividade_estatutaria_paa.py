"""
Módulo de modelos para atividades estatutárias do PAA.

Este módulo define a entidade responsável por registrar as atividades
estatutárias associadas a um PAA em uma data específica.
"""
from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class AtividadeEstatutariaPaa(ModeloBase):
    """
    Representa a associação de uma atividade estatutária a um PAA em uma data específica.

    Essa model registra a ocorrência da atividade no contexto de um plano anual,
    vinculando uma atividade estatutária a um PAA e ao período em que ela foi
    realizada ou deverá ser considerada.
    """
    history = AuditlogHistoryField()
    atividade_estatutaria = models.ForeignKey('paa.AtividadeEstatutaria', on_delete=models.PROTECT)
    paa = models.ForeignKey('paa.Paa', on_delete=models.PROTECT, verbose_name="PAA")
    data = models.DateField('Data da atividade', blank=False, null=False)

    def __str__(self) -> str:
        """Retorna uma representação textual da atividade com o nome e a data."""
        return f"{self.atividade_estatutaria.nome} - {self.data.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Atividade Estatutária PAA"
        verbose_name_plural = "Atividades Estatutárias PAA"
        unique_together = ['atividade_estatutaria', 'paa', 'data']


auditlog.register(AtividadeEstatutariaPaa)

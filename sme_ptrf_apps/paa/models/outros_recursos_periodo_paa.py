"""Modelo para representar a associação de um outro recurso a um período PAA."""
from django.db.models import Q, QuerySet
from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class OutroRecursoPeriodoPaaQuerySet(models.QuerySet):
    def disponiveis_para_paa(self, paa) -> QuerySet:
        """Retorna os recursos disponíveis para o PAA, considerando
        as unidades vinculadas ao PAA e o período do PAA.
        """
        return (
            self.filter(
                Q(unidades=paa.associacao.unidade) | Q(unidades__isnull=True),
                ativo=True,
                periodo_paa=paa.periodo_paa,
            )
            .select_related('outro_recurso', 'periodo_paa')
            .distinct()
        )


class OutroRecursoPeriodoPaa(ModeloBase):
    """
    Representa a associação de um outro recurso a um período PAA.

    Essa model registra a ocorrência de um outro recurso no contexto de um plano anual,
    vinculando um outro recurso a um período PAA e às unidades que podem utilizá-lo.
    """
    history = AuditlogHistoryField()

    periodo_paa = models.ForeignKey('paa.PeriodoPaa', on_delete=models.PROTECT, verbose_name="Período PAA",
                                    blank=False, null=True)
    outro_recurso = models.ForeignKey('paa.OutroRecurso', on_delete=models.PROTECT, verbose_name="Outro Recurso",
                                      blank=False, null=True)
    unidades = models.ManyToManyField('core.Unidade', blank=True)
    ativo = models.BooleanField(default=True)

    objects = OutroRecursoPeriodoPaaQuerySet.as_manager()

    def __str__(self) -> str:
        """Retorna uma representação textual do recurso com o nome e o período PAA."""
        return f'{self.outro_recurso} - {self.periodo_paa}'

    def uso_associacao(self) -> str:
        """Retorna uma string indicando se o recurso está vinculado a todas as unidades ou apenas a algumas."""
        tem_unidades_vinculadas = self.unidades.exists()
        return "Parcial" if tem_unidades_vinculadas else "Todas"

    class Meta:
        verbose_name = "Outro Recurso PAA"
        verbose_name_plural = "Outros Recursos PAA"
        unique_together = ['outro_recurso', 'periodo_paa']


auditlog.register(OutroRecursoPeriodoPaa)

from django.db.models import Q
from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class OutroRecursoPeriodoPaaQuerySet(models.QuerySet):
    def disponiveis_para_paa(self, paa):
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
    history = AuditlogHistoryField()

    periodo_paa = models.ForeignKey('paa.PeriodoPaa', on_delete=models.PROTECT, verbose_name="Período PAA",
                                    blank=False, null=True)
    outro_recurso = models.ForeignKey('paa.OutroRecurso', on_delete=models.PROTECT, verbose_name="Outro Recurso",
                                      blank=False, null=True)
    unidades = models.ManyToManyField('core.Unidade', blank=True)
    ativo = models.BooleanField(default=True)

    objects = OutroRecursoPeriodoPaaQuerySet.as_manager()

    def __str__(self):
        return f'{self.outro_recurso} - {self.periodo_paa}'

    def uso_associacao(self):
        tem_unidades_vinculadas = self.unidades.exists()
        return "Parcial" if tem_unidades_vinculadas else "Todas"

    class Meta:
        verbose_name = "Outro Recurso PAA"
        verbose_name_plural = "Outros Recursos PAA"
        unique_together = ['outro_recurso', 'periodo_paa']


auditlog.register(OutroRecursoPeriodoPaa)

from django.db import models
from django.core.exceptions import ValidationError
from sme_ptrf_apps.core.models_abstracts import ModeloBase

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class PeriodoInicialAssociacao(ModeloBase):
    history = AuditlogHistoryField()

    associacao = models.ForeignKey(
        "Associacao",
        on_delete=models.PROTECT,
        related_name="periodos_iniciais",
        blank=False,
        null=False,
        verbose_name='Associação',
    )

    recurso = models.ForeignKey(
        "core.Recurso",
        verbose_name="Recurso",
        on_delete=models.PROTECT,
        null=False,
        blank=False,
    )

    periodo_inicial = models.ForeignKey(
        'Periodo',
        on_delete=models.PROTECT,
        verbose_name='Período inicial',
        null=False, blank=False,
        help_text="O período inicial informado é uma referência e indica que o período a ser habilitado para a associação será o período posterior ao período informado."
    )

    class Meta:
        verbose_name = "Período Inicial de Associação"
        verbose_name_plural = "08.1) Períodos Iniciais de Associações"
        constraints = [
            models.UniqueConstraint(
                fields=["associacao", "recurso"],
                name="uniq_periodo_inicial_associacao_recurso",
            )
        ]

    def clean(self):
        super().clean()

        if self.periodo_inicial.recurso.id != self.recurso.id:
            raise ValidationError({
                "periodo_inicial": (
                    "Período deve pertencer ao recurso selecionado."
                )
            })

    @classmethod
    def filter_by_dre(cls, dre_uuid, queryset=None):
        obj = cls.objects if queryset is None else queryset

        return obj.filter(
            associacao__unidade__dre__uuid=dre_uuid,
            associacao__periodos_iniciais__isnull=False
        ).distinct()

    @classmethod
    def filter_by_recurso(cls, recurso, queryset=None):
        obj = cls.objects if queryset is None else queryset

        return obj.filter(
            recurso=recurso,
            associacao__periodos_iniciais__isnull=False
        ).distinct()

    @classmethod
    def order_by_referencia(cls, queryset=None):
        obj = cls.objects if queryset is None else queryset

        return obj.order_by('periodo_inicial__referencia')

    @classmethod
    def get_periodo_inicial_by_dre_and_recurso(cls, dre_uuid, recurso=None):
        queryset = cls.filter_by_dre(dre_uuid)

        if recurso:
            queryset = cls.filter_by_recurso(recurso, queryset)

        queryset = cls.order_by_referencia(queryset)

        return queryset.first() if queryset.exists() else None


auditlog.register(PeriodoInicialAssociacao)

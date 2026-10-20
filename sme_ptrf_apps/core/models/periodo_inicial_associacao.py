from django.db import models
from django.core.exceptions import ValidationError
from sme_ptrf_apps.core.models_abstracts import ModeloBase

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class PeriodoInicialAssociacao(ModeloBase):
    history = AuditlogHistoryField()

    STATUS_VALORES_REPROGRAMADOS_NAO_FINALIZADO = "NAO_FINALIZADO"
    STATUS_VALORES_REPROGRAMADOS_EM_CONFERENCIA_DRE = "EM_CONFERENCIA_DRE"
    STATUS_VALORES_REPROGRAMADOS_EM_CORRECAO_UE = "EM_CORRECAO_UE"
    STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS = "VALORES_CORRETOS"

    STATUS_VALORES_REPROGRAMADOS_NOMES = {
        STATUS_VALORES_REPROGRAMADOS_NAO_FINALIZADO: "Não finalizado",
        STATUS_VALORES_REPROGRAMADOS_EM_CONFERENCIA_DRE: "Em conferência DRE",
        STATUS_VALORES_REPROGRAMADOS_EM_CORRECAO_UE: "Em correção UE",
        STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS: "Valores corretos",
    }

    STATUS_VALORES_REPROGRAMADOS_CHOICES = (
        (
            STATUS_VALORES_REPROGRAMADOS_NAO_FINALIZADO,
            STATUS_VALORES_REPROGRAMADOS_NOMES[STATUS_VALORES_REPROGRAMADOS_NAO_FINALIZADO],
        ),
        (
            STATUS_VALORES_REPROGRAMADOS_EM_CONFERENCIA_DRE,
            STATUS_VALORES_REPROGRAMADOS_NOMES[STATUS_VALORES_REPROGRAMADOS_EM_CONFERENCIA_DRE],
        ),
        (
            STATUS_VALORES_REPROGRAMADOS_EM_CORRECAO_UE,
            STATUS_VALORES_REPROGRAMADOS_NOMES[STATUS_VALORES_REPROGRAMADOS_EM_CORRECAO_UE],
        ),
        (
            STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS,
            STATUS_VALORES_REPROGRAMADOS_NOMES[STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS],
        ),
    )

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

    status_valores_reprogramados = models.CharField(
        "Status dos valores reprogramados",
        max_length=20,
        choices=STATUS_VALORES_REPROGRAMADOS_CHOICES,
        default=STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS,
    )


    @staticmethod
    def filter_by_recurso(queryset, recurso):
        return queryset.filter(recurso=recurso)

    @classmethod
    def sincronizar_status_por_recurso_a_partir_do_status_global(cls, associacao):
        atualizado = 0
        for periodo_inicial_associacao in cls.objects.filter(associacao=associacao):
            if periodo_inicial_associacao.status_valores_reprogramados != associacao.status_valores_reprogramados:
                periodo_inicial_associacao.status_valores_reprogramados = associacao.status_valores_reprogramados
                periodo_inicial_associacao.save(update_fields=["status_valores_reprogramados", "alterado_em"])
                atualizado += 1
        return atualizado

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


auditlog.register(PeriodoInicialAssociacao)

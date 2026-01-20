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
    paa = models.ForeignKey('paa.Paa', on_delete=models.PROTECT, verbose_name="PAA", blank=True, null=True)
    ordem = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Atividade Estatutária"
        verbose_name_plural = "Atividades Estatutárias"
        unique_together = ['nome', 'mes', 'tipo']

    @classmethod
    def disponiveis_ordenadas(cls, paa):
        from sme_ptrf_apps.paa.models.atividade_estatutaria_paa import AtividadeEstatutariaPaa
        from django.db.models.functions import Coalesce
        from datetime import date
        from django.db.models import (
            Case, When, Value, IntegerField,
            DateField, Q, Subquery, OuterRef, F
        )
        """
        Retorna:
        - Atividades base (sem PAA), ordenadas por 'ordem'
        - Atividades do PAA, ordenadas por 'data'
        """

        data_paa_subquery = (
            AtividadeEstatutariaPaa.objects
            .filter(
                paa=paa,
                atividade_estatutaria=OuterRef('pk')
            )
            .order_by('data')
            .values('data')[:1]
        )

        atividades_base = (
            cls.objects
            .filter(
                Q(paa__isnull=True) | Q(paa=paa),
                status=StatusChoices.ATIVO,
            )
            .annotate(
                data_paa_ordem=Coalesce(
                    Subquery(data_paa_subquery, output_field=DateField()),
                    date(9999, 12, 31)
                ),
                ordem_final=Case(
                    When(ordem=0, then=Value(9999)),
                    default=F('ordem'),
                    output_field=IntegerField(),
                )
            )
            .order_by('ordem_final', 'data_paa_ordem')
        )

        return atividades_base


auditlog.register(AtividadeEstatutaria)

from django.db import models
from auditlog.models import AuditlogHistoryField
from django.db.models import Case, When, F, IntegerField, DateTimeField, Value, BooleanField
from auditlog.registry import auditlog
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.paa.enums import TipoAtividadeEstatutariaEnum
from sme_ptrf_apps.paa.choices import Mes, StatusChoices


class AtividadeEstatutariaQuerySet(models.QuerySet):
    def ordenadas(self):
        return (
            self.annotate(
                paa_is_null=Case(
                    When(paa__isnull=True, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
            .order_by(
                '-paa_is_null',
                Case(
                    When(paa__isnull=True, then=F('ordem')),
                    output_field=IntegerField(),
                ),
                Case(
                    When(paa__isnull=False, then=F('criado_em')),
                    output_field=DateTimeField(),
                ),
            )
        )


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

    objects = AtividadeEstatutariaQuerySet.as_manager()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Atividade Estatutária"
        verbose_name_plural = "Atividades Estatutárias"
        unique_together = ['nome', 'mes', 'tipo']


auditlog.register(AtividadeEstatutaria)

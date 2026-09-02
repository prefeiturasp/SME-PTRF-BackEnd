from datetime import timedelta
from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.mandatos.choices import CargoComposicaoVacanciaChoices as Cargo


class CargoComposicaoVacancia(ModeloBase):
    history = AuditlogHistoryField()

    composicao = models.ForeignKey(
        'ComposicaoVacancia', verbose_name="Composição",
        on_delete=models.CASCADE, related_name='cargos_da_composicao_vacancia'
    )

    ocupante_do_cargo = models.ForeignKey(
        'OcupanteCargo', verbose_name="Ocupante do Cargo",
        on_delete=models.CASCADE, related_name='cargos_da_composicao_vacancia_do_ocupante',
        null=True, blank=True
    )  # null considerar cargo vago no período

    cargo_associacao = models.CharField(
        'Cargo Associação', max_length=50,
        choices=Cargo.choices,
        default=Cargo.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
    )

    data_inicio_no_cargo = models.DateField(verbose_name='Data de início no cargo')
    data_fim_no_cargo = models.DateField(verbose_name='Data de término no cargo')

    substituido_por = models.ForeignKey(
        'self', verbose_name="Substituído por",
        on_delete=models.PROTECT,
        related_name='substitui',
        null=True, blank=True
    )

    def __str__(self):
        return f"{self.cargo_associacao}"

    @property
    def substituido(self) -> bool:
        """ True se este registro foi encerrado e outro assumiu no dia seguinte, sem gap """
        return self.substituido_por_id is not None

    @property
    def substituto(self) -> bool:
        """ True se este registro começou substituindo diretamente quem saiu no dia anterior """
        return self.substituto_imediato is not None

    @property
    def substituto_imediato(self) -> bool:
        """ True se este registro começou substituindo diretamente quem saiu no dia anterior """
        return self.substitui.filter(
            data_fim_no_cargo=self.data_inicio_no_cargo - timedelta(days=1)
        ).first()

    @classmethod
    def ordenar_por_cargo(cls, participante):
        cargos = {
            Cargo.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA.label: 1,
            Cargo.CARGO_ASSOCIACAO_VICE_PRESIDENTE_DIRETORIA_EXECUTIVA.label: 2,
            Cargo.CARGO_ASSOCIACAO_SECRETARIO.label: 3,
            Cargo.CARGO_ASSOCIACAO_TESOUREIRO.label: 4,
            'Vogal': 5,
            Cargo.CARGO_ASSOCIACAO_VOGAL_1.label: 5,
            Cargo.CARGO_ASSOCIACAO_VOGAL_2.label: 6,
            Cargo.CARGO_ASSOCIACAO_VOGAL_3.label: 7,
            Cargo.CARGO_ASSOCIACAO_VOGAL_4.label: 8,
            Cargo.CARGO_ASSOCIACAO_VOGAL_5.label: 9,
            Cargo.CARGO_ASSOCIACAO_PRESIDENTE_CONSELHO_FISCAL.label: 10,
            'Conselheiro': 7,
            Cargo.CARGO_ASSOCIACAO_CONSELHEIRO_1.label: 11,
            Cargo.CARGO_ASSOCIACAO_CONSELHEIRO_2.label: 12,
            Cargo.CARGO_ASSOCIACAO_CONSELHEIRO_3.label: 13,
            Cargo.CARGO_ASSOCIACAO_CONSELHEIRO_4.label: 14,
        }

        return cargos.get(participante['cargo'], 99)

    class Meta:
        verbose_name = 'Cargo Composição Vacância'
        verbose_name_plural = 'Cargos Composições Vacâncias'


auditlog.register(CargoComposicaoVacancia)

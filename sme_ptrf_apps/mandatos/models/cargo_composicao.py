from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class CargoComposicao(ModeloBase):
    history = AuditlogHistoryField()

    # Cargos Associação
    CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA = 'PRESIDENTE_DIRETORIA_EXECUTIVA'
    CARGO_ASSOCIACAO_VICE_PRESIDENTE_DIRETORIA_EXECUTIVA = 'VICE_PRESIDENTE_DIRETORIA_EXECUTIVA'
    CARGO_ASSOCIACAO_SECRETARIO = 'SECRETARIO'
    CARGO_ASSOCIACAO_TESOUREIRO = 'TESOUREIRO'
    CARGO_ASSOCIACAO_VOGAL_1 = 'VOGAL_1'
    CARGO_ASSOCIACAO_VOGAL_2 = 'VOGAL_2'
    CARGO_ASSOCIACAO_VOGAL_3 = 'VOGAL_3'
    CARGO_ASSOCIACAO_VOGAL_4 = 'VOGAL_4'
    CARGO_ASSOCIACAO_VOGAL_5 = 'VOGAL_5'
    CARGO_ASSOCIACAO_PRESIDENTE_CONSELHO_FISCAL = 'PRESIDENTE_CONSELHO_FISCAL'
    CARGO_ASSOCIACAO_CONSELHEIRO_1 = 'CONSELHEIRO_1'
    CARGO_ASSOCIACAO_CONSELHEIRO_2 = 'CONSELHEIRO_2'
    CARGO_ASSOCIACAO_CONSELHEIRO_3 = 'CONSELHEIRO_3'
    CARGO_ASSOCIACAO_CONSELHEIRO_4 = 'CONSELHEIRO_4'

    CARGO_ASSOCIACAO_NOMES = {
        CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA: 'Presidente da diretoria executiva',
        CARGO_ASSOCIACAO_VICE_PRESIDENTE_DIRETORIA_EXECUTIVA: 'Vice-Presidente da diretoria executiva',
        CARGO_ASSOCIACAO_SECRETARIO: 'Secretário',
        CARGO_ASSOCIACAO_TESOUREIRO: 'Tesoureiro',
        CARGO_ASSOCIACAO_VOGAL_1: 'Vogal 1',
        CARGO_ASSOCIACAO_VOGAL_2: 'Vogal 2',
        CARGO_ASSOCIACAO_VOGAL_3: 'Vogal 3',
        CARGO_ASSOCIACAO_VOGAL_4: 'Vogal 4',
        CARGO_ASSOCIACAO_VOGAL_5: 'Vogal 5',
        CARGO_ASSOCIACAO_PRESIDENTE_CONSELHO_FISCAL: 'Presidente do conselho fiscal',
        CARGO_ASSOCIACAO_CONSELHEIRO_1: 'Conselheiro 1',
        CARGO_ASSOCIACAO_CONSELHEIRO_2: 'Conselheiro 2',
        CARGO_ASSOCIACAO_CONSELHEIRO_3: 'Conselheiro 3',
        CARGO_ASSOCIACAO_CONSELHEIRO_4: 'Conselheiro 4',
    }

    CARGO_ASSOCIACAO_CHOICES = (
        (CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
         CARGO_ASSOCIACAO_NOMES[CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA]),
        (CARGO_ASSOCIACAO_VICE_PRESIDENTE_DIRETORIA_EXECUTIVA,
         CARGO_ASSOCIACAO_NOMES[CARGO_ASSOCIACAO_VICE_PRESIDENTE_DIRETORIA_EXECUTIVA]),
        (CARGO_ASSOCIACAO_SECRETARIO, CARGO_ASSOCIACAO_NOMES[CARGO_ASSOCIACAO_SECRETARIO]),
        (CARGO_ASSOCIACAO_TESOUREIRO, CARGO_ASSOCIACAO_NOMES[CARGO_ASSOCIACAO_TESOUREIRO]),
        (CARGO_ASSOCIACAO_VOGAL_1, CARGO_ASSOCIACAO_NOMES[CARGO_ASSOCIACAO_VOGAL_1]),
        (CARGO_ASSOCIACAO_VOGAL_2, CARGO_ASSOCIACAO_NOMES[CARGO_ASSOCIACAO_VOGAL_2]),
        (CARGO_ASSOCIACAO_VOGAL_3, CARGO_ASSOCIACAO_NOMES[CARGO_ASSOCIACAO_VOGAL_3]),
        (CARGO_ASSOCIACAO_VOGAL_4, CARGO_ASSOCIACAO_NOMES[CARGO_ASSOCIACAO_VOGAL_4]),
        (CARGO_ASSOCIACAO_VOGAL_5, CARGO_ASSOCIACAO_NOMES[CARGO_ASSOCIACAO_VOGAL_5]),
        (CARGO_ASSOCIACAO_PRESIDENTE_CONSELHO_FISCAL,
         CARGO_ASSOCIACAO_NOMES[CARGO_ASSOCIACAO_PRESIDENTE_CONSELHO_FISCAL]),
        (CARGO_ASSOCIACAO_CONSELHEIRO_1, CARGO_ASSOCIACAO_NOMES[CARGO_ASSOCIACAO_CONSELHEIRO_1]),
        (CARGO_ASSOCIACAO_CONSELHEIRO_2, CARGO_ASSOCIACAO_NOMES[CARGO_ASSOCIACAO_CONSELHEIRO_2]),
        (CARGO_ASSOCIACAO_CONSELHEIRO_3, CARGO_ASSOCIACAO_NOMES[CARGO_ASSOCIACAO_CONSELHEIRO_3]),
        (CARGO_ASSOCIACAO_CONSELHEIRO_4, CARGO_ASSOCIACAO_NOMES[CARGO_ASSOCIACAO_CONSELHEIRO_4]),
    )

    composicao = models.ForeignKey('Composicao', verbose_name="Composição",
                                   on_delete=models.CASCADE, related_name='cargos_da_composicao_da_composicao')

    ocupante_do_cargo = models.ForeignKey('OcupanteCargo', verbose_name="Ocupante do Cargo",
                                          on_delete=models.CASCADE, related_name='cargos_da_composicao_do_ocupante', null=True, blank=True)

    cargo_associacao = models.CharField(
        'Cargo Associação',
        max_length=50,
        choices=CARGO_ASSOCIACAO_CHOICES,
        default=CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
    )

    substituto = models.BooleanField("Substituto", default=False, blank=True, null=True)

    substituido = models.BooleanField("Substituido", default=False, blank=True, null=True)

    data_inicio_no_cargo = models.DateField(verbose_name='Data de início no cargo', blank=True, null=True)

    data_fim_no_cargo = models.DateField(verbose_name='Data de término no cargo', blank=True, null=True)

    class Meta:
        verbose_name = 'Cargo Composição'
        verbose_name_plural = 'Cargos Composições'

    def __str__(self):
        return f"{self.cargo_associacao}"

    def set_encerrar_e_substituir(self, data_fim_no_cargo):
        self.substituido = True
        self.data_fim_no_cargo = data_fim_no_cargo
        self.save()

    def data_inicio_posterior_a_data_informada(self, data):
        return self.data_inicio_no_cargo > data

    @classmethod
    def ordenar_por_cargo(cls, participante):
        cargos = {
            cls.CARGO_ASSOCIACAO_NOMES[cls.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA]: 1,
            cls.CARGO_ASSOCIACAO_NOMES[cls.CARGO_ASSOCIACAO_VICE_PRESIDENTE_DIRETORIA_EXECUTIVA]: 2,
            cls.CARGO_ASSOCIACAO_NOMES[cls.CARGO_ASSOCIACAO_SECRETARIO]: 3,
            cls.CARGO_ASSOCIACAO_NOMES[cls.CARGO_ASSOCIACAO_TESOUREIRO]: 4,
            
            'Vogal': 5,
            cls.CARGO_ASSOCIACAO_NOMES[cls.CARGO_ASSOCIACAO_VOGAL_1]: 5,
            cls.CARGO_ASSOCIACAO_NOMES[cls.CARGO_ASSOCIACAO_VOGAL_2]: 6,
            cls.CARGO_ASSOCIACAO_NOMES[cls.CARGO_ASSOCIACAO_VOGAL_3]: 7,
            cls.CARGO_ASSOCIACAO_NOMES[cls.CARGO_ASSOCIACAO_VOGAL_4]: 8,
            cls.CARGO_ASSOCIACAO_NOMES[cls.CARGO_ASSOCIACAO_VOGAL_5]: 9,

            cls.CARGO_ASSOCIACAO_NOMES[cls.CARGO_ASSOCIACAO_PRESIDENTE_CONSELHO_FISCAL]: 10,

            'Conselheiro': 7,
            cls.CARGO_ASSOCIACAO_NOMES[cls.CARGO_ASSOCIACAO_CONSELHEIRO_1]: 11,
            cls.CARGO_ASSOCIACAO_NOMES[cls.CARGO_ASSOCIACAO_CONSELHEIRO_2]: 12,
            cls.CARGO_ASSOCIACAO_NOMES[cls.CARGO_ASSOCIACAO_CONSELHEIRO_3]: 13,
            cls.CARGO_ASSOCIACAO_NOMES[cls.CARGO_ASSOCIACAO_CONSELHEIRO_4]: 14,
        }

        return cargos.get(participante['cargo'], 99)


auditlog.register(CargoComposicao)

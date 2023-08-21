from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class OcupanteCargo(ModeloBase):
    history = AuditlogHistoryField()

    # Represnetação Cargo
    REPRESENTACAO_CARGO_SERVIDOR = 'SERVIDOR'
    REPRESENTACAO_CARGO_PAI_RESPONSAVEL = 'PAI_RESPONSAVEL'
    REPRESENTACAO_CARGO_ESTUDANTE = 'ESTUDANTE'

    REPRESENTACAO_CARGO_NOMES = {
        REPRESENTACAO_CARGO_SERVIDOR: 'Servidor',
        REPRESENTACAO_CARGO_PAI_RESPONSAVEL: 'Pai ou responsável',
        REPRESENTACAO_CARGO_ESTUDANTE: 'Estudante',
    }

    REPRESENTACAO_CARGO_CHOICES = (
        (REPRESENTACAO_CARGO_SERVIDOR, REPRESENTACAO_CARGO_NOMES[REPRESENTACAO_CARGO_SERVIDOR]),
        (REPRESENTACAO_CARGO_PAI_RESPONSAVEL, REPRESENTACAO_CARGO_NOMES[REPRESENTACAO_CARGO_PAI_RESPONSAVEL]),
        (REPRESENTACAO_CARGO_ESTUDANTE, REPRESENTACAO_CARGO_NOMES[REPRESENTACAO_CARGO_ESTUDANTE]),
    )

    nome = models.CharField('Nome', max_length=160)

    codigo_identificacao = models.CharField('Código EOL ou RF', max_length=10, blank=True, null=True, default="")

    cargo_educacao = models.CharField('Cargo Educação', max_length=160, blank=True, null=True, default="")

    representacao = models.CharField(
        'Representação',
        max_length=15,
        choices=REPRESENTACAO_CARGO_CHOICES,
        default=REPRESENTACAO_CARGO_SERVIDOR,
    )

    email = models.EmailField("E-mail", max_length=254, null=True, blank=True)

    cpf_responsavel = models.CharField("CPF Responsável", max_length=14, blank=True, null=True, default="")

    telefone = models.CharField('Telefone', max_length=20, blank=True, default='')

    cep = models.CharField('CEP', max_length=20, blank=True, default='')

    bairro = models.CharField('Bairro', max_length=255, blank=True, default='')

    endereco = models.CharField('Endereço', max_length=255, blank=True, default='')


    class Meta:
        verbose_name = 'Ocupante Cargo'
        verbose_name_plural = 'Ocupantes Cargo'

    def __str__(self):
        return f"Nome: {self.nome}, Representacao: {self.representacao}"


auditlog.register(OcupanteCargo)

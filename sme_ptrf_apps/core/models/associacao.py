from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from .validators import cnpj_validation
from ..choices import MembroEnum


class Associacao(ModeloIdNome):
    # Status de Regularidade
    STATUS_REGULARIDADE_PENDENTE = 'PENDENTE'
    STATUS_REGULARIDADE_REGULAR = 'REGULAR'

    STATUS_REGULARIDADE_NOMES = {
        STATUS_REGULARIDADE_PENDENTE: 'Pendente',
        STATUS_REGULARIDADE_REGULAR: 'Regular',
    }

    STATUS_REGULARIDADE_CHOICES = (
        (STATUS_REGULARIDADE_PENDENTE, STATUS_REGULARIDADE_NOMES[STATUS_REGULARIDADE_PENDENTE]),
        (STATUS_REGULARIDADE_REGULAR, STATUS_REGULARIDADE_NOMES[STATUS_REGULARIDADE_REGULAR]),
    )

    unidade = models.ForeignKey('Unidade', on_delete=models.PROTECT, related_name="associacoes", to_field="codigo_eol",
                                null=True)

    cnpj = models.CharField(
        "CNPJ", max_length=20, validators=[cnpj_validation], blank=True, default="", unique=True
    )

    periodo_inicial = models.ForeignKey('Periodo', on_delete=models.PROTECT, verbose_name='período inicial',
                                        related_name='associacoes_iniciadas_no_periodo', null=True, blank=True)

    ccm = models.CharField('CCM', max_length=15, null=True, blank=True, default="")

    email = models.EmailField("E-mail", max_length=254, null=True, blank=True, default="")

    status_regularidade = models.CharField(
        'Status de Regularidade',
        max_length=15,
        choices=STATUS_REGULARIDADE_CHOICES,
        default=STATUS_REGULARIDADE_PENDENTE,
    )

    def apaga_implantacoes_de_saldo(self):
        self.fechamentos_associacao.filter(status='IMPLANTACAO').delete()

    @property
    def presidente_associacao(self):
        cargo = self.cargos.filter(cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.value).get()
        if cargo:
            return {
                'nome': cargo.nome,
                'email': cargo.email
            }
        else:
            return {
                'nome': '',
                'email': ''
            }

    @property
    def presidente_conselho_fiscal(self):
        cargo = self.cargos.filter(cargo_associacao=MembroEnum.PRESIDENTE_CONSELHO_FISCAL.value).get()
        if cargo:
            return {
                'nome': cargo.nome,
                'email': cargo.email
            }
        else:
            return {
                'nome': '',
                'email': ''
            }

    @classmethod
    def acoes_da_associacao(cls, associacao_uuid):
        associacao = cls.objects.filter(uuid=associacao_uuid).first()
        return associacao.acoes.all().order_by('acao__posicao_nas_pesquisas') if associacao else []

    @classmethod
    def status_regularidade_to_json(cls):
        result = []
        for choice in cls.STATUS_REGULARIDADE_CHOICES:
            status = {
                'id': choice[0],
                'nome': choice[1]
            }
            result.append(status)
        return result

    class Meta:
        verbose_name = "Associação"
        verbose_name_plural = "Associações"

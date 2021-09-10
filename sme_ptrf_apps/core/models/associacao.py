from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from .validators import cnpj_validation
from ..choices import MembroEnum
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class Associacao(ModeloIdNome):
    history = AuditlogHistoryField()

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

    processo_regularidade = models.CharField('Nº processo regularidade', max_length=100, default='', blank=True)

    motivo_nao_regularidade = models.CharField(
        'Motivo da não regularização da associação', max_length=300, default='', blank=True)

    def apaga_implantacoes_de_saldo(self):
        self.fechamentos_associacao.filter(status='IMPLANTACAO').delete()

    @property
    def presidente_associacao(self):
        cargo = self.cargos.filter(cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.name).first()
        if cargo:
            return {
                'nome': cargo.nome,
                'email': cargo.email,
                'cargo_educacao': cargo.cargo_educacao,
                'telefone': cargo.telefone,
                'endereco': cargo.endereco,
                'bairro': cargo.bairro,
                'cep': cargo.cep
            }
        else:
            return {
                'nome': '',
                'email': '',
                'cargo_educacao': '',
                'telefone': '',
                'endereco': '',
                'bairro': '',
                'cep': ''
            }

    @property
    def presidente_conselho_fiscal(self):
        cargo = self.cargos.filter(cargo_associacao=MembroEnum.PRESIDENTE_CONSELHO_FISCAL.name).first()
        if cargo:
            return {
                'nome': cargo.nome,
                'email': cargo.email,
                'cargo_educacao': cargo.cargo_educacao
            }
        else:
            return {
                'nome': '',
                'email': '',
                'cargo_educacao': ''
            }

    def periodos_com_prestacao_de_contas(self):
        periodos = set()
        for prestacao in self.prestacoes_de_conta_da_associacao.all():
            periodos.add(prestacao.periodo)
        return periodos

    def proximo_periodo_de_prestacao_de_contas(self):
        ultima_prestacao_feita = self.prestacoes_de_conta_da_associacao.last()
        ultimo_periodo_com_prestacao = ultima_prestacao_feita.periodo if ultima_prestacao_feita else None
        if ultimo_periodo_com_prestacao:
            return ultimo_periodo_com_prestacao.periodo_seguinte.first()
        else:
            return self.periodo_inicial.periodo_seguinte.first() if self.periodo_inicial else None

    def periodos_para_prestacoes_de_conta(self):
        periodos = list(self.periodos_com_prestacao_de_contas())
        proximo_periodo = self.proximo_periodo_de_prestacao_de_contas()
        if proximo_periodo:
            periodos.append(proximo_periodo)
        return periodos

    def periodos_ate_agora_fora_implantacao(self):
        from datetime import datetime
        from .periodo import Periodo

        qry_periodos = Periodo.objects.filter(
            data_inicio_realizacao_despesas__lte=datetime.today()).order_by('-referencia')

        if self.periodo_inicial:
            qry_periodos = qry_periodos.filter(
                data_inicio_realizacao_despesas__gte=self.periodo_inicial.data_fim_realizacao_despesas
            )

        return qry_periodos.all()

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
        verbose_name_plural = "07.0) Associações"


auditlog.register(Associacao)

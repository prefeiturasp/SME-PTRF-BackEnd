import logging

from datetime import date

from django.db import models
from django.db import transaction
from django.db.models.aggregates import Sum

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.dre.models import Atribuicao

logger = logging.getLogger(__name__)


class PrestacaoConta(ModeloBase):
    # Status Choice
    STATUS_DOCS_PENDENTES = 'DOCS_PENDENTES'
    STATUS_NAO_RECEBIDA = 'NAO_RECEBIDA'
    STATUS_RECEBIDA = 'RECEBIDA'
    STATUS_EM_ANALISE = 'EM_ANALISE'
    STATUS_DEVOLVIDA = 'DEVOLVIDA'
    STATUS_APROVADA = 'APROVADA'
    STATUS_APROVADA_RESSALVA = 'APROVADA_RESSALVA'
    STATUS_REPROVADA = 'REPROVADA'

    STATUS_NOMES = {
        STATUS_DOCS_PENDENTES: 'Documentos pendentes',
        STATUS_NAO_RECEBIDA: 'Não recebida',
        STATUS_RECEBIDA: 'Recebida',
        STATUS_EM_ANALISE: 'Em análise',
        STATUS_DEVOLVIDA: 'Devolvida para acertos',
        STATUS_APROVADA: 'Aprovada',
        STATUS_APROVADA_RESSALVA: 'Aprovada com ressalvas',
        STATUS_REPROVADA: 'Reprovada'
    }

    STATUS_CHOICES = (
        (STATUS_DOCS_PENDENTES, STATUS_NOMES[STATUS_DOCS_PENDENTES]),
        (STATUS_NAO_RECEBIDA, STATUS_NOMES[STATUS_NAO_RECEBIDA]),
        (STATUS_RECEBIDA, STATUS_NOMES[STATUS_RECEBIDA]),
        (STATUS_EM_ANALISE, STATUS_NOMES[STATUS_EM_ANALISE]),
        (STATUS_DEVOLVIDA, STATUS_NOMES[STATUS_DEVOLVIDA]),
        (STATUS_APROVADA, STATUS_NOMES[STATUS_APROVADA]),
        (STATUS_APROVADA_RESSALVA, STATUS_NOMES[STATUS_APROVADA_RESSALVA]),
        (STATUS_REPROVADA, STATUS_NOMES[STATUS_REPROVADA]),
    )

    periodo = models.ForeignKey('Periodo', on_delete=models.PROTECT, related_name='prestacoes_de_conta')

    associacao = models.ForeignKey('Associacao', on_delete=models.PROTECT,
                                   related_name='prestacoes_de_conta_da_associacao',
                                   blank=True, null=True)

    status = models.CharField(
        'status',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DOCS_PENDENTES
    )

    data_recebimento = models.DateField('data de recebimento pela DRE', blank=True, null=True)

    data_ultima_analise = models.DateField('data da última análise pela DRE', blank=True, null=True)

    devolucao_tesouro = models.BooleanField('há devolução ao tesouro', blank=True, null=True, default=False)

    ressalvas_aprovacao = models.TextField('Ressalvas na aprovação pela DRE', blank=True, default='')

    @property
    def tecnico_responsavel(self):
        atribuicoes = Atribuicao.search(
            **{'unidade__uuid': self.associacao.unidade.uuid, 'periodo__uuid': self.periodo.uuid})
        if atribuicoes.exists():
            return atribuicoes.first().tecnico
        else:
            return None

    @property
    def total_devolucao_ao_tesouro(self):
        return self.devolucoes_ao_tesouro_da_prestacao.all().aggregate(Sum('valor'))['valor__sum'] or 0.00

    def __str__(self):
        return f"{self.periodo} - {self.status}"

    def apaga_fechamentos(self):
        for fechamento in self.fechamentos_da_prestacao.all():
            fechamento.delete()

    def apaga_relacao_bens(self):
        for relacao in self.relacoes_de_bens_da_prestacao.all():
            relacao.delete()

    def apaga_demonstrativos_financeiros(self):
        for demonstrativo in self.demonstrativos_da_prestacao.all():
            demonstrativo.delete()

    def ultima_ata(self):
        return self.atas_da_prestacao.filter(tipo_ata='APRESENTACAO').last()

    def ultima_ata_retificacao(self):
        return self.atas_da_prestacao.filter(tipo_ata='RETIFICACAO').last()

    def concluir(self):
        self.status = self.STATUS_NAO_RECEBIDA
        self.save()
        return self

    def receber(self, data_recebimento):
        self.data_recebimento = data_recebimento
        self.status = self.STATUS_RECEBIDA
        self.save()
        return self

    def desfazer_recebimento(self):
        self.data_recebimento = None
        self.status = self.STATUS_NAO_RECEBIDA
        self.save()
        return self

    def analisar(self):
        self.status = self.STATUS_EM_ANALISE
        self.save()
        return self

    def desfazer_analise(self):
        self.data_ultima_analise = None
        self.status = self.STATUS_RECEBIDA
        self.save()
        return self


    @transaction.atomic
    def salvar_devolucoes_ao_tesouro(self, devolucoes_ao_tesouro_da_prestacao=[]):
        from ..models.devolucao_ao_tesouro import DevolucaoAoTesouro
        from ..models.tipo_devolucao_ao_tesouro import TipoDevolucaoAoTesouro
        from ...despesas.models.despesa import Despesa

        self.devolucoes_ao_tesouro_da_prestacao.all().delete()
        for devolucao in devolucoes_ao_tesouro_da_prestacao:
            tipo_devolucao = TipoDevolucaoAoTesouro.by_uuid(devolucao['tipo'])
            despesa = Despesa.by_uuid(devolucao['despesa'])
            DevolucaoAoTesouro.objects.create(
                prestacao_conta=self,
                tipo=tipo_devolucao,
                despesa=despesa,
                data=devolucao['data'],
                devolucao_total=devolucao['devolucao_total'],
                motivo=devolucao['motivo'],
                valor=devolucao['valor']
            )

        return self

    @transaction.atomic
    def salvar_analise(self, devolucao_tesouro, analises_de_conta_da_prestacao, resultado_analise=None,
                       ressalvas_aprovacao='', devolucoes_ao_tesouro_da_prestacao=[]):
        from ..models.analise_conta_prestacao_conta import AnaliseContaPrestacaoConta
        from ..models.devolucao_ao_tesouro import DevolucaoAoTesouro
        from ..models.conta_associacao import ContaAssociacao
        from ..models.tipo_devolucao_ao_tesouro import TipoDevolucaoAoTesouro
        from ...despesas.models.despesa import Despesa

        self.devolucao_tesouro = devolucao_tesouro
        self.data_ultima_analise = date.today()

        if resultado_analise:
            self.status = resultado_analise

        self.ressalvas_aprovacao = ressalvas_aprovacao

        self.save()

        self.analises_de_conta_da_prestacao.all().delete()
        for analise in analises_de_conta_da_prestacao:
            conta_associacao = ContaAssociacao.by_uuid(analise['conta_associacao'])
            AnaliseContaPrestacaoConta.objects.create(
                prestacao_conta=self,
                conta_associacao=conta_associacao,
                data_extrato=analise['data_extrato'],
                saldo_extrato=analise['saldo_extrato']
            )

        self.devolucoes_ao_tesouro_da_prestacao.all().delete()
        for devolucao in devolucoes_ao_tesouro_da_prestacao:
            tipo_devolucao = TipoDevolucaoAoTesouro.by_uuid(devolucao['tipo'])
            despesa = Despesa.by_uuid(devolucao['despesa'])
            DevolucaoAoTesouro.objects.create(
                prestacao_conta=self,
                tipo=tipo_devolucao,
                despesa=despesa,
                data=devolucao['data'],
                devolucao_total=devolucao['devolucao_total'],
                motivo=devolucao['motivo'],
                valor=devolucao['valor']
            )

        return self

    @transaction.atomic
    def devolver(self, data_limite_ue):
        from ..models import DevolucaoPrestacaoConta
        DevolucaoPrestacaoConta.objects.create(
            prestacao_conta=self,
            data=date.today(),
            data_limite_ue=data_limite_ue
        )
        self.apaga_fechamentos()
        self.apaga_relacao_bens()
        self.apaga_demonstrativos_financeiros()
        return self

    @transaction.atomic
    def concluir_analise(self, resultado_analise, devolucao_tesouro, analises_de_conta_da_prestacao,
                         ressalvas_aprovacao, data_limite_ue, devolucoes_ao_tesouro_da_prestacao=[]):
        prestacao_atualizada = self.salvar_analise(resultado_analise=resultado_analise,
                                                   devolucao_tesouro=devolucao_tesouro,
                                                   analises_de_conta_da_prestacao=analises_de_conta_da_prestacao,
                                                   ressalvas_aprovacao=ressalvas_aprovacao,
                                                   devolucoes_ao_tesouro_da_prestacao=devolucoes_ao_tesouro_da_prestacao)

        if resultado_analise == PrestacaoConta.STATUS_DEVOLVIDA:
            prestacao_atualizada = prestacao_atualizada.devolver(data_limite_ue=data_limite_ue)

        return prestacao_atualizada

    def desfazer_conclusao_analise(self):
        self.ressalvas_aprovacao = ''
        self.status = self.STATUS_EM_ANALISE
        self.save()
        return self

    @classmethod
    @transaction.atomic
    def reabrir(cls, uuid):
        logger.info(f'Apagando a prestação de contas de uuid {uuid}.')
        try:
            prestacao_de_conta = cls.by_uuid(uuid=uuid)
            prestacao_de_conta.apaga_fechamentos()
            prestacao_de_conta.apaga_relacao_bens()
            prestacao_de_conta.apaga_demonstrativos_financeiros()
            prestacao_de_conta.delete()
            logger.info(f'Prestação de contas de uuid {uuid} foi apagada.')
            return True
        except:
            logger.error(f'Houve algum erro ao tentar apagar a PC de uuid {uuid}.')
            return False


    @classmethod
    def abrir(cls, periodo, associacao):
        prestacao_de_conta = cls.by_periodo(associacao=associacao, periodo=periodo)

        if not prestacao_de_conta:
            prestacao_de_conta = PrestacaoConta.objects.create(
                periodo=periodo,
                associacao=associacao,
                status=cls.STATUS_DOCS_PENDENTES
            )
        return prestacao_de_conta

    @classmethod
    def by_periodo(cls, associacao, periodo):
        return cls.objects.filter(associacao=associacao, periodo=periodo).first()

    @classmethod
    def dashboard(cls, periodo_uuid, dre_uuid):
        titulos_por_status = {
            cls.STATUS_NAO_RECEBIDA: "Prestações de contas não recebidas",
            cls.STATUS_RECEBIDA: "Prestações de contas recebidas aguardando análise",
            cls.STATUS_EM_ANALISE: "Prestações de contas em análise",
            cls.STATUS_DEVOLVIDA: "Prestações de conta devolvidas para acertos",
            cls.STATUS_APROVADA: "Prestações de contas aprovadas",
            cls.STATUS_REPROVADA: "Prestações de contas reprovadas",
        }

        cards = []
        qs = cls.objects.filter(periodo__uuid=periodo_uuid, associacao__unidade__dre__uuid=dre_uuid)
        for status, titulo in titulos_por_status.items():
            card = {
                "titulo": titulo,
                "quantidade_prestacoes": qs.filter(status=status).count(),
                "status": status
            }
            cards.append(card)

        return cards

    @classmethod
    def status_to_json(cls):
        result = []
        for choice in cls.STATUS_CHOICES:
            status = {
                'id': choice[0],
                'nome': choice[1]
            }
            result.append(status)
        return result

    class Meta:
        verbose_name = "Prestação de conta"
        verbose_name_plural = "09.0) Prestações de contas"
        unique_together = ['associacao', 'periodo']

from django.db import models
from django.db import transaction

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.dre.models import Atribuicao


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

    @property
    def tecnico_responsavel(self):
        atribuicoes = Atribuicao.search(
            **{'unidade__uuid': self.associacao.unidade.uuid, 'periodo__uuid': self.periodo.uuid})
        if atribuicoes.exists():
            return atribuicoes.first().tecnico
        else:
            return None

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
        return self.atas_da_prestacao.last()

    def concluir(self):
        self.status = self.STATUS_NAO_RECEBIDA
        self.save()
        return self

    @classmethod
    @transaction.atomic
    def reabrir(cls, uuid):
        prestacao_de_conta = cls.by_uuid(uuid=uuid)
        prestacao_de_conta.status = cls.STATUS_DEVOLVIDA
        prestacao_de_conta.save()
        prestacao_de_conta.apaga_fechamentos()
        prestacao_de_conta.apaga_relacao_bens()
        prestacao_de_conta.apaga_demonstrativos_financeiros()
        return prestacao_de_conta

    @classmethod
    def abrir(cls, periodo, associacao):
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

    class Meta:
        verbose_name = "Prestação de conta"
        verbose_name_plural = "Prestações de contas"
        unique_together = ['associacao', 'periodo']

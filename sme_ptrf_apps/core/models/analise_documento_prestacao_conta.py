from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from ...utils.choices_to_json import choices_to_json
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.core.models import TipoAcertoDocumento


class AnaliseDocumentoPrestacaoConta(ModeloBase):
    history = AuditlogHistoryField()

    # Status Choice
    RESULTADO_CORRETO = 'CORRETO'
    RESULTADO_AJUSTE = 'AJUSTE'

    RESULTADO_NOMES = {
        RESULTADO_CORRETO: 'Documento Correto',
        RESULTADO_AJUSTE: 'Ajuste necessário',
    }

    RESULTADO_CHOICES = (
        (RESULTADO_CORRETO, RESULTADO_NOMES[RESULTADO_CORRETO]),
        (RESULTADO_AJUSTE, RESULTADO_NOMES[RESULTADO_AJUSTE]),
    )

    # Status realizacao choices
    STATUS_REALIZACAO_PENDENTE = 'PENDENTE'
    STATUS_REALIZACAO_REALIZADO = 'REALIZADO'
    STATUS_REALIZACAO_JUSTIFICADO = 'JUSTIFICADO'

    STATUS_REALIZACAO_NOMES = {
        STATUS_REALIZACAO_PENDENTE: 'Pendente',
        STATUS_REALIZACAO_REALIZADO: 'Realizado',
        STATUS_REALIZACAO_JUSTIFICADO: 'Justificado'
    }

    STATUS_REALIZACAO_CHOICES = (
        (STATUS_REALIZACAO_PENDENTE, STATUS_REALIZACAO_NOMES[STATUS_REALIZACAO_PENDENTE]),
        (STATUS_REALIZACAO_REALIZADO, STATUS_REALIZACAO_NOMES[STATUS_REALIZACAO_REALIZADO]),
        (STATUS_REALIZACAO_JUSTIFICADO, STATUS_REALIZACAO_NOMES[STATUS_REALIZACAO_JUSTIFICADO])
    )

    analise_prestacao_conta = models.ForeignKey('AnalisePrestacaoConta', on_delete=models.CASCADE,
                                                related_name='analises_de_documento')

    tipo_documento_prestacao_conta = models.ForeignKey('TipoDocumentoPrestacaoConta', on_delete=models.PROTECT,
                                                       related_name='analises_do_documento', blank=True, null=True)

    conta_associacao = models.ForeignKey('ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='analises_de_documento_da_conta', blank=True, null=True)

    resultado = models.CharField(
        'status',
        max_length=20,
        choices=RESULTADO_CHOICES,
        default=RESULTADO_CORRETO
    )

    status_realizacao = models.CharField(
        'Status de realização',
        max_length=15,
        choices=STATUS_REALIZACAO_CHOICES,
        default=STATUS_REALIZACAO_PENDENTE
    )

    justificativa = models.TextField('Justificativa', max_length=300, blank=True, null=True, default=None)

    despesa_incluida = models.ForeignKey('despesas.Despesa', on_delete=models.SET_NULL,
                                         related_name='analise_de_documento_que_incluiu_a_despesa', blank=True, null=True)

    receita_incluida = models.ForeignKey('receitas.Receita', on_delete=models.SET_NULL,
                                         related_name='analise_de_documento_que_incluiu_a_receita', blank=True, null=True)

    esclarecimentos = models.TextField('Esclarecimentos', max_length=300, blank=True, null=True, default=None)

    @property
    def requer_esclarecimentos(self):
        requer = self.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria=TipoAcertoDocumento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO
        ).exists()
        return requer

    @property
    def requer_inclusao_credito(self):
        requer = self.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria=TipoAcertoDocumento.CATEGORIA_INCLUSAO_CREDITO
        ).exists()
        return requer

    @property
    def requer_inclusao_gasto(self):
        requer = self.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria=TipoAcertoDocumento.CATEGORIA_INCLUSAO_GASTO
        ).exists()
        return requer

    @property
    def requer_ajuste_externo(self):
        requer = self.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria=TipoAcertoDocumento.CATEGORIA_AJUSTES_EXTERNOS
        ).exists()
        return requer

    def __str__(self):
        return f"Análise de documento {self.uuid} - Resultado:{self.resultado}"

    def altera_status_realizacao(self, novo_status, justificativa=None):
        self.justificativa = justificativa
        self.status_realizacao = novo_status
        self.save()

    def solicitacoes_de_acertos_total(self):
        total_solicitacoes = len(self.solicitacoes_de_ajuste_da_analise.all())

        return total_solicitacoes

    def solicitacoes_de_acertos_agrupado_por_categoria(self):
        from sme_ptrf_apps.core.api.serializers.tipo_acerto_documento_serializer import TipoAcertoDocumentoSerializer

        categoria_inclusao_credito = []
        categoria_inclusao_gasto = []
        categoria_ajuste_externo = []
        categoria_solicitacao_esclarecimento = []

        for solicitacao in self.solicitacoes_de_ajuste_da_analise.all():
            categoria = solicitacao.tipo_acerto.categoria

            dado_solicitacao = {
                "tipo_acerto": TipoAcertoDocumentoSerializer(solicitacao.tipo_acerto, many=False).data,
                "detalhamento": solicitacao.detalhamento,
                "id": solicitacao.id,
                "uuid": f"{solicitacao.uuid}",
                "copiado": solicitacao.copiado,
                "status_realizacao": solicitacao.status_realizacao,
                "justificativa": solicitacao.justificativa,
                "esclarecimentos": solicitacao.esclarecimentos,
                "ordem": None,
                "despesa_incluida": solicitacao.despesa_incluida.uuid if solicitacao.despesa_incluida else None,
                "receita_incluida": solicitacao.receita_incluida.uuid if solicitacao.receita_incluida else None
            }

            if categoria == TipoAcertoDocumento.CATEGORIA_INCLUSAO_CREDITO:
                categoria_inclusao_credito.append(dado_solicitacao)
            elif categoria == TipoAcertoDocumento.CATEGORIA_INCLUSAO_GASTO:
                categoria_inclusao_gasto.append(dado_solicitacao)
            elif categoria == TipoAcertoDocumento.CATEGORIA_AJUSTES_EXTERNOS:
                categoria_ajuste_externo.append(dado_solicitacao)
            elif categoria == TipoAcertoDocumento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO:
                categoria_solicitacao_esclarecimento.append(dado_solicitacao)

        result = {
            "analise_documento": f"{self.uuid}",
            "solicitacoes_acerto_por_categoria": self.monta_estrutura_solicitacoes_acerto_por_categoria(
                categoria_inclusao_credito,
                categoria_inclusao_gasto,
                categoria_ajuste_externo,
                categoria_solicitacao_esclarecimento
            )
        }

        result_com_ordem_calculada = self.calcula_ordem(result)

        return result_com_ordem_calculada

    @staticmethod
    def calcula_ordem(result):
        ordem = 1
        for categoria in result['solicitacoes_acerto_por_categoria']:
            for solicitacao in categoria["acertos"]:
                solicitacao["ordem"] = ordem
                ordem = ordem + 1

        return result

    def monta_estrutura_solicitacoes_acerto_por_categoria(
        self,
        categoria_inclusao_credito,
        categoria_inclusao_gasto,
        categoria_ajuste_externo,
        categoria_solicitacao_esclarecimento
    ):

        solicitacoes_acerto_por_categoria = []

        if categoria_inclusao_credito:
            solicitacoes_acerto_por_categoria.append({
                "acertos": categoria_inclusao_credito,
                "categoria": TipoAcertoDocumento.CATEGORIA_INCLUSAO_CREDITO,
                "analise_documento": f"{self.uuid}",
                "requer_inclusao_credito": self.requer_inclusao_credito
            })

        if categoria_inclusao_gasto:
            solicitacoes_acerto_por_categoria.append({
                "acertos": categoria_inclusao_gasto,
                "categoria": TipoAcertoDocumento.CATEGORIA_INCLUSAO_GASTO,
                "analise_documento": f"{self.uuid}",
                "requer_inclusao_gasto": self.requer_inclusao_gasto,
            })

        if categoria_ajuste_externo:
            solicitacoes_acerto_por_categoria.append({
                "acertos": categoria_ajuste_externo,
                "categoria": TipoAcertoDocumento.CATEGORIA_AJUSTES_EXTERNOS,
                "analise_documento": f"{self.uuid}",
                "requer_ajustes_externos": self.requer_ajuste_externo,
            })

        if categoria_solicitacao_esclarecimento:
            solicitacoes_acerto_por_categoria.append({
                "acertos": categoria_solicitacao_esclarecimento,
                "categoria": TipoAcertoDocumento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO,
                "analise_documento": f"{self.uuid}",
                "requer_esclarecimentos": self.requer_esclarecimentos,
            })

        return solicitacoes_acerto_por_categoria

    @classmethod
    def status_realizacao_choices_to_json(cls):
        return choices_to_json(cls.STATUS_REALIZACAO_CHOICES)

    class Meta:
        verbose_name = "Análise de documentos de PC"
        verbose_name_plural = "16.6) Análises de documentos de PC"


auditlog.register(AnaliseDocumentoPrestacaoConta)

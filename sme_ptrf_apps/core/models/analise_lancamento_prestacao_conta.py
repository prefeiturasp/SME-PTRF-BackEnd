from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from ...utils.choices_to_json import choices_to_json
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from django.db.models import UniqueConstraint, Q


class AnaliseLancamentoPrestacaoConta(ModeloBase):
    # Tags de informações de conferência de lançamentos
    TAG_AJUSTE = {"id": "1", "nome": "AJUSTE", "descricao": "O lançamento possui acertos para serem conferidos."}
    TAG_CORRETO = {"id": "2", "nome": "CORRETO", "descricao": "O lançamento está correto e/ou os acertos foram conferidos."}
    TAG_CONFERENCIA_AUTOMATICA = {"id": "3", "nome": "CONFERENCIA_AUTOMATICA", "descricao": "O lançamento possui acerto(s) que foram conferidos automaticamente pelo sistema."}
    TAG_NAO_CONFERIDO = {"id": "4", "nome": "NAO_CONFERIDO", "descricao": "Não conferido."}

    history = AuditlogHistoryField()

    # Status Choice
    RESULTADO_CORRETO = 'CORRETO'
    RESULTADO_AJUSTE = 'AJUSTE'

    RESULTADO_NOMES = {
        RESULTADO_CORRETO: 'Lançamento Correto',
        RESULTADO_AJUSTE: 'Ajuste necessário',
    }

    RESULTADO_CHOICES = (
        (RESULTADO_CORRETO, RESULTADO_NOMES[RESULTADO_CORRETO]),
        (RESULTADO_AJUSTE, RESULTADO_NOMES[RESULTADO_AJUSTE]),
    )

    # Tipo Lançamento Choice
    TIPO_LANCAMENTO_CREDITO = 'CREDITO'
    TIPO_LANCAMENTO_GASTO = 'GASTO'

    TIPO_LANCAMENTO_NOMES = {
        TIPO_LANCAMENTO_CREDITO: 'Crédito',
        TIPO_LANCAMENTO_GASTO: 'Gasto',
    }

    TIPO_LANCAMENTO_CHOICES = (
        (TIPO_LANCAMENTO_CREDITO, TIPO_LANCAMENTO_NOMES[TIPO_LANCAMENTO_CREDITO]),
        (TIPO_LANCAMENTO_GASTO, TIPO_LANCAMENTO_NOMES[TIPO_LANCAMENTO_GASTO]),
    )

    # Status realizacao choices
    STATUS_REALIZACAO_PENDENTE = 'PENDENTE'
    STATUS_REALIZACAO_REALIZADO = 'REALIZADO'
    STATUS_REALIZACAO_JUSTIFICADO = 'JUSTIFICADO'
    STATUS_REALIZACAO_REALIZADO_JUSTIFICADO = 'REALIZADO_JUSTIFICADO'
    STATUS_REALIZACAO_REALIZADO_PARCIALMENTE = 'REALIZADO_PARCIALMENTE'

    STATUS_REALIZACAO_NOMES = {
        STATUS_REALIZACAO_PENDENTE: 'Pendente',
        STATUS_REALIZACAO_REALIZADO: 'Realizado',
        STATUS_REALIZACAO_JUSTIFICADO: 'Justificado',
        STATUS_REALIZACAO_REALIZADO_JUSTIFICADO: 'Realizado e justificado',
        STATUS_REALIZACAO_REALIZADO_PARCIALMENTE: 'Realizado parcialmente',
    }

    STATUS_REALIZACAO_CHOICES = (
        (STATUS_REALIZACAO_PENDENTE, STATUS_REALIZACAO_NOMES[STATUS_REALIZACAO_PENDENTE]),
        (STATUS_REALIZACAO_REALIZADO, STATUS_REALIZACAO_NOMES[STATUS_REALIZACAO_REALIZADO]),
        (STATUS_REALIZACAO_JUSTIFICADO, STATUS_REALIZACAO_NOMES[STATUS_REALIZACAO_JUSTIFICADO]),
        (STATUS_REALIZACAO_REALIZADO_JUSTIFICADO, STATUS_REALIZACAO_NOMES[STATUS_REALIZACAO_REALIZADO_JUSTIFICADO]),
        (STATUS_REALIZACAO_REALIZADO_PARCIALMENTE, STATUS_REALIZACAO_NOMES[STATUS_REALIZACAO_REALIZADO_PARCIALMENTE]),
    )

    analise_prestacao_conta = models.ForeignKey('AnalisePrestacaoConta', on_delete=models.CASCADE,
                                                related_name='analises_de_lancamentos', blank=True, null=True)

    analise_prestacao_conta_auxiliar = models.ForeignKey('AnalisePrestacaoConta', on_delete=models.CASCADE,
                                                related_name='analises_de_lancamentos_auxiliar', blank=True, null=True)

    analise_corrigida_via_admin_action = models.BooleanField("Análise corrigida via admin action?", default=False)

    tipo_lancamento = models.CharField(
        'Tipo Lançamento',
        max_length=20,
        choices=TIPO_LANCAMENTO_CHOICES,
        default=TIPO_LANCAMENTO_CREDITO
    )

    despesa = models.ForeignKey('despesas.Despesa', on_delete=models.CASCADE,
                                related_name='analises_de_lancamento_da_despesa', blank=True, null=True)

    receita = models.ForeignKey('receitas.Receita', on_delete=models.CASCADE,
                                related_name='analises_de_lancamento_da_receita', blank=True, null=True)

    resultado = models.CharField(
        'Status',
        max_length=20,
        choices=RESULTADO_CHOICES,
        default=RESULTADO_CORRETO
    )

    status_realizacao = models.CharField(
        'Status de realização',
        max_length=40,
        choices=STATUS_REALIZACAO_CHOICES,
        default=STATUS_REALIZACAO_PENDENTE
    )

    devolucao_tesouro_atualizada = models.BooleanField("Devolução ao Tesouro Atualizada?", default=False)

    lancamento_atualizado = models.BooleanField("Lançamento Atualizado?", default=False)

    lancamento_excluido = models.BooleanField("Lançamento Excluído?", default=False)

    conciliacao_atualizada = models.BooleanField("Conciliação Atualizada?", default=False)

    houve_considerados_corretos_automaticamente = models.BooleanField("Houve considerados corretos automaticamente?", default=False)

    def __str__(self):
        return f"{self.analise_prestacao_conta} - Resultado:{self.resultado}"

    @classmethod
    def status_realizacao_choices_to_json(cls):
        return choices_to_json(cls.STATUS_REALIZACAO_CHOICES)

    @property
    def requer_atualizacao_devolucao_ao_tesouro(self):
        from . import TipoAcertoLancamento
        requer = self.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_DEVOLUCAO
        ).exists()
        return requer

    def passar_devolucao_tesouro_para_atualizada(self):
        self.devolucao_tesouro_atualizada = True
        self.save()
        return self

    def passar_devolucao_tesouro_para_nao_atualizada(self):
        from ..models import SolicitacaoAcertoLancamento
        from ..models import TipoAcertoLancamento

        self.devolucao_tesouro_atualizada = False
        devolucoes = self.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_DEVOLUCAO)

        for devolucao in devolucoes:
            if devolucao.status_realizacao == SolicitacaoAcertoLancamento.STATUS_REALIZACAO_REALIZADO:
                devolucao.altera_status_realizacao(novo_status=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE)

        self.save()
        return self

    @property
    def requer_atualizacao_lancamento(self):
        from . import TipoAcertoLancamento
        requer = self.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO
        ).exists()
        return requer

    def passar_lancamento_para_atualizado(self):
        self.lancamento_atualizado = True
        self.save()
        return self

    @property
    def requer_exclusao_lancamento(self):
        from . import TipoAcertoLancamento
        requer = self.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_EXCLUSAO_LANCAMENTO
        ).exists()
        return requer

    def passar_lancamento_para_excluido(self):
        self.lancamento_excluido = True
        self.save()
        return self

    @property
    def requer_ajustes_externos(self):
        from . import TipoAcertoLancamento
        requer = self.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_AJUSTES_EXTERNOS
        ).exists()
        return requer

    @property
    def requer_esclarecimentos(self):
        from . import TipoAcertoLancamento
        requer = self.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO
        ).exists()
        return requer

    @property
    def requer_conciliacao_lancamento(self):
        from . import TipoAcertoLancamento
        requer = self.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_CONCILIACAO_LANCAMENTO
        ).exists()
        return requer

    @property
    def requer_desconciliacao_lancamento(self):
        from . import TipoAcertoLancamento
        requer = self.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_DESCONCILIACAO_LANCAMENTO
        ).exists()
        return requer

    def solicitacoes_de_acertos_total(self):
        total_solicitacoes = len(self.solicitacoes_de_ajuste_da_analise.all())

        return total_solicitacoes

    def solicitacoes_de_acertos_agrupado_por_categoria(self):
        from sme_ptrf_apps.core.api.serializers.solicitacao_devolucao_ao_tesouro_serializer import \
            SolicitacaoDevolucaoAoTesouroRetrieveSerializer
        from sme_ptrf_apps.core.api.serializers.tipo_acerto_lancamento_serializer import TipoAcertoLancamentoSerializer
        from . import TipoAcertoLancamento

        categoria_devolucao_tesouro = []
        categoria_edicao_lancamento = []
        categoria_exclusao_lancamento = []
        categoria_ajuste_externo = []
        categoria_solicitacao_esclarecimento = []
        categoria_conciliacao_lancamento = []
        categoria_desconciliacao_lancamento = []

        for solicitacao in self.solicitacoes_de_ajuste_da_analise.all().order_by('id'):
            categoria = solicitacao.tipo_acerto.categoria
            devolucao_ao_tesouro = None

            if categoria == TipoAcertoLancamento.CATEGORIA_DEVOLUCAO:
                devolucao_ao_tesouro = SolicitacaoDevolucaoAoTesouroRetrieveSerializer(
                    solicitacao.solicitacao_devolucao_ao_tesouro, many=False).data

            dado_solicitacao = {
                "tipo_acerto": TipoAcertoLancamentoSerializer(solicitacao.tipo_acerto, many=False).data,
                "detalhamento": solicitacao.detalhamento,
                "devolucao_ao_tesouro": devolucao_ao_tesouro,
                "id": solicitacao.id,
                "uuid": f"{solicitacao.uuid}",
                "copiado": solicitacao.copiado,
                "status_realizacao": solicitacao.status_realizacao,
                "justificativa": solicitacao.justificativa,
                "esclarecimentos": solicitacao.esclarecimentos,
                "ordem": None
            }

            if categoria == TipoAcertoLancamento.CATEGORIA_DEVOLUCAO:
                categoria_devolucao_tesouro.append(dado_solicitacao)
            elif categoria == TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO:
                categoria_edicao_lancamento.append(dado_solicitacao)
            elif categoria == TipoAcertoLancamento.CATEGORIA_EXCLUSAO_LANCAMENTO:
                categoria_exclusao_lancamento.append(dado_solicitacao)
            elif categoria == TipoAcertoLancamento.CATEGORIA_AJUSTES_EXTERNOS:
                categoria_ajuste_externo.append(dado_solicitacao)
            elif categoria == TipoAcertoLancamento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO:
                categoria_solicitacao_esclarecimento.append(dado_solicitacao)
            elif categoria == TipoAcertoLancamento.CATEGORIA_CONCILIACAO_LANCAMENTO:
                categoria_conciliacao_lancamento.append(dado_solicitacao)
            elif categoria == TipoAcertoLancamento.CATEGORIA_DESCONCILIACAO_LANCAMENTO:
                categoria_desconciliacao_lancamento.append(dado_solicitacao)

        result = {
            "analise_lancamento": f"{self.uuid}",
            "solicitacoes_acerto_por_categoria": self.monta_estrutura_solicitacoes_acerto_por_categoria(
                categoria_devolucao_tesouro,
                categoria_edicao_lancamento,
                categoria_exclusao_lancamento,
                categoria_ajuste_externo,
                categoria_solicitacao_esclarecimento,
                categoria_conciliacao_lancamento,
                categoria_desconciliacao_lancamento
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

    @staticmethod
    def mensagem_lancamento_inativo(despesa, receita):
        if despesa:
            return despesa.mensagem_inativacao

        if receita:
            return receita.mensagem_inativacao

        return None

    def monta_estrutura_solicitacoes_acerto_por_categoria(
        self,
        categoria_devolucao_tesouro,
        categoria_edicao_lancamento,
        categoria_exclusao_lancamento,
        categoria_ajuste_externo,
        categoria_solicitacao_esclarecimento,
        categoria_conciliacao_lancamento,
        categoria_desconciliacao_lancamento
    ):
        from . import TipoAcertoLancamento

        solicitacoes_acerto_por_categoria = []

        if categoria_devolucao_tesouro:
            solicitacoes_acerto_por_categoria.append({
                "requer_atualizacao_devolucao_ao_tesouro": self.requer_atualizacao_devolucao_ao_tesouro,
                "devolucao_tesouro_atualizada": self.devolucao_tesouro_atualizada,
                "acertos": categoria_devolucao_tesouro,
                "categoria": TipoAcertoLancamento.CATEGORIA_DEVOLUCAO,
                "despesa": f"{self.despesa.uuid}" if self.despesa else None,
                "receita": f"{self.receita.uuid}" if self.receita else None,
                "analise_lancamento": f"{self.uuid}",
                "mensagem_inativa": None
            })

        if categoria_edicao_lancamento:
            solicitacoes_acerto_por_categoria.append({
                "requer_atualizacao_lancamento": self.requer_atualizacao_lancamento,
                "lancamento_atualizado": self.lancamento_atualizado,
                "acertos": categoria_edicao_lancamento,
                "categoria": TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO,
                "despesa": f"{self.despesa.uuid}" if self.despesa else None,
                "receita": f"{self.receita.uuid}" if self.receita else None,
                "analise_lancamento": f"{self.uuid}",
                "mensagem_inativa": None
            })

        if categoria_exclusao_lancamento:
            solicitacoes_acerto_por_categoria.append({
                "requer_exclusao_lancamento": self.requer_exclusao_lancamento,
                "lancamento_excluido": self.lancamento_excluido,
                "acertos": categoria_exclusao_lancamento,
                "categoria": TipoAcertoLancamento.CATEGORIA_EXCLUSAO_LANCAMENTO,
                "despesa": f"{self.despesa.uuid}" if self.despesa else None,
                "receita": f"{self.receita.uuid}" if self.receita else None,
                "analise_lancamento": f"{self.uuid}",
                "mensagem_inativa": self.mensagem_lancamento_inativo(self.despesa, self.receita)
            })

        if categoria_ajuste_externo:
            solicitacoes_acerto_por_categoria.append({
                "requer_ajustes_externos": self.requer_ajustes_externos,
                "acertos": categoria_ajuste_externo,
                "categoria": TipoAcertoLancamento.CATEGORIA_AJUSTES_EXTERNOS,
                "despesa": f"{self.despesa.uuid}" if self.despesa else None,
                "receita": f"{self.receita.uuid}" if self.receita else None,
                "analise_lancamento": f"{self.uuid}",
                "mensagem_inativa": None
            })

        if categoria_solicitacao_esclarecimento:
            solicitacoes_acerto_por_categoria.append({
                "requer_esclarecimentos": self.requer_esclarecimentos,
                "acertos": categoria_solicitacao_esclarecimento,
                "categoria": TipoAcertoLancamento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO,
                "despesa": f"{self.despesa.uuid}" if self.despesa else None,
                "receita": f"{self.receita.uuid}" if self.receita else None,
                "analise_lancamento": f"{self.uuid}",
                "mensagem_inativa": None
            })

        if categoria_conciliacao_lancamento:
            solicitacoes_acerto_por_categoria.append({
                "requer_conciliacao_lancamento": self.requer_conciliacao_lancamento,
                "conciliacao_atualizada": self.conciliacao_atualizada,
                "acertos": categoria_conciliacao_lancamento,
                "categoria": TipoAcertoLancamento.CATEGORIA_CONCILIACAO_LANCAMENTO,
                "despesa": f"{self.despesa.uuid}" if self.despesa else None,
                "receita": f"{self.receita.uuid}" if self.receita else None,
                "analise_lancamento": f"{self.uuid}",
                "mensagem_inativa": None
            })

        if categoria_desconciliacao_lancamento:
            solicitacoes_acerto_por_categoria.append({
                "requer_conciliacao_lancamento": self.requer_desconciliacao_lancamento,
                "conciliacao_atualizada": self.conciliacao_atualizada,
                "acertos": categoria_desconciliacao_lancamento,
                "categoria": TipoAcertoLancamento.CATEGORIA_DESCONCILIACAO_LANCAMENTO,
                "despesa": f"{self.despesa.uuid}" if self.despesa else None,
                "receita": f"{self.receita.uuid}" if self.receita else None,
                "analise_lancamento": f"{self.uuid}",
                "mensagem_inativa": None
            })

        return solicitacoes_acerto_por_categoria

    def calcula_status_realizacao_analise_lancamento(self):
        from . import SolicitacaoAcertoLancamento

        novo_status = None

        solicitacoes_realizadas = self.solicitacoes_de_ajuste_da_analise.filter(
            status_realizacao=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_REALIZADO).exists()

        solicitacoes_justificadas = self.solicitacoes_de_ajuste_da_analise.filter(
            status_realizacao=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_JUSTIFICADO).exists()

        solicitacoes_nao_realizadas = self.solicitacoes_de_ajuste_da_analise.filter(
            status_realizacao=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE).exists()

        if solicitacoes_realizadas and not solicitacoes_justificadas and not solicitacoes_nao_realizadas:
            novo_status = AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO
        elif solicitacoes_justificadas and not solicitacoes_realizadas and not solicitacoes_nao_realizadas:
            novo_status = AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_JUSTIFICADO
        elif solicitacoes_nao_realizadas and not solicitacoes_realizadas and not solicitacoes_justificadas:
            novo_status = AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE
        elif solicitacoes_realizadas and solicitacoes_justificadas and not solicitacoes_nao_realizadas:
            novo_status = AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO_JUSTIFICADO
        elif solicitacoes_realizadas and solicitacoes_nao_realizadas and not solicitacoes_justificadas:
            novo_status = AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO_PARCIALMENTE
        elif solicitacoes_justificadas and solicitacoes_nao_realizadas and not solicitacoes_realizadas:
            novo_status = AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO_PARCIALMENTE
        elif solicitacoes_justificadas and solicitacoes_realizadas and solicitacoes_nao_realizadas:
            novo_status = AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO_PARCIALMENTE

        self.status_realizacao = novo_status
        self.save()

    def passar_lancamento_para_conciliado(self, periodo):
        from ..models import SolicitacaoAcertoLancamento
        from ..models import TipoAcertoLancamento

        for rateio in self.despesa.rateios.all():
            rateio.marcar_conferido(periodo_conciliacao=periodo)

        self.conciliacao_atualizada = True if self.requer_conciliacao_lancamento else False
        self.save()

        if self.requer_desconciliacao_lancamento:
            solicitacoes_de_desconciliacao = self.solicitacoes_de_ajuste_da_analise.filter(
                tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_DESCONCILIACAO_LANCAMENTO)

            for solicitacao in solicitacoes_de_desconciliacao:
                if solicitacao.status_realizacao == SolicitacaoAcertoLancamento.STATUS_REALIZACAO_REALIZADO:
                    solicitacao.altera_status_realizacao(
                        novo_status=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE)

        return self

    def passar_lancamento_para_desconciliado(self):
        from ..models import SolicitacaoAcertoLancamento
        from ..models import TipoAcertoLancamento

        for rateio in self.despesa.rateios.all():
            rateio.desmarcar_conferido()

        self.conciliacao_atualizada = True if self.requer_desconciliacao_lancamento else False
        self.save()

        if self.requer_conciliacao_lancamento:
            solicitacoes_de_conciliacao = self.solicitacoes_de_ajuste_da_analise.filter(
                tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_CONCILIACAO_LANCAMENTO)

            for solicitacao in solicitacoes_de_conciliacao:
                if solicitacao.status_realizacao == SolicitacaoAcertoLancamento.STATUS_REALIZACAO_REALIZADO:
                    solicitacao.altera_status_realizacao(
                        novo_status=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE)

        return self

    @classmethod
    def get_tags_informacoes_de_conferencia_list(cls):
        return [cls.TAG_AJUSTE, cls.TAG_CORRETO, cls.TAG_CONFERENCIA_AUTOMATICA, cls.TAG_NAO_CONFERIDO]


    class Meta:
        verbose_name = "Análise de lançamento"
        verbose_name_plural = "16.1) Análises de lançamentos"
        constraints = [
            UniqueConstraint(fields=['analise_prestacao_conta', 'receita'],
                             condition=Q(despesa__isnull=True),
                             name='unique_constraint_analise_pc_e_receita'),

            UniqueConstraint(fields=['analise_prestacao_conta', 'despesa'],
                             condition=Q(receita__isnull=True),
                             name='unique_constraint_analise_pc_e_despesa'),
        ]


auditlog.register(AnaliseLancamentoPrestacaoConta)

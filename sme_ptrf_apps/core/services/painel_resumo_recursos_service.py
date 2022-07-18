from datetime import datetime

from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.core.services.periodo_services import status_prestacao_conta_associacao
from sme_ptrf_apps.core.services.resumo_rescursos_service import ResumoRecursosService


class PainelResumoRecursosCardConta:
    def __init__(self, periodo, conta_associacao):
        ...


class PainelResumoRecursosCardAcao:
    def __init__(self, periodo, acao_associacao, conta_associacao=None):
        self.acao_associacao_uuid = acao_associacao.uuid
        self.acao_associacao_nome = acao_associacao.acao.nome

        self.resumo_recursos = ResumoRecursosService.resumo_recursos(
            periodo=periodo,
            acao_associacao=acao_associacao,
            conta_associacao=conta_associacao
        )
        self.saldo_reprogramado = self.resumo_recursos.saldo_anterior.total_geral
        self.saldo_reprogramado_capital = self.resumo_recursos.saldo_anterior.total_capital
        self.saldo_reprogramado_custeio = self.resumo_recursos.saldo_anterior.total_custeio
        self.saldo_reprogramado_livre = self.resumo_recursos.saldo_anterior.total_livre

        self.receitas_no_periodo = self.resumo_recursos.receitas.total_geral

        self.repasses_no_periodo = self.resumo_recursos.receitas.repasses_geral
        self.repasses_no_periodo_capital = self.resumo_recursos.receitas.repasses_capital
        self.repasses_no_periodo_custeio = self.resumo_recursos.receitas.repasses_custeio
        self.repasses_no_periodo_livre = self.resumo_recursos.receitas.repasses_livre

        self.outras_receitas_no_periodo = self.resumo_recursos.receitas.outras_geral
        self.outras_receitas_no_periodo_capital = self.resumo_recursos.receitas.outras_capital
        self.outras_receitas_no_periodo_custeio = self.resumo_recursos.receitas.outras_custeio
        self.outras_receitas_no_periodo_livre = self.resumo_recursos.receitas.outras_livre

        self.despesas_no_periodo = self.resumo_recursos.despesas.total_geral
        self.despesas_no_periodo_capital = self.resumo_recursos.despesas.total_capital
        self.despesas_no_periodo_custeio = self.resumo_recursos.despesas.total_custeio

        self.saldo_atual_total = self.resumo_recursos.saldo_posterior.total_geral
        self.saldo_atual_capital = self.resumo_recursos.saldo_posterior.total_capital
        self.saldo_atual_custeio = self.resumo_recursos.saldo_posterior.total_custeio
        self.saldo_atual_livre = self.resumo_recursos.saldo_posterior.total_livre


class PainelResumoRecursos:
    def __init__(self, associacao, periodo, conta_associacao):
        self.associacao = associacao
        self.periodo_referencia = periodo
        self.data_inicio_realizacao_despesas = periodo.data_inicio_realizacao_despesas
        self.data_fim_realizacao_despesas = periodo.data_fim_realizacao_despesas
        self.data_prevista_repasse = periodo.data_prevista_repasse
        self.ultima_atualizacao = datetime.now()
        self.prestacao_contas_status = status_prestacao_conta_associacao(
            periodo_uuid=self.periodo_referencia.uuid,
            associacao_uuid=self.associacao.uuid
        )
        self.conta_associacao = conta_associacao
        self.info_conta = PainelResumoRecursosCardConta(periodo=periodo, conta_associacao=conta_associacao)

        self.__set_info_acoes()

    def __set_info_acoes(self):
        self.info_acoes = []
        acoes_associacao = Associacao.acoes_da_associacao(associacao_uuid=self.associacao.uuid)
        for acao in acoes_associacao:
            self.info_acoes.append(
                PainelResumoRecursosCardAcao(
                    periodo=self.periodo_referencia,
                    acao_associacao=acao,
                    conta_associacao=self.conta_associacao
                )
            )


class PainelResumoRecursosService:
    @classmethod
    def painel_resumo_recursos(cls, associacao, periodo, conta_associacao=None):
        return PainelResumoRecursos(associacao=associacao, periodo=periodo, conta_associacao=conta_associacao)


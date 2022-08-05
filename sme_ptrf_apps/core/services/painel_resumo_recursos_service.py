from datetime import datetime
from decimal import Decimal

from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.core.services.periodo_services import status_prestacao_conta_associacao
from sme_ptrf_apps.core.services.resumo_rescursos_service import ResumoRecursosService


class PainelResumoRecursosCardConta:
    def __init__(self, periodo, conta_associacao):
        self.conta_associacao_uuid = conta_associacao.uuid
        self.conta_associacao_nome = conta_associacao.tipo_conta.nome
        self.periodo = periodo

        self.saldo_reprogramado = Decimal(0.00)
        self.saldo_reprogramado_capital = Decimal(0.00)
        self.saldo_reprogramado_custeio = Decimal(0.00)
        self.saldo_reprogramado_livre = Decimal(0.00)

        self.receitas_no_periodo = Decimal(0.00)

        self.repasses_no_periodo = Decimal(0.00)
        self.repasses_no_periodo_capital = Decimal(0.00)
        self.repasses_no_periodo_custeio = Decimal(0.00)
        self.repasses_no_periodo_livre = Decimal(0.00)

        self.outras_receitas_no_periodo = Decimal(0.00)
        self.outras_receitas_no_periodo_capital = Decimal(0.00)
        self.outras_receitas_no_periodo_custeio = Decimal(0.00)
        self.outras_receitas_no_periodo_livre = Decimal(0.00)

        self.despesas_no_periodo = Decimal(0.00)
        self.despesas_no_periodo_capital = Decimal(0.00)
        self.despesas_no_periodo_custeio = Decimal(0.00)

        self.saldo_atual_total = Decimal(0.00)
        self.saldo_atual_capital = Decimal(0.00)
        self.saldo_atual_custeio = Decimal(0.00)
        self.saldo_atual_livre = Decimal(0.00)


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
    def __init__(self, associacao, periodo, conta_associacao=None):
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

        self.__set_info_acoes()
        self.__set_info_contas()

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

    def __set_info_contas(self):
        if not self.conta_associacao:
            self.info_conta = None
            return

        self.info_conta = PainelResumoRecursosCardConta(
            periodo=self.periodo_referencia,
            conta_associacao=self.conta_associacao
        )

        campos_nao_somaveis = ['acao_associacao_uuid', 'acao_associacao_nome', 'resumo_recursos']
        for info_acao in self.info_acoes:
            valores_info_acao = vars(info_acao)
            for campo, valor_acao in valores_info_acao.items():
                if campo not in campos_nao_somaveis:
                    setattr(self.info_conta, campo, getattr(self.info_conta, campo) + valor_acao)

    @staticmethod
    def __object_to_dict(obj, except_fields=None):
        if except_fields is None:
            except_fields = []

        obj_dict = vars(obj)
        for field in except_fields:
            obj_dict.pop(field)

        return obj_dict

    def to_json(self):
        json_info_acoes = []
        for info_acao in self.info_acoes:
            json_info_acoes.append(self.__object_to_dict(info_acao, except_fields=['resumo_recursos']))

        if self.info_conta:
            json_info_conta = self.__object_to_dict(self.info_conta, except_fields=['periodo'])
        else:
            json_info_conta = None

        json = {
            'associacao': self.associacao.uuid,
            'periodo_referencia': self.periodo_referencia.referencia,
            'prestacao_contas_status': self.prestacao_contas_status,
            'data_inicio_realizacao_despesas': f'{self.data_inicio_realizacao_despesas}',
            'data_fim_realizacao_despesas': f'{self.data_fim_realizacao_despesas}',
            'data_prevista_repasse': f'{self.data_prevista_repasse}',
            'ultima_atualizacao': f'{self.ultima_atualizacao}',
            'info_acoes': json_info_acoes,
            'info_conta': json_info_conta
        }

        return json


class PainelResumoRecursosService:
    @classmethod
    def painel_resumo_recursos(cls, associacao, periodo=None, conta_associacao=None):
        return PainelResumoRecursos(associacao=associacao, periodo=periodo, conta_associacao=conta_associacao)


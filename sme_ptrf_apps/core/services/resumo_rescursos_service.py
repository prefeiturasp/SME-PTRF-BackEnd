from django.db.models import Sum

from sme_ptrf_apps.receitas.models import Receita
from sme_ptrf_apps.despesas.models import RateioDespesa


class ResumoRecursosException(Exception):
    pass


class ResumoDespesas:
    def __init__(self, periodo, acao_associacao, conta_associacao):
        self.periodo = periodo
        self.acao_associacao = acao_associacao
        self.conta_associacao = conta_associacao
        self.total_custeio = 0
        self.total_capital = 0
        self.total_geral = 0

        self.__set_total_despesas_do_periodo()

    def __set_total_despesas_do_periodo(self):
        despesas = RateioDespesa.rateios_da_acao_associacao_no_periodo(
            acao_associacao=self.acao_associacao,
            conta_associacao=self.conta_associacao,
            periodo=self.periodo,
        )

        totais_despesa_por_aplicacao = despesas.values('aplicacao_recurso').order_by('aplicacao_recurso').annotate(
            valor_total_aplicacao=Sum('valor_rateio'))

        for total in totais_despesa_por_aplicacao:
            self.total_geral += total['valor_total_aplicacao']

            if total['aplicacao_recurso'] == 'CUSTEIO':
                self.total_custeio += total['valor_total_aplicacao']
            elif total['aplicacao_recurso'] == 'CAPITAL':
                self.total_capital += total['valor_total_aplicacao']
            else:
                erro = f'Existem rateios com aplicação desconhecida. Aplicação:{total["aplicacao_recurso"] }'
                raise ResumoRecursosException(erro)


class ResumoReceitas:
    def __init__(self, periodo, acao_associacao, conta_associacao):
        self.periodo = periodo
        self.acao_associacao = acao_associacao
        self.conta_associacao = conta_associacao
        self.total_custeio = 0
        self.total_capital = 0
        self.total_livre = 0
        self.total_geral = 0

        self.__set_total_receitas_do_periodo()

    def __set_total_receitas_do_periodo(self):
        receitas = Receita.receitas_da_acao_associacao_no_periodo(
            acao_associacao=self.acao_associacao,
            conta_associacao=self.conta_associacao,
            periodo=self.periodo,
        )
        totais_receita_por_aplicacao = receitas.values('categoria_receita').order_by('categoria_receita').annotate(
            valor_total_categoria=Sum('valor'))

        for total in totais_receita_por_aplicacao:
            self.total_geral += total['valor_total_categoria']

            if total['categoria_receita'] == 'CUSTEIO':
                self.total_custeio += total['valor_total_categoria']
            elif total['categoria_receita'] == 'CAPITAL':
                self.total_capital += total['valor_total_categoria']
            elif total['categoria_receita'] == 'LIVRE':
                self.total_livre += total['valor_total_categoria']
            else:
                erro = f'Existem receitas com categoria desconhecida. Categoria:{total["categoria_receita"]}'
                raise ResumoRecursosException(erro)


class ResumoRecursos:

    def __init__(self, periodo, acao_associacao, conta_associacao):
        self.periodo = periodo
        self.acao_associacao = acao_associacao
        self.conta_associacao = conta_associacao
        self.saldo_anterior = 0.00
        self.receitas = ResumoReceitas(periodo, acao_associacao, conta_associacao)
        self.despesas = ResumoDespesas(periodo, acao_associacao, conta_associacao)
        self.saldo_posterior = 0.00


class ResumoRecursosService:
    @classmethod
    def resumo_recursos(cls, periodo, acao_associacao, conta_associacao=None):
        return ResumoRecursos(periodo=periodo, acao_associacao=acao_associacao, conta_associacao=conta_associacao)


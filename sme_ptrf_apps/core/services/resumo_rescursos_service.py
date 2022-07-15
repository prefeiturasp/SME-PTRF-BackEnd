from decimal import Decimal

from django.db.models import Sum

from sme_ptrf_apps.core.models import FechamentoPeriodo
from sme_ptrf_apps.receitas.models import Receita
from sme_ptrf_apps.despesas.models import RateioDespesa


class ResumoRecursosException(Exception):
    pass


class ResumoSaldo:
    def __init__(self, periodo, acao_associacao, conta_associacao, total_custeio=Decimal(0.00), total_capital=Decimal(0.00), total_livre=Decimal(0.00)):
        self.periodo = periodo
        self.acao_associacao = acao_associacao
        self.conta_associacao = conta_associacao
        self.total_custeio = total_custeio
        self.total_capital = total_capital
        self.total_livre = total_livre
        self.total_geral = total_custeio + total_capital + total_livre


class ResumoDespesas:
    def __init__(self, periodo, acao_associacao, conta_associacao):
        self.periodo = periodo
        self.acao_associacao = acao_associacao
        self.conta_associacao = conta_associacao
        self.total_custeio = Decimal(0.00)
        self.total_capital = Decimal(0.00)
        self.total_geral = Decimal(0.00)

        self.__set_totais_despesas()

    def __set_totais_despesas(self):
        fechamentos_no_periodo = FechamentoPeriodo.fechamentos_da_acao_no_periodo(
            periodo=self.periodo,
            acao_associacao=self.acao_associacao,
            conta_associacao=self.conta_associacao,
        )

        if fechamentos_no_periodo:
            self.__set_totais_despesas_pelos_fechamentos(fechamentos=fechamentos_no_periodo)
        else:
            self.__set_total_despesas_pelo_movimento_do_periodo()

        self.total_geral += self.total_custeio + self.total_capital

    def __set_totais_despesas_pelos_fechamentos(self, fechamentos):
        self.total_custeio = Decimal(0.00)
        self.total_capital = Decimal(0.00)

        for fechamento in fechamentos:
            self.total_custeio += fechamento.total_despesas_custeio
            self.total_capital += fechamento.total_despesas_capital

    def __set_total_despesas_pelo_movimento_do_periodo(self):
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
        self.total_custeio = Decimal(0.00)
        self.total_capital = Decimal(0.00)
        self.total_livre = Decimal(0.00)
        self.total_geral = Decimal(0.00)

        self.__set_totais_receitas()

    def __set_totais_receitas(self):
        fechamentos_no_periodo = FechamentoPeriodo.fechamentos_da_acao_no_periodo(
            periodo=self.periodo,
            acao_associacao=self.acao_associacao,
            conta_associacao=self.conta_associacao,
        )

        if fechamentos_no_periodo:
            self.__set_totais_receitas_pelos_fechamentos(fechamentos=fechamentos_no_periodo)
        else:
            self.__set_totais_receitas_pelo_movimento_do_periodo()

        self.total_geral += self.total_custeio + self.total_capital + self.total_livre

    def __set_totais_receitas_pelos_fechamentos(self, fechamentos):
        self.total_custeio = Decimal(0.00)
        self.total_capital = Decimal(0.00)
        self.total_livre = Decimal(0.00)

        for fechamento in fechamentos:
            self.total_custeio += fechamento.total_receitas_custeio
            self.total_capital += fechamento.total_receitas_capital
            self.total_livre += fechamento.total_receitas_livre

    def __set_totais_receitas_pelo_movimento_do_periodo(self):
        receitas = Receita.receitas_da_acao_associacao_no_periodo(
            acao_associacao=self.acao_associacao,
            conta_associacao=self.conta_associacao,
            periodo=self.periodo,
        )
        totais_receita_por_aplicacao = receitas.values('categoria_receita').order_by('categoria_receita').annotate(
            valor_total_categoria=Sum('valor'))

        for total in totais_receita_por_aplicacao:
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
        self.receitas = ResumoReceitas(periodo, acao_associacao, conta_associacao)
        self.despesas = ResumoDespesas(periodo, acao_associacao, conta_associacao)

        self.__set_saldos()

    def __set_saldos(self):
        fechamentos_no_periodo = FechamentoPeriodo.fechamentos_da_acao_no_periodo(
            periodo=self.periodo,
            acao_associacao=self.acao_associacao,
            conta_associacao=self.conta_associacao,
        )

        if fechamentos_no_periodo:
            self.__set_saldos_pelos_fechamentos(fechamentos=fechamentos_no_periodo)
        else:
            self.__set_saldos_por_calculo()

    def __set_saldos_pelos_fechamentos(self, fechamentos):
        saldo_anterior_custeio = Decimal(0.00)
        saldo_anterior_capital = Decimal(0.00)
        saldo_anterior_livre = Decimal(0.00)

        saldo_posterior_custeio = Decimal(0.00)
        saldo_posterior_capital = Decimal(0.00)
        saldo_posterior_livre = Decimal(0.00)

        for fechamento in fechamentos:
            saldo_anterior_custeio += fechamento.saldo_anterior_custeio
            saldo_anterior_capital += fechamento.saldo_anterior_capital
            saldo_anterior_livre += fechamento.saldo_anterior_livre

            saldo_posterior_custeio += fechamento.saldo_reprogramado_custeio
            saldo_posterior_capital += fechamento.saldo_reprogramado_capital
            saldo_posterior_livre += fechamento.saldo_reprogramado_livre

        self.saldo_anterior = ResumoSaldo(
            periodo=self.periodo,
            acao_associacao=self.acao_associacao,
            conta_associacao=self.conta_associacao,
            total_custeio=saldo_anterior_custeio,
            total_capital=saldo_anterior_capital,
            total_livre=saldo_anterior_livre,
        )

        self.saldo_posterior = ResumoSaldo(
            periodo=self.periodo,
            acao_associacao=self.acao_associacao,
            conta_associacao=self.conta_associacao,
            total_custeio=saldo_posterior_custeio,
            total_capital=saldo_posterior_capital,
            total_livre=saldo_posterior_livre,
        )

    def __set_saldos_por_calculo(self):
        if self.periodo.periodo_anterior:
            resumo_anterior = ResumoRecursos(self.periodo.periodo_anterior, self.acao_associacao, self.conta_associacao)
            self.saldo_anterior = resumo_anterior.saldo_posterior
        else:
            saldo_zerado = ResumoSaldo(self.periodo, self.acao_associacao, self.conta_associacao)
            self.saldo_anterior = saldo_zerado

        saldo_posterior_custeio = (
            self.saldo_anterior.total_custeio
            + self.receitas.total_custeio
            - self.despesas.total_custeio
        )

        saldo_posterior_capital = (
            self.saldo_anterior.total_capital
            + self.receitas.total_capital
            - self.despesas.total_capital
        )

        saldo_posterior_livre = (
            self.saldo_anterior.total_livre
            + self.receitas.total_livre
        )

        self.saldo_posterior = ResumoSaldo(
            periodo=self.periodo,
            acao_associacao=self.acao_associacao,
            conta_associacao=self.conta_associacao,
            total_custeio=saldo_posterior_custeio,
            total_capital=saldo_posterior_capital,
            total_livre=saldo_posterior_livre,
        )


class ResumoRecursosService:
    @classmethod
    def resumo_recursos(cls, periodo, acao_associacao, conta_associacao=None):
        return ResumoRecursos(periodo=periodo, acao_associacao=acao_associacao, conta_associacao=conta_associacao)


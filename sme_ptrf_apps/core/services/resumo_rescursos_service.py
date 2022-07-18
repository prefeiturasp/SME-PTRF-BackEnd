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
    def __init__(self, periodo, acao_associacao, conta_associacao, fechamentos_no_periodo):
        self.periodo = periodo
        self.acao_associacao = acao_associacao
        self.conta_associacao = conta_associacao
        self.total_custeio = Decimal(0.00)
        self.total_capital = Decimal(0.00)
        self.total_geral = Decimal(0.00)

        self.fechamentos_no_periodo = fechamentos_no_periodo

        self.__set_totais_despesas()

    def __set_totais_despesas(self):
        if self.fechamentos_no_periodo:
            self.__set_totais_despesas_pelos_fechamentos()
        else:
            self.__set_total_despesas_pelo_movimento_do_periodo()

        self.total_geral += self.total_custeio + self.total_capital

    def __set_totais_despesas_pelos_fechamentos(self):
        self.total_custeio = Decimal(0.00)
        self.total_capital = Decimal(0.00)

        for fechamento in self.fechamentos_no_periodo:
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
            if total['aplicacao_recurso'] == 'CUSTEIO':
                self.total_custeio += total['valor_total_aplicacao']
            elif total['aplicacao_recurso'] == 'CAPITAL':
                self.total_capital += total['valor_total_aplicacao']
            else:
                erro = f'Existem rateios com aplicação desconhecida. Aplicação:{total["aplicacao_recurso"] }'
                raise ResumoRecursosException(erro)


class ResumoReceitas:
    def __init__(self, periodo, acao_associacao, conta_associacao, fechamentos_no_periodo):
        self.periodo = periodo
        self.acao_associacao = acao_associacao
        self.conta_associacao = conta_associacao

        self.fechamentos_no_periodo = fechamentos_no_periodo

        self.__set_totais_receitas()

    def __set_totais_receitas(self):
        self.__set_totais_receitas_com_zero()

        if self.fechamentos_no_periodo:
            self.__set_totais_receitas_pelos_fechamentos()
        else:
            self.__set_totais_receitas_pelo_movimento_do_periodo()

        self.total_geral = self.total_custeio + self.total_capital + self.total_livre
        self.repasses_geral = self.repasses_custeio + self.repasses_capital + self.repasses_livre
        self.outras_geral = self.outras_custeio + self.outras_capital + self.outras_livre

    def __set_totais_receitas_com_zero(self):
        self.total_custeio = Decimal(0.00)
        self.total_capital = Decimal(0.00)
        self.total_livre = Decimal(0.00)

        self.repasses_custeio = Decimal(0.00)
        self.repasses_capital = Decimal(0.00)
        self.repasses_livre = Decimal(0.00)

        self.outras_custeio = Decimal(0.00)
        self.outras_capital = Decimal(0.00)
        self.outras_livre = Decimal(0.00)

    def __set_totais_receitas_pelos_fechamentos(self):
        for fechamento in self.fechamentos_no_periodo:
            self.total_custeio += fechamento.total_receitas_custeio
            self.total_capital += fechamento.total_receitas_capital
            self.total_livre += fechamento.total_receitas_livre

            self.repasses_custeio += fechamento.total_repasses_custeio
            self.repasses_capital += fechamento.total_repasses_capital
            self.repasses_livre += fechamento.total_repasses_livre

            self.outras_custeio += (fechamento.total_receitas_custeio - fechamento.total_repasses_custeio)
            self.outras_capital += (fechamento.total_receitas_capital - fechamento.total_repasses_capital)
            self.outras_livre += (fechamento.total_receitas_livre - fechamento.total_repasses_livre)

    def __set_totais_receitas_pelo_movimento_do_periodo(self):
        receitas = Receita.receitas_da_acao_associacao_no_periodo(
            acao_associacao=self.acao_associacao,
            conta_associacao=self.conta_associacao,
            periodo=self.periodo,
        )
        for receita in receitas.all():
            if receita.categoria_receita not in ['CUSTEIO', 'CAPITAL', 'LIVRE']:
                erro = f'Categoria de receita desconhecida. Categoria:{receita.categoria_receita} Receita:{receita.id}'
                raise ResumoRecursosException(erro)

            if receita.tipo_receita.e_repasse:
                self.repasses_custeio += receita.valor if receita.categoria_receita == 'CUSTEIO' else Decimal(0.00)
                self.repasses_capital += receita.valor if receita.categoria_receita == 'CAPITAL' else Decimal(0.00)
                self.repasses_livre += receita.valor if receita.categoria_receita == 'LIVRE' else Decimal(0.00)
            else:
                self.outras_custeio += receita.valor if receita.categoria_receita == 'CUSTEIO' else Decimal(0.00)
                self.outras_capital += receita.valor if receita.categoria_receita == 'CAPITAL' else Decimal(0.00)
                self.outras_livre += receita.valor if receita.categoria_receita == 'LIVRE' else Decimal(0.00)

        self.total_custeio = self.repasses_custeio + self.outras_custeio
        self.total_capital = self.repasses_capital + self.outras_capital
        self.total_livre = self.repasses_livre + self.outras_livre


class ResumoRecursos:

    def __init__(self, periodo, acao_associacao, conta_associacao):
        self.periodo = periodo
        self.acao_associacao = acao_associacao
        self.conta_associacao = conta_associacao

        self.fechamentos_no_periodo = FechamentoPeriodo.fechamentos_da_acao_no_periodo(
            periodo=self.periodo,
            acao_associacao=self.acao_associacao,
            conta_associacao=self.conta_associacao,
        )

        self.receitas = ResumoReceitas(periodo, acao_associacao, conta_associacao, fechamentos_no_periodo=self.fechamentos_no_periodo)
        self.despesas = ResumoDespesas(periodo, acao_associacao, conta_associacao, fechamentos_no_periodo=self.fechamentos_no_periodo)

        self.__set_saldos()

    def __set_saldos(self):
        if self.fechamentos_no_periodo:
            self.__set_saldos_pelos_fechamentos()
        else:
            self.__set_saldos_por_calculo()

    def __set_saldos_pelos_fechamentos(self):
        saldo_anterior_custeio = Decimal(0.00)
        saldo_anterior_capital = Decimal(0.00)
        saldo_anterior_livre = Decimal(0.00)

        saldo_posterior_custeio = Decimal(0.00)
        saldo_posterior_capital = Decimal(0.00)
        saldo_posterior_livre = Decimal(0.00)

        for fechamento in self.fechamentos_no_periodo:
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


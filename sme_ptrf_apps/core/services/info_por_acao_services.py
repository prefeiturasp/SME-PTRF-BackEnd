import datetime
import logging
from decimal import Decimal
from django.db.models import Sum

from ..models import FechamentoPeriodo, Associacao, AcaoAssociacao, ContaAssociacao, Periodo, Parametros
from ..services.periodo_services import status_prestacao_conta_associacao
from ...despesas.models import RateioDespesa, Despesa
from ...despesas.tipos_aplicacao_recurso import APLICACAO_CUSTEIO, APLICACAO_CAPITAL
from ...receitas.models import Receita, Repasse

logger = logging.getLogger(__name__)


def especificacoes_despesas_acao_associacao_no_periodo(acao_associacao, periodo, exclude_despesa=None, conta=None):
    fechamentos_periodo = FechamentoPeriodo.fechamentos_da_acao_no_periodo(acao_associacao=acao_associacao,
                                                                           periodo=periodo, conta_associacao=conta)
    if fechamentos_periodo:
        fechamento = fechamentos_periodo.first()
        aplicacoes = {
            APLICACAO_CAPITAL: fechamento.especificacoes_despesas_capital,
            APLICACAO_CUSTEIO: fechamento.especificacoes_despesas_custeio,
        }
        return aplicacoes
    else:
        return RateioDespesa.especificacoes_dos_rateios_da_acao_associacao_no_periodo(acao_associacao=acao_associacao,
                                                                                      periodo=periodo,
                                                                                      conta_associacao=conta,
                                                                                      exclude_despesa=exclude_despesa)


def saldos_insuficientes_para_rateios(rateios, periodo, exclude_despesa=None):
    def sumariza_rateios_por_conta_acao_aplicacao(rateios):
        totalizador_contas = dict()
        sumarizacao_conta_acao_aplicacao = dict()

        for rateio in rateios:
            conta_key = rateio['conta_associacao']
            acao_key = rateio['acao_associacao']
            aplicacao = rateio['aplicacao_recurso']
            valor_rateio = Decimal(rateio['valor_rateio'])

            if conta_key not in sumarizacao_conta_acao_aplicacao:
                sumarizacao_conta_acao_aplicacao[conta_key] = dict()
            if acao_key not in sumarizacao_conta_acao_aplicacao[conta_key]:
                sumarizacao_conta_acao_aplicacao[conta_key][acao_key] = {'CAPITAL': 0, 'CUSTEIO': 0}

            sumarizacao_conta_acao_aplicacao[conta_key][acao_key][aplicacao] += valor_rateio

            if conta_key and conta_key not in totalizador_contas:
                totalizador_contas[conta_key] = Decimal(0.00)

            if conta_key:
                totalizador_contas[conta_key] += Decimal(rateio['valor_rateio'])

        return sumarizacao_conta_acao_aplicacao, totalizador_contas

    gastos_por_conta_acao_aplicacao, gastos_por_conta = sumariza_rateios_por_conta_acao_aplicacao(rateios)

    saldos_insuficientes = []

    for conta_associacao_uuid, gasto_conta_associacao in gastos_por_conta.items():
        conta_associacao = ContaAssociacao.by_uuid(conta_associacao_uuid)
        saldos_conta = info_conta_associacao_no_periodo(conta_associacao, periodo, exclude_despesa=exclude_despesa)

        saldo_conta = saldos_conta['saldo_atual_custeio'] + saldos_conta['saldo_atual_capital'] + saldos_conta[
            'saldo_atual_livre']

        logger.info(f"Saldo calculado: {saldo_conta}  Conta:{conta_associacao}")

        if round(saldo_conta, 2) < round(gasto_conta_associacao, 2):
            saldo_insuficiente = {
                'conta': conta_associacao.tipo_conta.nome,
                'saldo_disponivel': saldo_conta,
                'total_rateios': gasto_conta_associacao
            }
            saldos_insuficientes.append(saldo_insuficiente)

    if saldos_insuficientes:
        return {
            'tipo_saldo': 'CONTA',
            'saldos_insuficientes': saldos_insuficientes
        }

    for uuid_conta, gasto_por_conta_acao_aplicacao in gastos_por_conta_acao_aplicacao.items():
        for acao in gasto_por_conta_acao_aplicacao:

            try:
                acao_associacao = AcaoAssociacao.by_uuid(acao)
            except AcaoAssociacao.DoesNotExist:
                return {
                    'situacao_do_saldo': 'impossivel_determinar',
                    'mensagem': 'Sem informar a ação da associação não há como determinar o saldo disponível.',
                    'saldos_insuficientes': [],
                    'aceitar_lancamento': True
                }

            try:
                conta = ContaAssociacao.by_uuid(uuid_conta)
            except ContaAssociacao.DoesNotExist:
                return {
                    'situacao_do_saldo': 'impossivel_determinar',
                    'mensagem': 'Sem informar a conta da associação não há como determinar o saldo disponível.',
                    'saldos_insuficientes': [],
                    'aceitar_lancamento': True
                }

            saldos_acao = info_acao_associacao_no_periodo(
                acao_associacao, periodo, conta=conta, exclude_despesa=exclude_despesa)

            saldo_livre_acao = saldos_acao['saldo_atual_livre']

            for aplicacao, saldo_atual_key in (('CUSTEIO', 'saldo_atual_custeio'), ('CAPITAL', 'saldo_atual_capital')):
                if not gasto_por_conta_acao_aplicacao[acao][aplicacao]:
                    continue

                saldo_atual_aplicacao = saldos_acao[saldo_atual_key]
                gasto_da_despesa_na_acao_aplicacao = round(gasto_por_conta_acao_aplicacao[acao][aplicacao], 2)

                if round(saldo_atual_aplicacao + saldo_livre_acao, 2) < gasto_da_despesa_na_acao_aplicacao:
                    saldo_insuficiente = {
                        'conta': conta,
                        'acao': acao_associacao.acao.nome,
                        'conta': conta_associacao.tipo_conta.nome,
                        'aplicacao': aplicacao,
                        'saldo_disponivel': saldo_atual_aplicacao + saldo_livre_acao,
                        'total_rateios': gasto_por_conta_acao_aplicacao[acao][aplicacao]
                    }

                    saldos_insuficientes.append(saldo_insuficiente)
                    saldo_livre_acao = 0
                elif round(saldo_atual_aplicacao, 2) < gasto_da_despesa_na_acao_aplicacao:
                    sobra_livre_acao = round(saldo_atual_aplicacao + saldo_livre_acao, 2) - \
                        gasto_da_despesa_na_acao_aplicacao
                    if (sobra_livre_acao < 0):
                        saldo_livre_acao = 0
                    else:
                        saldo_livre_acao = sobra_livre_acao
    return {
        'tipo_saldo': 'ACAO',
        'saldos_insuficientes': saldos_insuficientes
    }


def valida_rateios_quanto_aos_saldos(rateios, associacao, data_documento=None, exclude_despesa=None, recurso=None):
    logger.info(f"Valida saldo para rateios. Data documento:{data_documento}")

    if not data_documento:
        """
        Caso não tenha sido informada a data da transação, não é possível determinar o saldo.
        """
        return {
            'situacao_do_saldo': 'impossível_determinar',
            'mensagem': 'Sem informar a data da despesa não há como determinar o saldo disponível.',
            'saldos_insuficientes': [],
            'aceitar_lancamento': True
        }

    if associacao.periodo_inicial and data_documento <= associacao.periodo_inicial.data_fim_realizacao_despesas:
        """
        Caso o lançamento seja anterior ao período de implantação da Associação, ele deve ser tratado como uma
        implantação de lançamento não demonstrado (não conciliado).
        """
        return {
            'situacao_do_saldo': 'lancamento_anterior_implantacao',
            'mensagem': 'Lançamento com data anterior ao período inicial da associação.',
            'saldos_insuficientes': [],
            'aceitar_lancamento': True
        }

    """
    Verifica se os rateios informados causarão algum saldo negativo.
    """
    if recurso:
        periodo_despesa = Periodo.da_data_por_recurso(data_documento, recurso)
    else:
        periodo_despesa = Periodo.da_data(data_documento)

    logger.info(f"Período da despesa validada: {periodo_despesa}")

    saldos_insuficientes = saldos_insuficientes_para_rateios(
        rateios=rateios,
        periodo=periodo_despesa,
        exclude_despesa=exclude_despesa
    )

    if 'situacao_do_saldo' in saldos_insuficientes and saldos_insuficientes['situacao_do_saldo'] == 'impossivel_determinar':
        logger.info("Impossível determinar saldo nas contas e ações.")
        """
        Caso não sejam seja possivel determinar saldo.
        """
        return {
            'situacao_do_saldo': 'impossivel_determinar',
            'mensagem': saldos_insuficientes['mensagem'],
            'saldos_insuficientes': [],
            'aceitar_lancamento': True
        }

    if not saldos_insuficientes['saldos_insuficientes']:
        logger.info("Saldos suficientes nas contas e ações.")
        """
        Caso não sejam encontrados saldos insuficientes.
        """
        return {
            'situacao_do_saldo': 'saldo_suficiente',
            'mensagem': 'Há saldo disponível para cobertura da despesa.',
            'saldos_insuficientes': [],
            'aceitar_lancamento': True
        }

    if saldos_insuficientes['tipo_saldo'] == 'CONTA':
        logger.info("Saldos insuficientes em contas.")
        result = {
            'situacao_do_saldo': 'saldo_conta_insuficiente',
            'mensagem': 'Não há saldo disponível em alguma das contas da despesa.',
            'saldos_insuficientes': saldos_insuficientes['saldos_insuficientes'],
            'aceitar_lancamento': Parametros.get().permite_saldo_conta_negativo
        }
    else:
        logger.info("Saldos insuficientes em Ações.")
        result = {
            'situacao_do_saldo': 'saldo_insuficiente',
            'mensagem': 'Não há saldo disponível em alguma das ações da despesa.',
            'saldos_insuficientes': saldos_insuficientes['saldos_insuficientes'],
            'aceitar_lancamento': Parametros.get().permite_saldo_acoes_negativo
        }

    return result


def info_acao_associacao_no_periodo(
    acao_associacao,
    periodo,
    exclude_despesa=None,
    conta=None,
    apenas_transacoes_do_periodo=False,
    recurso=None
):
    def resultado_vazio():
        return {
            'saldo_anterior_custeio': 0,
            'receitas_no_periodo_custeio': 0,
            'receitas_devolucao_no_periodo_custeio': 0,
            'repasses_no_periodo_custeio': 0,
            'despesas_no_periodo_custeio': 0,
            'saldo_atual_custeio': 0,
            'receitas_nao_conciliadas_custeio': 0,
            'despesas_nao_conciliadas_custeio': 0,
            'despesas_conciliadas_custeio': 0,
            'saldo_bancario_custeio': 0,

            'saldo_anterior_capital': 0,
            'receitas_no_periodo_capital': 0,
            'receitas_devolucao_no_periodo_capital': 0,
            'repasses_no_periodo_capital': 0,
            'despesas_no_periodo_capital': 0,
            'saldo_atual_capital': 0,
            'receitas_nao_conciliadas_capital': 0,
            'despesas_nao_conciliadas_capital': 0,
            'despesas_conciliadas_capital': 0,
            'saldo_bancario_capital': 0,

            'saldo_anterior_livre': 0,
            'receitas_no_periodo_livre': 0,
            'receitas_devolucao_no_periodo_livre': 0,
            'repasses_no_periodo_livre': 0,
            'saldo_atual_livre': 0,
            'receitas_nao_conciliadas_livre': 0,
            'saldo_bancario_livre': 0,

        }

    def fechamento_sumarizado_por_acao(fechamentos_periodo, conta=None, considera_exclude_despesa=False):
        """
        `considera_exclude_despesa` só deve ser True quando o saldo é obtido
        exclusivamente do fechamento, sem recálculo de receitas ou despesas.
        Esse parâmetro é utilizado apenas no cenário de edição de despesa.
        """

        info = resultado_vazio()
        logger.debug(f'Buscando fechamentos da conta {conta}...')
        for fechamento_periodo in fechamentos_periodo:

            if conta and fechamento_periodo.conta_associacao != conta:
                logger.debug(
                    f'IGNORADO fechamento Período:{fechamento_periodo.periodo} Ação:{fechamento_periodo.acao_associacao} Conta:{fechamento_periodo.conta_associacao}')
                continue

            logger.debug(
                f'Somando fechamento Período:{fechamento_periodo.periodo} Ação:{fechamento_periodo.acao_associacao} Conta:{fechamento_periodo.conta_associacao}')

            info['saldo_anterior_custeio'] += fechamento_periodo.saldo_anterior_custeio
            info['receitas_no_periodo_custeio'] += fechamento_periodo.total_receitas_custeio
            info['receitas_devolucao_no_periodo_custeio'] += fechamento_periodo.total_receitas_devolucao_custeio
            info['repasses_no_periodo_custeio'] += fechamento_periodo.total_repasses_custeio
            info['despesas_no_periodo_custeio'] += fechamento_periodo.total_despesas_custeio
            info['saldo_atual_custeio'] += fechamento_periodo.saldo_reprogramado_custeio
            info['receitas_nao_conciliadas_custeio'] += fechamento_periodo.total_receitas_nao_conciliadas_custeio
            info['despesas_nao_conciliadas_custeio'] += fechamento_periodo.total_despesas_nao_conciliadas_custeio
            info['despesas_conciliadas_custeio'] += (fechamento_periodo.total_despesas_custeio -
                                                     fechamento_periodo.total_despesas_nao_conciliadas_custeio)
            info['saldo_bancario_custeio'] += (
                fechamento_periodo.saldo_reprogramado_custeio +
                fechamento_periodo.total_despesas_nao_conciliadas_custeio
            )

            info['saldo_anterior_capital'] += fechamento_periodo.saldo_anterior_capital
            info['receitas_no_periodo_capital'] += fechamento_periodo.total_receitas_capital
            info['receitas_devolucao_no_periodo_capital'] += fechamento_periodo.total_receitas_devolucao_capital
            info['repasses_no_periodo_capital'] += fechamento_periodo.total_repasses_capital
            info['despesas_no_periodo_capital'] += fechamento_periodo.total_despesas_capital
            info['saldo_atual_capital'] += fechamento_periodo.saldo_reprogramado_capital
            info['receitas_nao_conciliadas_capital'] += fechamento_periodo.total_receitas_nao_conciliadas_capital
            info['despesas_nao_conciliadas_capital'] += fechamento_periodo.total_despesas_nao_conciliadas_capital
            info['despesas_conciliadas_capital'] += (fechamento_periodo.total_despesas_capital -
                                                     fechamento_periodo.total_despesas_nao_conciliadas_capital)
            info['saldo_bancario_capital'] += (
                fechamento_periodo.saldo_reprogramado_capital +
                fechamento_periodo.total_despesas_nao_conciliadas_capital
            )

            info['saldo_anterior_livre'] += fechamento_periodo.saldo_anterior_livre
            info['receitas_no_periodo_livre'] += fechamento_periodo.total_receitas_livre
            info['receitas_devolucao_no_periodo_livre'] += fechamento_periodo.total_receitas_devolucao_livre
            info['repasses_no_periodo_livre'] += fechamento_periodo.total_repasses_livre
            info['saldo_atual_livre'] += fechamento_periodo.saldo_reprogramado_livre
            info['receitas_nao_conciliadas_livre'] += fechamento_periodo.total_receitas_nao_conciliadas_livre
            info['saldo_bancario_livre'] += fechamento_periodo.saldo_reprogramado_livre

            if exclude_despesa and considera_exclude_despesa:
                despesa = Despesa.objects.get(uuid=exclude_despesa)
                rateios = despesa.rateios.filter(acao_associacao=fechamento_periodo.acao_associacao).filter(
                    conta_associacao=fechamento_periodo.conta_associacao)
                for rateio in rateios.all():
                    if rateio.aplicacao_recurso == APLICACAO_CAPITAL:
                        info['despesas_no_periodo_capital'] -= rateio.valor_rateio
                        info['saldo_atual_capital'] += rateio.valor_rateio
                    elif rateio.aplicacao_recurso == APLICACAO_CUSTEIO:
                        info['despesas_no_periodo_custeio'] -= rateio.valor_rateio
                        info['saldo_atual_custeio'] += rateio.valor_rateio

        return info

    def sumariza_receitas_acao_entre_periodos(periodo_inicial, periodo_final, acao_associacao, info, conta=None):
        receitas = Receita.receitas_da_acao_associacao_entre_periodos(
            acao_associacao=acao_associacao,
            periodo_inicial=periodo_inicial,
            periodo_final=periodo_final
        )

        for receita in receitas:
            if conta and receita.conta_associacao != conta:
                continue

            if receita.categoria_receita == APLICACAO_CUSTEIO:
                info['receitas_no_periodo_custeio'] += receita.valor
                info[
                    'receitas_devolucao_no_periodo_custeio'] += receita.valor if receita.tipo_receita.e_devolucao else 0
                info['saldo_atual_custeio'] += receita.valor
                info['repasses_no_periodo_custeio'] += receita.valor if receita.tipo_receita.e_repasse else 0
                info['receitas_nao_conciliadas_custeio'] += receita.valor if not receita.conferido else 0

            elif receita.categoria_receita == APLICACAO_CAPITAL:
                info['receitas_no_periodo_capital'] += receita.valor
                info[
                    'receitas_devolucao_no_periodo_capital'] += receita.valor if receita.tipo_receita.e_devolucao else 0
                info['saldo_atual_capital'] += receita.valor
                info['repasses_no_periodo_capital'] += receita.valor if receita.tipo_receita.e_repasse else 0
                info['receitas_nao_conciliadas_capital'] += receita.valor if not receita.conferido else 0
            else:
                info['receitas_no_periodo_livre'] += receita.valor
                info['receitas_devolucao_no_periodo_livre'] += receita.valor if receita.tipo_receita.e_devolucao else 0
                info['saldo_atual_livre'] += receita.valor
                info['repasses_no_periodo_livre'] += receita.valor if receita.tipo_receita.e_repasse else 0
                info['receitas_nao_conciliadas_livre'] += receita.valor if not receita.conferido else 0

        return info

    def sumariza_despesas_acao_entre_periodos(
        periodo_inicial,
        periodo_final,
        acao_associacao,
        info,
        exclude_despesa=exclude_despesa,
        conta=None,
        recurso=None,
    ):
        rateios = RateioDespesa.rateios_da_acao_entre_periodos(
            acao_associacao=acao_associacao,
            periodo_inicial=periodo_inicial,
            periodo_final=periodo_final,
            exclude_despesa=exclude_despesa,
            recurso=recurso,
        )

        for rateio in rateios:
            if conta and rateio.conta_associacao != conta:
                continue

            if rateio.aplicacao_recurso == APLICACAO_CUSTEIO:
                info['despesas_no_periodo_custeio'] += rateio.valor_rateio
                info['saldo_atual_custeio'] -= rateio.valor_rateio

                if (not rateio.conferido) or (rateio.periodo_conciliacao and rateio.periodo_conciliacao.referencia > periodo_final.referencia):
                    info['despesas_nao_conciliadas_custeio'] += rateio.valor_rateio
                else:
                    info['despesas_conciliadas_custeio'] += rateio.valor_rateio

            else:
                info['despesas_no_periodo_capital'] += rateio.valor_rateio
                info['saldo_atual_capital'] -= rateio.valor_rateio

                if (not rateio.conferido) or (rateio.periodo_conciliacao and rateio.periodo_conciliacao.referencia > periodo_final.referencia):
                    info['despesas_nao_conciliadas_capital'] += rateio.valor_rateio
                else:
                    info['despesas_conciliadas_capital'] += rateio.valor_rateio

        return info

    def periodo_aberto_sumarizado_por_acao(
        periodo,
        acao_associacao,
        conta=None,
        apenas_transacoes_do_periodo=False,
        recurso=None,
    ):
        info = resultado_vazio()

        if not periodo:
            return info

        fechamentos_periodo_anterior = FechamentoPeriodo.fechamentos_da_acao_imediatamente_antes_do_periodo(
            acao_associacao=acao_associacao,
            periodo=periodo,
            conta_associacao=conta,
        )

        if fechamentos_periodo_anterior:
            sumario_periodo_anterior = fechamento_sumarizado_por_acao(
                fechamentos_periodo_anterior, conta=conta, considera_exclude_despesa=False)
            info['saldo_anterior_capital'] = sumario_periodo_anterior['saldo_atual_capital']
            info['saldo_atual_capital'] = info['saldo_anterior_capital']
            info['saldo_anterior_custeio'] = sumario_periodo_anterior['saldo_atual_custeio']
            info['saldo_atual_custeio'] = info['saldo_anterior_custeio']
            info['saldo_anterior_livre'] = sumario_periodo_anterior['saldo_atual_livre']
            info['saldo_atual_livre'] = info['saldo_anterior_livre']

        # Determina a partir de qual período considera o saldo
        if fechamentos_periodo_anterior:
            periodo_do_saldo = fechamentos_periodo_anterior.first().periodo
        elif periodo.periodo_anterior:
            periodo_do_saldo = periodo.periodo_anterior
        else:
            periodo_do_saldo = periodo

        if (not apenas_transacoes_do_periodo) and periodo_do_saldo and periodo_do_saldo.proximo_periodo:
            periodo_inicial_transacoes = periodo_do_saldo.proximo_periodo
        else:
            periodo_inicial_transacoes = periodo

        info = sumariza_receitas_acao_entre_periodos(
            periodo_inicial=periodo_inicial_transacoes,
            periodo_final=periodo,
            acao_associacao=acao_associacao,
            info=info,
            conta=conta,
        )

        info = sumariza_despesas_acao_entre_periodos(
            periodo_inicial=periodo_inicial_transacoes,
            periodo_final=periodo,
            acao_associacao=acao_associacao,
            info=info,
            conta=conta,
            recurso=recurso,
        )

        if info['saldo_atual_custeio'] < 0:
            logger.debug(f'Usado saldo de livre aplicação para cobertura de custeio')
            info['saldo_atual_livre'] += info['saldo_atual_custeio']
            info['saldo_atual_custeio'] = 0

        if info['saldo_atual_capital'] < 0:
            logger.debug(f'Usado saldo de livre aplicação para cobertura de capital')
            info['saldo_atual_livre'] += info['saldo_atual_capital']
            info['saldo_atual_capital'] = 0

        info['saldo_bancario_capital'] += (
            info['saldo_atual_capital'] +
            info['despesas_nao_conciliadas_capital']
        )

        info['saldo_bancario_custeio'] += (
            info['saldo_atual_custeio'] +
            info['despesas_nao_conciliadas_custeio']
        )

        info['saldo_bancario_livre'] += (
            info['saldo_atual_livre']
        )

        return info

    fechamentos_periodo = FechamentoPeriodo.fechamentos_da_acao_no_periodo(acao_associacao=acao_associacao,
                                                                           periodo=periodo)
    if fechamentos_periodo:
        logger.info(f'Get fechamentos sumarizados por ação. Conta:{conta}')
        return fechamento_sumarizado_por_acao(fechamentos_periodo, conta=conta, considera_exclude_despesa=True)
    else:
        logger.info(f'Get periodo aberto sumarizado por ação. Período:{periodo} Ação:{acao_associacao} Conta:{conta}')
        return periodo_aberto_sumarizado_por_acao(periodo,
                                                  acao_associacao,
                                                  conta=conta,
                                                  apenas_transacoes_do_periodo=apenas_transacoes_do_periodo,
                                                  recurso=recurso,
                                                  )


def info_repasses_pendentes_acao_associacao_no_periodo(acao_associacao, periodo, conta=None):
    repasses_pendentes = Repasse.repasses_pendentes_da_acao_associacao_no_periodo(acao_associacao=acao_associacao,
                                                                                  periodo=periodo,
                                                                                  conta_associacao=conta)

    total_repasses = {
        'CAPITAL': 0,
        'CUSTEIO': 0,
        'LIVRE': 0,
    }
    for repasse in repasses_pendentes:
        total_repasses['CAPITAL'] += repasse.valor_capital if not repasse.realizado_capital else 0
        total_repasses['CUSTEIO'] += repasse.valor_custeio if not repasse.realizado_custeio else 0
        total_repasses['LIVRE'] += repasse.valor_livre if not repasse.realizado_livre else 0

    return total_repasses


def info_acoes_associacao_no_periodo(associacao_uuid, periodo, conta=None, apenas_transacoes_do_periodo=False):
    acoes_associacao = Associacao.acoes_da_associacao(associacao_uuid=associacao_uuid)
   
    # filtrar ações da associação por recurso
    acoes_associacao = AcaoAssociacao.filter_by_recurso(acoes_associacao, periodo.recurso)
   
    result = []
    for acao_associacao in acoes_associacao:
        logger.debug(f'Get info ação no período. Ação:{acao_associacao} Período:{periodo} Conta:{conta}')
        info_acao = info_acao_associacao_no_periodo(
            acao_associacao=acao_associacao,
            periodo=periodo,
            conta=conta,
            apenas_transacoes_do_periodo=apenas_transacoes_do_periodo
        )
        especificacoes_despesas = especificacoes_despesas_acao_associacao_no_periodo(acao_associacao=acao_associacao,
                                                                                     periodo=periodo, conta=conta)

        info_repasses_pendentes = info_repasses_pendentes_acao_associacao_no_periodo(acao_associacao=acao_associacao,
                                                                                     periodo=periodo, conta=conta)

        despesas_nao_conciliadas_anteriores_capital = RateioDespesa.rateios_da_acao_associacao_em_periodo_anteriores(
            acao_associacao=acao_associacao, conta_associacao=conta, periodo=periodo, conferido=False,
            aplicacao_recurso=APLICACAO_CAPITAL).aggregate(valor=Sum('valor_rateio'))
        despesas_nao_conciliadas_anteriores_capital = despesas_nao_conciliadas_anteriores_capital['valor'] or 0

        despesas_nao_conciliadas_anteriores_custeio = RateioDespesa.rateios_da_acao_associacao_em_periodo_anteriores(
            acao_associacao=acao_associacao, conta_associacao=conta, periodo=periodo, conferido=False,
            aplicacao_recurso=APLICACAO_CUSTEIO).aggregate(valor=Sum('valor_rateio'))
        despesas_nao_conciliadas_anteriores_custeio = despesas_nao_conciliadas_anteriores_custeio['valor'] or 0

        info = {
            'acao_associacao_uuid': f'{acao_associacao.uuid}',
            'acao_associacao_nome': acao_associacao.acao.nome,

            'saldo_reprogramado': info_acao['saldo_anterior_custeio'] +
            info_acao['saldo_anterior_capital'] +
            info_acao['saldo_anterior_livre'],
            'saldo_reprogramado_capital': info_acao['saldo_anterior_capital'],
            'saldo_reprogramado_custeio': info_acao['saldo_anterior_custeio'],
            'saldo_reprogramado_livre': info_acao['saldo_anterior_livre'],

            'receitas_no_periodo': info_acao['receitas_no_periodo_custeio'] +
            info_acao['receitas_no_periodo_capital'] +
            info_acao['receitas_no_periodo_livre'],

            'receitas_devolucao_no_periodo': info_acao['receitas_devolucao_no_periodo_custeio'] +
            info_acao['receitas_devolucao_no_periodo_capital'] +
            info_acao['receitas_devolucao_no_periodo_livre'],

            'receitas_devolucao_no_periodo_custeio': info_acao['receitas_devolucao_no_periodo_custeio'],
            'receitas_devolucao_no_periodo_capital': info_acao['receitas_devolucao_no_periodo_capital'],
            'receitas_devolucao_no_periodo_livre': info_acao['receitas_devolucao_no_periodo_livre'],

            'repasses_no_periodo': info_acao['repasses_no_periodo_custeio'] +
            info_acao['repasses_no_periodo_capital'] +
            info_acao['repasses_no_periodo_livre'],
            'repasses_no_periodo_capital': info_acao['repasses_no_periodo_capital'],
            'repasses_no_periodo_custeio': info_acao['repasses_no_periodo_custeio'],
            'repasses_no_periodo_livre': info_acao['repasses_no_periodo_livre'],

            'outras_receitas_no_periodo': info_acao['receitas_no_periodo_custeio'] +
            info_acao['receitas_no_periodo_capital'] +
            info_acao['receitas_no_periodo_livre'] -
            info_acao['repasses_no_periodo_custeio'] -
            info_acao['repasses_no_periodo_capital'] -
            info_acao['repasses_no_periodo_livre'],

            'outras_receitas_no_periodo_capital': info_acao['receitas_no_periodo_capital'] -
            info_acao['repasses_no_periodo_capital'],

            'outras_receitas_no_periodo_custeio': info_acao['receitas_no_periodo_custeio'] -
            info_acao['repasses_no_periodo_custeio'],

            'outras_receitas_no_periodo_livre': info_acao['receitas_no_periodo_livre'] -
            info_acao['repasses_no_periodo_livre'],

            'despesas_no_periodo': info_acao['despesas_no_periodo_custeio'] +
            info_acao['despesas_no_periodo_capital'],
            'despesas_no_periodo_capital': info_acao['despesas_no_periodo_capital'],
            'despesas_no_periodo_custeio': info_acao['despesas_no_periodo_custeio'],

            'despesas_nao_conciliadas': info_acao['despesas_nao_conciliadas_custeio'] +
            info_acao['despesas_nao_conciliadas_capital'],
            'despesas_nao_conciliadas_capital': info_acao['despesas_nao_conciliadas_capital'],
            'despesas_nao_conciliadas_custeio': info_acao['despesas_nao_conciliadas_custeio'],

            'despesas_nao_conciliadas_anteriores_capital': despesas_nao_conciliadas_anteriores_capital,

            'despesas_nao_conciliadas_anteriores_custeio': despesas_nao_conciliadas_anteriores_custeio,

            'despesas_nao_conciliadas_anteriores': despesas_nao_conciliadas_anteriores_capital + despesas_nao_conciliadas_anteriores_custeio,

            'despesas_conciliadas': info_acao['despesas_conciliadas_custeio'] +
            info_acao['despesas_conciliadas_capital'],
            'despesas_conciliadas_capital': info_acao['despesas_conciliadas_capital'],
            'despesas_conciliadas_custeio': info_acao['despesas_conciliadas_custeio'],

            'receitas_nao_conciliadas': info_acao['receitas_nao_conciliadas_custeio'] +
            info_acao['receitas_nao_conciliadas_capital'] +
            info_acao['receitas_nao_conciliadas_livre'],
            'receitas_nao_conciliadas_capital': info_acao['receitas_nao_conciliadas_capital'],
            'receitas_nao_conciliadas_custeio': info_acao['receitas_nao_conciliadas_custeio'],
            'receitas_nao_conciliadas_livre': info_acao['receitas_nao_conciliadas_livre'],

            'saldo_atual_custeio': info_acao['saldo_atual_custeio'],
            'saldo_atual_capital': info_acao['saldo_atual_capital'],
            'saldo_atual_livre': info_acao['saldo_atual_livre'],
            'saldo_atual_total': info_acao['saldo_atual_custeio'] +
            info_acao['saldo_atual_capital'] +
            info_acao['saldo_atual_livre'],

            'especificacoes_despesas_capital': especificacoes_despesas['CAPITAL'],
            'especificacoes_despesas_custeio': especificacoes_despesas['CUSTEIO'],

            'repasses_nao_realizados_capital': info_repasses_pendentes['CAPITAL'],
            'repasses_nao_realizados_custeio': info_repasses_pendentes['CUSTEIO'],
            'repasses_nao_realizados_livre': info_repasses_pendentes['LIVRE'],

            # Saldo Atual + Despesas Não demonstradas no período + Despesas não demonstradas períodos anteriores
            'saldo_bancario_custeio': info_acao['saldo_bancario_custeio'] + despesas_nao_conciliadas_anteriores_custeio,
            'saldo_bancario_capital': info_acao['saldo_bancario_capital'] + despesas_nao_conciliadas_anteriores_capital,
            'saldo_bancario_livre': info_acao['saldo_bancario_livre'],
            'saldo_bancario_total': info_acao['saldo_bancario_custeio'] +
            info_acao['saldo_bancario_capital'] +
            info_acao['saldo_bancario_livre'] +
            despesas_nao_conciliadas_anteriores_custeio +
            despesas_nao_conciliadas_anteriores_capital,


        }
        result.append(info)

    return result


def info_conta_associacao_no_periodo(conta_associacao, periodo, exclude_despesa=None):
    from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL, APLICACAO_CUSTEIO

    def resultado_vazio():
        return {
            'saldo_anterior_custeio': 0,
            'receitas_no_periodo_custeio': 0,
            'repasses_no_periodo_custeio': 0,
            'despesas_no_periodo_custeio': 0,
            'saldo_atual_custeio': 0,

            'saldo_anterior_capital': 0,
            'receitas_no_periodo_capital': 0,
            'repasses_no_periodo_capital': 0,
            'despesas_no_periodo_capital': 0,
            'saldo_atual_capital': 0,

            'saldo_anterior_livre': 0,
            'receitas_no_periodo_livre': 0,
            'repasses_no_periodo_livre': 0,
            'saldo_atual_livre': 0,
        }

    def fechamento_sumarizado_por_conta(fechamentos_periodo, considera_exclude_despesa=False):
        """
        `considera_exclude_despesa` só deve ser True quando o saldo é obtido
        exclusivamente do fechamento, sem recálculo de receitas ou despesas.
        Esse parâmetro é utilizado apenas no cenário de edição de despesa.
        """
        info = resultado_vazio()
        for fechamento_periodo in fechamentos_periodo:
            info['saldo_anterior_custeio'] += fechamento_periodo.saldo_anterior_custeio
            info['receitas_no_periodo_custeio'] += fechamento_periodo.total_receitas_custeio
            info['repasses_no_periodo_custeio'] += fechamento_periodo.total_repasses_custeio
            info['despesas_no_periodo_custeio'] += fechamento_periodo.total_despesas_custeio
            info['saldo_atual_custeio'] += fechamento_periodo.saldo_reprogramado_custeio

            info['saldo_anterior_capital'] += fechamento_periodo.saldo_anterior_capital
            info['receitas_no_periodo_capital'] += fechamento_periodo.total_receitas_capital
            info['repasses_no_periodo_capital'] += fechamento_periodo.total_repasses_capital
            info['despesas_no_periodo_capital'] += fechamento_periodo.total_despesas_capital
            info['saldo_atual_capital'] += fechamento_periodo.saldo_reprogramado_capital

            info['saldo_anterior_livre'] += fechamento_periodo.saldo_anterior_livre
            info['receitas_no_periodo_livre'] += fechamento_periodo.total_receitas_livre
            info['repasses_no_periodo_livre'] += fechamento_periodo.total_repasses_livre
            info['saldo_atual_livre'] += fechamento_periodo.saldo_reprogramado_livre

        if exclude_despesa and considera_exclude_despesa:
            despesa = Despesa.objects.get(uuid=exclude_despesa)
            for rateio in despesa.rateios.all():
                if rateio.aplicacao_recurso == APLICACAO_CAPITAL:
                    info['despesas_no_periodo_capital'] -= rateio.valor_rateio
                    info['saldo_atual_capital'] += rateio.valor_rateio
                elif rateio.aplicacao_recurso == APLICACAO_CUSTEIO:
                    info['despesas_no_periodo_custeio'] -= rateio.valor_rateio
                    info['saldo_atual_custeio'] += rateio.valor_rateio

        return info

    def sumariza_receitas_conta_entre_periodos(periodo_inicial, periodo_final, conta_associacao, info):
        logger.info(
            f"Sumarizando receitas entre os períodos {periodo_inicial} e {periodo_final}. Conta:{conta_associacao}")
        receitas = Receita.receitas_da_conta_associacao_entre_periodos(
            conta_associacao=conta_associacao,
            periodo_inicial=periodo_inicial,
            periodo_final=periodo_final,
        )

        for receita in receitas:
            logger.info(f"Somando receita {receita.id} {receita.data} {receita.valor}")
            if receita.categoria_receita == APLICACAO_CUSTEIO:
                info['receitas_no_periodo_custeio'] += receita.valor
                info['saldo_atual_custeio'] += receita.valor
                info['repasses_no_periodo_custeio'] += receita.valor if receita.tipo_receita.e_repasse else 0

            elif receita.categoria_receita == APLICACAO_CAPITAL:
                info['receitas_no_periodo_capital'] += receita.valor
                info['saldo_atual_capital'] += receita.valor
                info['repasses_no_periodo_capital'] += receita.valor if receita.tipo_receita.e_repasse else 0

            else:
                info['receitas_no_periodo_livre'] += receita.valor
                info['saldo_atual_livre'] += receita.valor
                info['repasses_no_periodo_livre'] += receita.valor if receita.tipo_receita.e_repasse else 0

        return info

    def sumariza_despesas_conta_entre_periodos(
        periodo_inicial,
        periodo_final,
        conta_associacao,
        info,
        exclude_despesa=exclude_despesa
    ):
        logger.info(f"Sumarizando despesas entre os períodos {periodo_inicial} e {periodo_final}")

        rateios = RateioDespesa.rateios_da_conta_entre_periodos(
            conta_associacao=conta_associacao,
            periodo_inicial=periodo_inicial,
            periodo_final=periodo_final,
            exclude_despesa=exclude_despesa
        )

        for rateio in rateios:
            logger.info(f"Subtraindo rateio {rateio.id} {rateio.despesa.data_transacao} {rateio.valor_rateio}")
            if rateio.aplicacao_recurso == APLICACAO_CUSTEIO:
                info['despesas_no_periodo_custeio'] += rateio.valor_rateio
                info['saldo_atual_custeio'] -= rateio.valor_rateio
            else:
                info['despesas_no_periodo_capital'] += rateio.valor_rateio
                info['saldo_atual_capital'] -= rateio.valor_rateio

        return info

    def periodo_aberto_sumarizado_por_conta(periodo, conta_associacao):
        logger.info(f"O período está aberto. Sumarizando por conta. Período:{periodo} Conta:{conta_associacao}")
        info = resultado_vazio()

        if not periodo or not periodo.periodo_anterior:
            logger.info("Periodo indefinido ou sem período anterior. Retornando vazio.")
            return info

        fechamentos_periodo_anterior = FechamentoPeriodo.fechamentos_da_conta_imediatamente_antes_do_periodo(
            conta_associacao=conta_associacao,
            periodo=periodo)

        if fechamentos_periodo_anterior:
            logger.info(
                f'Encontrados fechamentos de períodos anteriores ao período {periodo} para a conta {conta_associacao}')
            sumario_periodo_anterior = fechamento_sumarizado_por_conta(
                fechamentos_periodo_anterior, considera_exclude_despesa=False)

            info['saldo_anterior_capital'] = sumario_periodo_anterior['saldo_atual_capital']
            info['saldo_atual_capital'] = info['saldo_anterior_capital']

            info['saldo_anterior_custeio'] = sumario_periodo_anterior['saldo_atual_custeio']
            info['saldo_atual_custeio'] = info['saldo_anterior_custeio']

            info['saldo_anterior_livre'] = sumario_periodo_anterior['saldo_atual_livre']
            info['saldo_atual_livre'] = info['saldo_anterior_livre']

        # Determina a partir de qual período considera o saldo
        if fechamentos_periodo_anterior:
            periodo_do_saldo = fechamentos_periodo_anterior.first().periodo
        elif periodo.periodo_anterior:
            periodo_do_saldo = periodo.periodo_anterior
        else:
            periodo_do_saldo = periodo

        if not periodo_do_saldo.proximo_periodo:
            logger.info("Periodo indefinido ou sem periodo inicial. Retornando vazio")
            info = resultado_vazio()
            return info

        logger.info(f'Usando saldos do período {periodo_do_saldo}')
        logger.info(
            f"Saldo capital:{info['saldo_atual_capital']} custeio:{info['saldo_atual_custeio']} livre:{info['saldo_atual_livre']}")
        info = sumariza_receitas_conta_entre_periodos(
            periodo_inicial=periodo_do_saldo.proximo_periodo,
            periodo_final=periodo,
            conta_associacao=conta_associacao,
            info=info
        )
        info = sumariza_despesas_conta_entre_periodos(
            periodo_inicial=periodo_do_saldo.proximo_periodo,
            periodo_final=periodo,
            conta_associacao=conta_associacao,
            info=info
        )

        if info['saldo_atual_custeio'] < 0:
            info['saldo_atual_livre'] += info['saldo_atual_custeio']
            info['saldo_atual_custeio'] = 0

        if info['saldo_atual_capital'] < 0:
            info['saldo_atual_livre'] += info['saldo_atual_capital']
            info['saldo_atual_capital'] = 0

        return info

    fechamentos_periodo = FechamentoPeriodo.fechamentos_da_conta_no_periodo(conta_associacao=conta_associacao,
                                                                            periodo=periodo)
    if fechamentos_periodo:
        logger.info(f'Encontrato fechamentos no período {periodo} e conta {conta_associacao}. Usando fechamento.')
        return fechamento_sumarizado_por_conta(fechamentos_periodo, considera_exclude_despesa=True)
    else:
        logger.info(f'Não encontrato fechamentos no período {periodo} e conta {conta_associacao}. Calculando saldo.')
        return periodo_aberto_sumarizado_por_conta(periodo, conta_associacao)


def info_painel_acoes_por_periodo_e_conta(associacao_uuid, periodo_uuid=None, conta_associacao_uuid=None):
    if periodo_uuid:
        try:
            periodo = Periodo.by_uuid(periodo_uuid)
        except:
            return {'erro': 'UUID do período inválido.'}
    else:
        periodo = Periodo.periodo_atual()

    prestacao_contas_status = status_prestacao_conta_associacao(periodo_uuid=periodo.uuid,
                                                                associacao_uuid=associacao_uuid)
    ultima_atualizacao = datetime.datetime.now()

    try:
        conta = ContaAssociacao.by_uuid(conta_associacao_uuid) if conta_associacao_uuid else None
    except:
        return {'erro': 'UUID da conta inválido.'}

    info_conta = {
        'conta_associacao_uuid': f'{conta.uuid}',
        'conta_associacao_nome': conta.tipo_conta.nome,

        'saldo_reprogramado': 0,
        'saldo_reprogramado_capital': 0,
        'saldo_reprogramado_custeio': 0,
        'saldo_reprogramado_livre': 0,

        'receitas_no_periodo': 0,

        'repasses_no_periodo': 0,
        'repasses_no_periodo_capital': 0,
        'repasses_no_periodo_custeio': 0,
        'repasses_no_periodo_livre': 0,

        'outras_receitas_no_periodo': 0,
        'outras_receitas_no_periodo_capital': 0,
        'outras_receitas_no_periodo_custeio': 0,
        'outras_receitas_no_periodo_livre': 0,

        'despesas_no_periodo': 0,
        'despesas_no_periodo_capital': 0,
        'despesas_no_periodo_custeio': 0,

        'saldo_atual_custeio': 0,
        'saldo_atual_capital': 0,
        'saldo_atual_livre': 0,
        'saldo_atual_total': 0
    } if conta else None

    info_acoes = info_acoes_associacao_no_periodo(associacao_uuid=associacao_uuid, periodo=periodo, conta=conta)

    info_acoes = [info for info in info_acoes if
                  info['saldo_reprogramado'] or info['receitas_no_periodo'] or info['despesas_no_periodo'] or info['despesas_nao_conciliadas_anteriores']]

    if info_conta:
        for acao in info_acoes:
            for key, value in acao.items():
                if key in info_conta:
                    info_conta[key] += value

    result = {
        'associacao': f'{associacao_uuid}',
        'periodo_referencia': periodo.referencia,
        'prestacao_contas_status': prestacao_contas_status,
        'data_inicio_realizacao_despesas': f'{periodo.data_inicio_realizacao_despesas if periodo else ""}',
        'data_fim_realizacao_despesas': f'{periodo.data_fim_realizacao_despesas if periodo else ""}',
        'data_prevista_repasse': f'{periodo.data_prevista_repasse if periodo else ""}',
        'ultima_atualizacao': f'{ultima_atualizacao}',
        'info_acoes': info_acoes,
        'info_conta': info_conta
    }

    return result

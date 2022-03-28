import logging

from datetime import datetime

from datetime import date

from django.db.models import Sum

from sme_ptrf_apps.core.choices import MembroEnum
from sme_ptrf_apps.core.models import (FechamentoPeriodo, MembroAssociacao, ObservacaoConciliacao)
from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.receitas.models import Receita
from sme_ptrf_apps.receitas.tipos_aplicacao_recurso_receitas import (APLICACAO_CAPITAL, APLICACAO_CUSTEIO,
                                                                     APLICACAO_LIVRE)

LOGGER = logging.getLogger(__name__)


def gerar_dados_demonstrativo_financeiro(usuario, acoes, periodo, conta_associacao, prestacao, observacao_conciliacao,
                                         previa=False):
    try:
        LOGGER.info("GERANDO DADOS DEMONSTRATIVO...")
        rateios_conferidos = RateioDespesa.rateios_da_conta_associacao_no_periodo(
            conta_associacao=conta_associacao, periodo=periodo, conferido=True).order_by('despesa__data_transacao')

        rateios_nao_conferidos = RateioDespesa.rateios_da_conta_associacao_no_periodo(conta_associacao=conta_associacao,
                                                                                      periodo=periodo,
                                                                                      conferido=False).order_by(
            'despesa__data_transacao')

        rateios_nao_conferidos_periodos_anteriores = RateioDespesa.rateios_da_conta_associacao_em_periodos_anteriores(
            conta_associacao=conta_associacao, periodo=periodo, conferido=False).order_by('despesa__data_transacao')

        receitas_demonstradas = Receita.receitas_da_conta_associacao_no_periodo(
            conta_associacao=conta_associacao, periodo=periodo, conferido=True)

        cabecalho = cria_cabecalho(periodo, conta_associacao, previa)
        identificacao_apm = cria_identificacao_apm(acoes)
        identificacao_conta = cria_identificacao_conta(conta_associacao, observacao_conciliacao)
        resumo_por_acao = cria_resumo_por_acao(acoes, conta_associacao, periodo)
        creditos_demonstrados = cria_creditos_demonstrados(receitas_demonstradas)
        despesas_demonstradas = cria_despesas(rateios_conferidos)
        despesas_nao_demonstradas = cria_despesas(rateios_nao_conferidos)
        despesas_anteriores_nao_demonstradas = cria_despesas(rateios_nao_conferidos_periodos_anteriores)
        observacoes = cria_observacoes(periodo, conta_associacao)
        justificativas = cria_justificativas(observacao_conciliacao)
        data_geracao_documento = cria_data_geracao_documento(usuario, previa)
        data_geracao = cria_data_geracao()

        """
            Mapeamento campos x pdf - Campos usados em cada um dos blocos do PDF:

            Bloco 1 - Identificação da Associação
                cabecalho
                identificacao_apm

            Bloco 2 - Identificação Bancária e Saldo
                identificacao_conta

            Bloco 3 - Resumo por Ação
                resumo_por_acao

            Bloco 4 - Créditos
                creditos_demonstrados

            Bloco 5 - Despesas Demonstradas
                despesas_demonstradas

            Bloco 6 - Despesas Não Demonstradas
                despesas_nao_demonstradas

            Bloco 7 - Despesas de períodos anteriores não demonstradas
                despesas_anteriores_nao_demonstradas

            Bloco 8 - Justificativas e informações adicionais
                justificativas

            Bloco 9 - Assinaturas
                data_geracao
        """
        dados_demonstrativo = {
            "cabecalho": cabecalho,
            "identificacao_apm": identificacao_apm,
            "identificacao_conta": identificacao_conta,
            "resumo_por_acao": resumo_por_acao,
            "creditos_demonstrados": creditos_demonstrados,
            "despesas_demonstradas": despesas_demonstradas,
            "despesas_nao_demonstradas": despesas_nao_demonstradas,
            "despesas_anteriores_nao_demonstradas": despesas_anteriores_nao_demonstradas,
            "observacoes_acoes": observacoes,
            "justificativas": justificativas,
            "data_geracao_documento": data_geracao_documento,
            "data_geracao": data_geracao
        }
    # except Exception as e:
    #    LOGGER.error("ERRO no DADOS DEMONSTRATIVO: %s", str(e))
    finally:
        LOGGER.info("DADOS DEMONSTRATIVO GERADO")

    return dados_demonstrativo


def cria_cabecalho(periodo, conta_associacao, previa):
    cabecalho = {
        "titulo": "Demonstrativo Financeiro - PRÉVIA" if previa else "Demonstrativo Financeiro - FINAL",
        "periodo": str(periodo),
        "periodo_referencia": periodo.referencia,
        "periodo_data_inicio": formata_data(periodo.data_inicio_realizacao_despesas),
        "periodo_data_fim": formata_data(periodo.data_fim_realizacao_despesas),
        "conta": conta_associacao.tipo_conta.nome
    }

    return cabecalho


def cria_identificacao_apm(acoes):
    acao_associacao = acoes[0]
    associacao = acao_associacao.associacao

    status_presidente_associacao = associacao.status_presidente
    cargo_substituto_presidente_ausente_name = associacao.cargo_substituto_presidente_ausente

    nome_associacao = associacao.nome
    cnpj_associacao = associacao.cnpj
    codigo_eol_associacao = associacao.unidade.codigo_eol or ""
    nome_dre_associacao = formata_nome_dre(associacao)
    tipo_unidade = associacao.unidade.tipo_unidade
    nome_unidade = associacao.unidade.nome
    _presidente_diretoria_executiva = ''

    if status_presidente_associacao == 'PRESENTE':
        _presidente_diretoria_executiva = \
            MembroAssociacao.objects.filter(associacao=associacao,
                                            cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.name).first()
        cargo_substituto_presidente_ausente_value = MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.value
    else:
        _presidente_diretoria_executiva = \
            MembroAssociacao.objects.filter(associacao=associacao, cargo_associacao=MembroEnum[
                cargo_substituto_presidente_ausente_name].name).first()
        cargo_substituto_presidente_ausente_value = MembroEnum[cargo_substituto_presidente_ausente_name].value

    _presidente_conselho_fiscal = \
        MembroAssociacao.objects.filter(associacao=associacao,
                                        cargo_associacao=MembroEnum.PRESIDENTE_CONSELHO_FISCAL.name).first()

    presidente_diretoria_executiva = _presidente_diretoria_executiva.nome if _presidente_diretoria_executiva else '-------'
    presidente_conselho_fiscal = _presidente_conselho_fiscal.nome if _presidente_conselho_fiscal else '-------'

    identificacao_apm = {
        "nome_associacao": nome_associacao,
        "cnpj_associacao": cnpj_associacao,
        "codigo_eol_associacao": codigo_eol_associacao,
        "nome_dre_associacao": nome_dre_associacao,
        "tipo_unidade": tipo_unidade,
        "nome_unidade": nome_unidade,
        "presidente_diretoria_executiva": presidente_diretoria_executiva,
        "presidente_conselho_fiscal": presidente_conselho_fiscal,
        "cargo_substituto_presidente_ausente": cargo_substituto_presidente_ausente_value,
    }

    return identificacao_apm


def cria_identificacao_conta(conta_associacao, observacao_conciliacao):
    identificacao_conta = {
        "banco": conta_associacao.banco_nome,
        "agencia": conta_associacao.agencia,
        "conta": conta_associacao.numero_conta,
        "data_extrato": observacao_conciliacao.data_extrato.strftime(
            "%d/%m/%Y") if observacao_conciliacao and observacao_conciliacao.data_extrato else "",
        "saldo_extrato": observacao_conciliacao.saldo_extrato if observacao_conciliacao and observacao_conciliacao.saldo_extrato else 0
    }

    return identificacao_conta


def cria_resumo_por_acao(acoes, conta_associacao, periodo):
    """
        Mapeamento campos x bloco 3 do PDF. Campos que são usados em cada coluna do bloco 3 no PDF:

        resumo_acoes (lista com os valores por ação):

            12-Ação                         : acao_associacao

            13-Saldo anterior           (C): linha_custeio.saldo_anterior
                                        (K): linha_capital.saldo_anterior
                                        (L): linha_livre.saldo_anterior

            14-Créditos                 (C): linha_custeio.credito
                                        (K): linha_capital.credito
                                        (L): linha_livre.credito

            15-Despesas Demonstradas    (C): linha_custeio.despesa_realizada
                                        (K): linha_capital.despesa_realizada
                                        (L): XXXXX Não tem

            16-Despesas Ñ Demonstradas  (C): linha_custeio.despesa_nao_realizada
                                        (K): linha_capital.despesa_nao_realizada
                                        (L): XXXXX Não tem

            17-Saldo próximo período    (C): linha_custeio.saldo_reprogramado_proximo
                                        (K): linha_capital.saldo_reprogramado_proximo
                                        (L): linha_livre.saldo_reprogramado_proximo
                                        (T): total_valores
                                        (*): 13+14-15-16

            18-Despesas Ñ Demonstr.Ant. (C): linha_custeio.despesa_nao_demostrada_outros_periodos
                                        (K): linha_capital.despesa_nao_demostrada_outros_periodos
                                        (L): XXXXX Não tem

            19-Saldo parcial próximo    (C): linha_custeio.valor_saldo_bancario_custeio
                                        (K): linha_capital.valor_saldo_bancario_capital
                                        (L): linha_livre.saldo_reprogramado_proximo  (mesmo da coluna 17)
                                        (T): saldo_bancario
                                        (*): 16+17+18

        total_valores (Totais):

            13-Saldo anterior           (C): saldo_anterior.C
                                        (K): saldo_anterior.K
                                        (L): saldo_anterior.L

            14-Créditos                 (C): credito.C
                                        (K): credito.K
                                        (L): credito.L

            15-Despesas Demonstradas    (C): despesa_realizada.C
                                        (K): despesa_realizada.K
                                        (L): XXXXX Não tem

            16-Despesas Ñ Demonstradas  (C): despesa_nao_realizada.C
                                        (K): despesa_nao_realizada.K
                                        (L): XXXXX Não tem

            17-Saldo próximo período    (C): saldo_reprogramado_proximo.C
                                        (K): saldo_reprogramado_proximo.K
                                        (L): saldo_reprogramado_proximo.L
                                        (T): total_valores


            18-Despesas Ñ Demonstr.Ant. (C): despesa_nao_demostrada_outros_periodos.C
                                        (K): despesa_nao_demostrada_outros_periodos.K
                                        (L): XXXXX Não tem

            19-Saldo parcial próximo    (C): valor_saldo_bancario.C
                                        (K): valor_saldo_bancario.K
                                        (L): saldo_reprogramado_proximo.L  (mesmo da coluna 17)
                                        (T): saldo_bancario

    """
    total_valores = 0
    total_conciliacao = 0

    totalizador = {
        "saldo_anterior": {'C': 0, 'K': 0, 'L': 0},
        "credito": {'C': 0, 'K': 0, 'L': 0},
        "despesa_realizada": {'C': 0, 'K': 0, 'L': 0},
        "despesa_nao_realizada": {'C': 0, 'K': 0, 'L': 0},
        "saldo_reprogramado_proximo": {'C': 0, 'K': 0, 'L': 0},
        "despesa_nao_demostrada_outros_periodos": {'C': 0, 'K': 0, 'L': 0},
        "saldo_bancario": 0,
        "valor_saldo_reprogramado_proximo_periodo": {'C': 0, 'K': 0, 'L': 0},
        "valor_saldo_bancario": {'C': 0, 'K': 0, 'L': 0},
        "credito_nao_demonstrado": {'C': 0, 'K': 0, 'L': 0},
        "total_valores": 0,
    }

    resumo_acoes = []
    for _, acao_associacao in enumerate(acoes):
        fechamento_periodo = FechamentoPeriodo.fechamentos_da_acao_no_periodo(acao_associacao=acao_associacao,
                                                                              periodo=periodo,
                                                                              conta_associacao=conta_associacao).first()

        resumo_acao, totalizador = sintese_receita_despesa(acao_associacao, conta_associacao, periodo,
                                                           fechamento_periodo, totalizador)

        if not tem_movimentacao(resumo_acao):
            continue

        total_valores += resumo_acao['total_valores']
        total_conciliacao += resumo_acao['total_conciliacao']
        resumo_acoes.append(resumo_acao)

    total_conciliacao = total_conciliacao

    resumo = {
        "resumo_acoes": resumo_acoes,
        "total_valores": totalizador,
        "total_conciliacao": total_conciliacao
    }

    return resumo


def sintese_receita_despesa(acao_associacao, conta_associacao, periodo, fechamento_periodo, totalizador):
    linha_custeio, totalizador = sintese_custeio(acao_associacao, conta_associacao, periodo, fechamento_periodo,
                                                 totalizador)
    linha_capital, totalizador = sintese_capital(acao_associacao, conta_associacao, periodo, fechamento_periodo,
                                                 totalizador)
    linha_livre, totalizador = sintese_livre(linha_capital, linha_custeio, acao_associacao, conta_associacao, periodo,
                                             fechamento_periodo, totalizador)

    valor_saldo_reprogramado_proximo_periodo_custeio = linha_custeio['valor_saldo_reprogramado_proximo_periodo_custeio']
    valor_saldo_bancario_custeio = linha_custeio['valor_saldo_bancario_custeio']
    valor_saldo_reprogramado_proximo_periodo_capital = linha_capital['valor_saldo_reprogramado_proximo_periodo_capital']
    valor_saldo_bancario_capital = linha_capital['valor_saldo_bancario_capital']
    valor_saldo_reprogramado_proximo_periodo_livre = linha_livre['valor_saldo_reprogramado_proximo_periodo_livre']

    valor_total_reprogramado_proximo = valor_saldo_reprogramado_proximo_periodo_livre
    valor_total_reprogramado_proximo = valor_total_reprogramado_proximo + \
                                       valor_saldo_reprogramado_proximo_periodo_capital if valor_saldo_reprogramado_proximo_periodo_capital > 0 else valor_total_reprogramado_proximo
    valor_total_reprogramado_proximo = valor_total_reprogramado_proximo + \
                                       valor_saldo_reprogramado_proximo_periodo_custeio if valor_saldo_reprogramado_proximo_periodo_custeio > 0 else valor_total_reprogramado_proximo

    subtotal_saldo_bancario = linha_custeio['valor_saldo_bancario_custeio'] + linha_capital[
        'valor_saldo_bancario_capital'] + linha_livre['valor_saldo_reprogramado_proximo_periodo_livre']

    total_valores = valor_total_reprogramado_proximo
    total_conciliacao = \
        valor_saldo_bancario_capital + valor_saldo_bancario_custeio + valor_saldo_reprogramado_proximo_periodo_livre

    totalizador['total_valores'] += total_valores
    totalizador['saldo_bancario'] += subtotal_saldo_bancario

    sintese = {
        "acao_associacao": acao_associacao.acao.nome,
        "linha_custeio": linha_custeio,
        "linha_capital": linha_capital,
        "linha_livre": linha_livre,
        "saldo_bancario": subtotal_saldo_bancario,
        "total_valores": total_valores,
        "total_conciliacao": total_conciliacao
    }
    return sintese, totalizador


def get_fechamento_anterior(conta_associacao, acao_associacao, periodo, fechamento_periodo):
    """ Obtem o fechamento anterior de uma conta e ação com base no período ou fechamento_periodo

    :param conta_associacao:
    :param acao_associacao:
    :param periodo:
    :param fechamento_periodo:
    :return: fechamento_anterior
    """
    if not fechamento_periodo:
        # Se não há um fechamento_periodo (caso de prévias), define o fechamento anterior pelo periodo
        if periodo and periodo.periodo_anterior:
            fechamentos_acao_periodo_anterior = FechamentoPeriodo.fechamentos_da_acao_no_periodo(
                acao_associacao=acao_associacao,
                periodo=periodo.periodo_anterior,
                conta_associacao=conta_associacao)
            fechamento_anterior = fechamentos_acao_periodo_anterior.first() if fechamentos_acao_periodo_anterior else None
        else:
            fechamento_anterior = None
    else:
        # Se há um fechamento_periodo o fechamento anterior é obtido atravez dele
        fechamento_anterior = fechamento_periodo.fechamento_anterior

    return fechamento_anterior


def sintese_custeio(acao_associacao, conta_associacao, periodo, fechamento_periodo, totalizador):
    fechamento_anterior = get_fechamento_anterior(conta_associacao=conta_associacao, acao_associacao=acao_associacao,
                                                  periodo=periodo, fechamento_periodo=fechamento_periodo)
    saldo_reprogramado_anterior_custeio = fechamento_anterior.saldo_reprogramado_custeio if fechamento_anterior else 0

    # Custeio
    receitas_demonstradas_custeio = Receita.receitas_da_acao_associacao_no_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=True,
        categoria_receita=APLICACAO_CUSTEIO).aggregate(valor=Sum('valor'))

    receitas_nao_demonstradas_custeio = Receita.receitas_da_acao_associacao_no_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=False,
        categoria_receita=APLICACAO_CUSTEIO).aggregate(valor=Sum('valor'))

    rateios_demonstrados_custeio = RateioDespesa.rateios_da_acao_associacao_no_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=True,
        aplicacao_recurso=APLICACAO_CUSTEIO).aggregate(valor=Sum('valor_rateio'))

    rateios_nao_conferidos_custeio = RateioDespesa.rateios_da_acao_associacao_no_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=False,
        aplicacao_recurso=APLICACAO_CUSTEIO).aggregate(valor=Sum('valor_rateio'))

    rateios_nao_conferidos_custeio_periodos_anteriores = RateioDespesa.rateios_da_acao_associacao_em_periodo_anteriores(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=False,
        aplicacao_recurso=APLICACAO_CUSTEIO).aggregate(valor=Sum('valor_rateio'))

    valor_custeio_receitas_demonstradas = receitas_demonstradas_custeio['valor'] or 0
    valor_custeio_receitas_nao_demonstradas = receitas_nao_demonstradas_custeio['valor'] or 0
    valor_custeio_rateios_demonstrados = rateios_demonstrados_custeio['valor'] or 0
    valor_custeio_rateios_nao_demonstrados = rateios_nao_conferidos_custeio['valor'] or 0
    valor_custeio_rateios_nao_demonstrados_periodos_anteriores = rateios_nao_conferidos_custeio_periodos_anteriores[
                                                                     'valor'] or 0

    saldo_anterior = 0
    credito = 0
    despesa_realizada = 0
    despesa_nao_realizada = 0
    despesa_nao_demostrada_outros_periodos = 0
    saldo_reprogramado_proximo = 0
    saldo_bancario = 0
    valor_saldo_reprogramado_proximo_periodo_custeio = 0
    valor_saldo_bancario_custeio = 0

    if saldo_reprogramado_anterior_custeio or valor_custeio_receitas_demonstradas or valor_custeio_rateios_demonstrados or valor_custeio_rateios_nao_demonstrados or valor_custeio_rateios_nao_demonstrados_periodos_anteriores:
        saldo_anterior = saldo_reprogramado_anterior_custeio
        credito = valor_custeio_receitas_demonstradas
        despesa_realizada = valor_custeio_rateios_demonstrados
        despesa_nao_realizada = valor_custeio_rateios_nao_demonstrados

        valor_saldo_reprogramado_proximo_periodo_custeio = (saldo_reprogramado_anterior_custeio +
                                                            valor_custeio_receitas_demonstradas -
                                                            valor_custeio_rateios_demonstrados -
                                                            valor_custeio_rateios_nao_demonstrados)

        saldo_reprogramado_proximo = (valor_saldo_reprogramado_proximo_periodo_custeio
                                      if valor_saldo_reprogramado_proximo_periodo_custeio > 0 else 0)

        despesa_nao_demostrada_outros_periodos = valor_custeio_rateios_nao_demonstrados_periodos_anteriores

        # valor_saldo_bancario_custeio = (valor_saldo_reprogramado_proximo_periodo_custeio +
        #                                 valor_custeio_rateios_nao_demonstrados +
        #                                 valor_custeio_rateios_nao_demonstrados_periodos_anteriores)

        valor_saldo_bancario_custeio = (despesa_nao_realizada +
                                        saldo_reprogramado_proximo +
                                        despesa_nao_demostrada_outros_periodos)

        valor_saldo_bancario_custeio = valor_saldo_bancario_custeio if valor_saldo_bancario_custeio > 0 else 0

        saldo_bancario = valor_saldo_bancario_custeio

    linha_custeio = {
        "saldo_anterior": saldo_anterior,
        "credito": credito,
        "despesa_realizada": despesa_realizada,
        "despesa_nao_realizada": despesa_nao_realizada,
        "despesa_nao_demostrada_outros_periodos": despesa_nao_demostrada_outros_periodos,
        "saldo_reprogramado_proximo": saldo_reprogramado_proximo,
        "saldo_reprogramado_proximo_vr": valor_saldo_reprogramado_proximo_periodo_custeio,
        "saldo_bancario": saldo_bancario,
        "valor_saldo_reprogramado_proximo_periodo_custeio": valor_saldo_reprogramado_proximo_periodo_custeio,
        "valor_saldo_bancario_custeio": valor_saldo_bancario_custeio,
        "credito_nao_demonstrado": valor_custeio_receitas_nao_demonstradas,
    }

    totalizador['saldo_anterior']['C'] += saldo_reprogramado_anterior_custeio
    totalizador['credito']['C'] += valor_custeio_receitas_demonstradas
    totalizador['despesa_realizada']['C'] += valor_custeio_rateios_demonstrados
    totalizador['despesa_nao_realizada']['C'] += valor_custeio_rateios_nao_demonstrados
    totalizador['despesa_nao_demostrada_outros_periodos'][
        'C'] += valor_custeio_rateios_nao_demonstrados_periodos_anteriores
    totalizador['saldo_reprogramado_proximo']['C'] += saldo_reprogramado_proximo
    totalizador['valor_saldo_reprogramado_proximo_periodo']['C'] += valor_saldo_reprogramado_proximo_periodo_custeio
    totalizador['valor_saldo_bancario']['C'] += valor_saldo_bancario_custeio
    totalizador['credito_nao_demonstrado']['C'] += valor_custeio_receitas_nao_demonstradas

    return linha_custeio, totalizador


def sintese_capital(acao_associacao, conta_associacao, periodo, fechamento_periodo, totalizador):
    fechamento_anterior = get_fechamento_anterior(conta_associacao=conta_associacao, acao_associacao=acao_associacao,
                                                  periodo=periodo, fechamento_periodo=fechamento_periodo)
    saldo_reprogramado_anterior_capital = fechamento_anterior.saldo_reprogramado_capital if fechamento_anterior else 0

    receitas_demonstradas_capital = Receita.receitas_da_acao_associacao_no_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=True,
        categoria_receita=APLICACAO_CAPITAL).aggregate(valor=Sum('valor'))

    receitas_nao_demonstradas_capital = Receita.receitas_da_acao_associacao_no_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=False,
        categoria_receita=APLICACAO_CAPITAL).aggregate(valor=Sum('valor'))

    rateios_demonstrados_capital = RateioDespesa.rateios_da_acao_associacao_no_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=True,
        aplicacao_recurso=APLICACAO_CAPITAL).aggregate(valor=Sum('valor_rateio'))

    rateios_nao_conferidos_capital = RateioDespesa.rateios_da_acao_associacao_no_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=False,
        aplicacao_recurso=APLICACAO_CAPITAL).aggregate(valor=Sum('valor_rateio'))

    rateios_nao_conferidos_outros_periodos = RateioDespesa.rateios_da_acao_associacao_em_periodo_anteriores(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=False,
        aplicacao_recurso=APLICACAO_CAPITAL).aggregate(valor=Sum('valor_rateio'))

    valor_capital_receitas_demonstradas = receitas_demonstradas_capital['valor'] or 0
    valor_capital_receitas_nao_demonstradas = receitas_nao_demonstradas_capital['valor'] or 0
    valor_capital_rateios_demonstrados = rateios_demonstrados_capital['valor'] or 0
    valor_capital_rateios_nao_demonstrados = rateios_nao_conferidos_capital['valor'] or 0
    valor_capital_rateios_nao_demonstrados_outros_periodos = rateios_nao_conferidos_outros_periodos['valor'] or 0

    saldo_anterior = 0
    credito = 0
    despesa_realizada = 0
    despesa_nao_realizada = 0
    despesa_nao_demostrada_outros_periodos = 0
    saldo_reprogramado_proximo = 0
    saldo_bancario = 0
    valor_saldo_reprogramado_proximo_periodo_capital = 0
    valor_saldo_bancario_capital = 0

    if saldo_reprogramado_anterior_capital or valor_capital_receitas_demonstradas or valor_capital_rateios_demonstrados or valor_capital_rateios_nao_demonstrados or valor_capital_rateios_nao_demonstrados_outros_periodos:
        saldo_anterior = saldo_reprogramado_anterior_capital
        credito = valor_capital_receitas_demonstradas
        despesa_realizada = valor_capital_rateios_demonstrados
        despesa_nao_realizada = valor_capital_rateios_nao_demonstrados
        valor_saldo_reprogramado_proximo_periodo_capital = (saldo_reprogramado_anterior_capital +
                                                            valor_capital_receitas_demonstradas -
                                                            valor_capital_rateios_demonstrados -
                                                            valor_capital_rateios_nao_demonstrados)

        saldo_reprogramado_proximo = (valor_saldo_reprogramado_proximo_periodo_capital
                                      if valor_saldo_reprogramado_proximo_periodo_capital > 0 else 0)

        despesa_nao_demostrada_outros_periodos = valor_capital_rateios_nao_demonstrados_outros_periodos
        # valor_saldo_bancario_capital = (valor_saldo_reprogramado_proximo_periodo_capital +
        #                                 valor_capital_rateios_nao_demonstrados +
        #                                 valor_capital_rateios_nao_demonstrados_outros_periodos)
        valor_saldo_bancario_capital = (despesa_nao_realizada +
                                        saldo_reprogramado_proximo +
                                        despesa_nao_demostrada_outros_periodos)

        valor_saldo_bancario_capital = valor_saldo_bancario_capital if valor_saldo_bancario_capital > 0 else 0

        saldo_bancario = valor_saldo_bancario_capital

    linha_capital = {
        "saldo_anterior": saldo_anterior,
        "credito": credito,
        "despesa_realizada": despesa_realizada,
        "despesa_nao_realizada": despesa_nao_realizada,
        "despesa_nao_demostrada_outros_periodos": despesa_nao_demostrada_outros_periodos,
        "saldo_reprogramado_proximo": saldo_reprogramado_proximo,
        "saldo_reprogramado_proximo_vr": valor_saldo_reprogramado_proximo_periodo_capital,
        "saldo_bancario": saldo_bancario,
        "valor_saldo_reprogramado_proximo_periodo_capital": valor_saldo_reprogramado_proximo_periodo_capital,
        "valor_saldo_bancario_capital": valor_saldo_bancario_capital,
        "credito_nao_demonstrado": valor_capital_receitas_nao_demonstradas,
    }

    totalizador['saldo_anterior']['K'] += saldo_reprogramado_anterior_capital
    totalizador['credito']['K'] += valor_capital_receitas_demonstradas
    totalizador['despesa_realizada']['K'] += valor_capital_rateios_demonstrados
    totalizador['despesa_nao_realizada']['K'] += valor_capital_rateios_nao_demonstrados
    totalizador['despesa_nao_demostrada_outros_periodos']['K'] += valor_capital_rateios_nao_demonstrados_outros_periodos
    totalizador['saldo_reprogramado_proximo']['K'] += (valor_saldo_reprogramado_proximo_periodo_capital
                                                       if valor_saldo_reprogramado_proximo_periodo_capital > 0 else 0)
    totalizador['valor_saldo_reprogramado_proximo_periodo']['K'] += valor_saldo_reprogramado_proximo_periodo_capital
    totalizador['valor_saldo_bancario']['K'] += valor_saldo_bancario_capital
    totalizador['credito_nao_demonstrado']['K'] += valor_capital_receitas_nao_demonstradas

    return linha_capital, totalizador


def sintese_livre(linha_capital, linha_custeio, acao_associacao, conta_associacao, periodo, fechamento_periodo,
                  totalizador):
    valor_saldo_reprogramado_proximo_periodo_custeio = linha_custeio['valor_saldo_reprogramado_proximo_periodo_custeio']
    valor_saldo_reprogramado_proximo_periodo_capital = linha_capital['valor_saldo_reprogramado_proximo_periodo_capital']

    fechamento_anterior = get_fechamento_anterior(conta_associacao=conta_associacao, acao_associacao=acao_associacao,
                                                  periodo=periodo, fechamento_periodo=fechamento_periodo)
    saldo_reprogramado_anterior_livre = fechamento_anterior.saldo_reprogramado_livre if fechamento_anterior else 0

    receitas_demonstradas_livre = Receita.receitas_da_acao_associacao_no_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=True,
        categoria_receita=APLICACAO_LIVRE).aggregate(valor=Sum('valor'))

    valor_livre_receitas_demonstradas = receitas_demonstradas_livre['valor'] or 0

    saldo_anterior = 0
    credito = 0
    saldo_reprogramado_proximo = 0
    valor_saldo_reprogramado_proximo_periodo_livre = 0

    if (
        saldo_reprogramado_anterior_livre or
        valor_livre_receitas_demonstradas or
        valor_saldo_reprogramado_proximo_periodo_custeio < 0 or
        valor_saldo_reprogramado_proximo_periodo_capital < 0
    ):
        saldo_anterior = saldo_reprogramado_anterior_livre
        credito = valor_livre_receitas_demonstradas

        valor_saldo_reprogramado_proximo_periodo_livre = (saldo_reprogramado_anterior_livre +
                                                          valor_livre_receitas_demonstradas)

        valor_saldo_reprogramado_proximo_periodo_livre = (valor_saldo_reprogramado_proximo_periodo_livre +
                                                          valor_saldo_reprogramado_proximo_periodo_capital
                                                          if valor_saldo_reprogramado_proximo_periodo_capital < 0
                                                          else valor_saldo_reprogramado_proximo_periodo_livre)

        valor_saldo_reprogramado_proximo_periodo_livre = (valor_saldo_reprogramado_proximo_periodo_livre +
                                                          valor_saldo_reprogramado_proximo_periodo_custeio
                                                          if valor_saldo_reprogramado_proximo_periodo_custeio < 0
                                                          else valor_saldo_reprogramado_proximo_periodo_livre)

        saldo_reprogramado_proximo = valor_saldo_reprogramado_proximo_periodo_livre

    linha_livre = {
        "saldo_anterior": saldo_anterior,
        "credito": credito,
        "saldo_reprogramado_proximo": saldo_reprogramado_proximo,
        "saldo_reprogramado_proximo_vr": valor_saldo_reprogramado_proximo_periodo_livre,
        "valor_saldo_reprogramado_proximo_periodo_livre": valor_saldo_reprogramado_proximo_periodo_livre,
        "credito_nao_demonstrado": 0,
    }

    totalizador['saldo_anterior']['L'] += saldo_reprogramado_anterior_livre
    totalizador['credito']['L'] += valor_livre_receitas_demonstradas
    totalizador['despesa_realizada']['L'] += 0
    totalizador['despesa_nao_realizada']['L'] += 0
    totalizador['despesa_nao_demostrada_outros_periodos']['L'] += 0
    totalizador['saldo_reprogramado_proximo']['L'] += saldo_reprogramado_proximo
    totalizador['valor_saldo_reprogramado_proximo_periodo']['L'] += valor_saldo_reprogramado_proximo_periodo_livre
    totalizador['valor_saldo_bancario']['L'] += 0
    totalizador['credito_nao_demonstrado']['L'] += 0

    return linha_livre, totalizador


def cria_creditos_demonstrados(receitas_demonstradas):
    linhas = []
    for _, receita in enumerate(receitas_demonstradas):
        linha = {
            "tipo_receita": receita.tipo_receita.nome,
            "detalhamento": receita.detalhamento,
            "nome_acao": receita.acao_associacao.acao.nome,
            "data": receita.data.strftime("%d/%m/%Y"),
            "valor": receita.valor
        }

        if receita.rateio_estornado:
            linha["estorno"] = {
                "data_estorno": receita.rateio_estornado.despesa.data_documento.strftime("%d/%m/%Y"),
                "numero_documento_despesa": receita.rateio_estornado.despesa.numero_documento if receita.rateio_estornado.despesa.numero_documento else ""
            }

        linhas.append(linha)

    valor_total = sum(r.valor for r in receitas_demonstradas)

    creditos_demonstradors = {
        "linhas": linhas,
        "valor_total": valor_total
    }

    return creditos_demonstradors


def cria_despesas(rateios):
    valor_total = sum(r.valor_rateio for r in rateios)

    linhas = []
    for _, rateio in enumerate(rateios):
        razao_social = rateio.despesa.nome_fornecedor
        cnpj_cpf = rateio.despesa.cpf_cnpj_fornecedor if rateio.despesa.cpf_cnpj_fornecedor else ''
        tipo_documento = rateio.despesa.tipo_documento.nome if rateio.despesa.tipo_documento else ''
        numero_documento = rateio.despesa.numero_documento
        nome_acao_documento = rateio.acao_associacao.acao.nome if rateio and rateio.acao_associacao and rateio.acao_associacao.acao.nome else ""
        especificacao_material = \
            rateio.especificacao_material_servico.descricao if rateio.especificacao_material_servico else ''
        tipo_despesa = rateio.aplicacao_recurso

        """
        Se o tipo de transação for cheque, deve ser exibido o número do cheque, caso contrário o tipo de transação.
        """
        tipo_transacao = rateio.despesa.tipo_transacao.nome
        if "CHEQUE" in tipo_transacao.upper():
            tipo_transacao = f"Ch-{rateio.despesa.documento_transacao}"

        data_documento = rateio.despesa.data_documento.strftime("%d/%m/%Y") if rateio.despesa.data_documento else ''
        data_transacao = rateio.despesa.data_transacao.strftime("%d/%m/%Y") if rateio.despesa.data_transacao else ''
        valor = rateio.valor_rateio
        linha = {
            "razao_social": razao_social,
            "cnpj_cpf": cnpj_cpf,
            "tipo_documento": tipo_documento,
            "numero_documento": numero_documento,
            "nome_acao_documento": nome_acao_documento,
            "especificacao_material": especificacao_material,
            "tipo_despesa": tipo_despesa,
            "tipo_transacao": tipo_transacao,
            "data_documento": data_documento,
            "data_transacao": data_transacao,
            "valor": valor
        }

        if rateio.despesa.despesa_imposto:
            # Despesas que possuem despesa imposto são despesas geradoras
            linha["despesa_imposto"] = {
                "data_transacao": rateio.despesa.despesa_imposto.data_transacao.strftime("%d/%m/%Y") if rateio.despesa.despesa_imposto.data_transacao else "",
                "valor": rateio.despesa.despesa_imposto.valor_total if rateio.despesa.despesa_imposto.valor_total else ""
            }

        if rateio.despesa.despesa_geradora_do_imposto.first():
            # Despesas que possuem despesa geradora, são despesas imposto
            despesa_geradora = rateio.despesa.despesa_geradora_do_imposto.first()
            linha["despesa_geradora"] = {
                "numero_documento": despesa_geradora.numero_documento if despesa_geradora.numero_documento else "",
                "data_transacao": despesa_geradora.data_transacao.strftime("%d/%m/%Y") if despesa_geradora.data_transacao else "",
                "valor": despesa_geradora.valor_total if despesa_geradora.valor_total else ""
            }

        linhas.append(linha)

    despesas = {
        "linhas": linhas,
        "valor_total": valor_total
    }
    return despesas


def cria_observacoes(periodo, conta_associacao):
    observacao = ObservacaoConciliacao.objects.filter(
        conta_associacao=conta_associacao,
        periodo__uuid=periodo.uuid
    ).first().texto if ObservacaoConciliacao.objects.filter(
        conta_associacao=conta_associacao, periodo__uuid=periodo.uuid
    ).exists() else ''

    return observacao


def cria_justificativas(observacao_conciliacao):
    texto_padrao = "Não houve justificativa ou informação adicional cadastrada."
    return observacao_conciliacao.texto if observacao_conciliacao and observacao_conciliacao.texto else texto_padrao


def cria_data_geracao_documento(usuario, previa):
    data_geracao = date.today().strftime("%d/%m/%Y")
    tipo_texto = "parcial" if previa else "final"
    quem_gerou = "" if usuario == "" else f"pelo usuário {usuario}, "
    texto = f"Documento {tipo_texto} gerado {quem_gerou}via SIG - Escola, em: {data_geracao}"

    return texto


def cria_data_geracao():
    data_geracao = date.today().strftime("%d/%m/%Y")

    return data_geracao


def formata_valor(valor):
    from babel.numbers import format_currency
    sinal, valor_formatado = format_currency(valor, 'BRL', locale='pt_BR').split('\xa0')
    sinal = '-' if '-' in sinal else ''
    return f'{sinal}{valor_formatado}'


def formata_data(data):
    data_formatada = " - "
    if data:
        d = datetime.strptime(str(data), '%Y-%m-%d')
        data_formatada = d.strftime("%d/%m/%Y")

    return f'{data_formatada}'


def formata_nome_dre(associacao):
    if associacao.unidade.dre:
        nome_dre = associacao.unidade.dre.nome.upper()
        if "DIRETORIA REGIONAL DE EDUCACAO" in nome_dre:
            nome_dre = nome_dre.replace("DIRETORIA REGIONAL DE EDUCACAO", "")
            nome_dre = nome_dre.strip()
            return nome_dre
        else:
            return nome_dre
    else:
        return ""


def tem_movimentacao(resumo_acao):
    # Calcula valor absoluto de custeio
    valor_absoluto_linha_custeio_saldo_anterior = abs(resumo_acao["linha_custeio"]["saldo_anterior"]) if \
        resumo_acao["linha_custeio"]["saldo_anterior"] != '' else 0

    valor_absoluto_linha_custeio_credito = abs(resumo_acao["linha_custeio"]["credito"]) if \
        resumo_acao["linha_custeio"]["credito"] != '' else 0

    valor_absoluto_linha_custeio_despesa = abs(resumo_acao["linha_custeio"]["despesa_realizada"]) if \
        resumo_acao["linha_custeio"]["despesa_realizada"] != '' else 0

    soma_absoluta_custeio = valor_absoluto_linha_custeio_saldo_anterior + valor_absoluto_linha_custeio_credito \
                            + valor_absoluto_linha_custeio_despesa

    # Calcula valor absoluto de capital
    valor_absoluto_linha_capital_saldo_anterior = abs(resumo_acao["linha_capital"]["saldo_anterior"]) if \
        resumo_acao["linha_capital"]["saldo_anterior"] != '' else 0

    valor_absoluto_linha_capital_credito = abs(resumo_acao["linha_capital"]["credito"]) if \
        resumo_acao["linha_capital"]["credito"] != '' else 0

    valor_absoluto_linha_capital_despesa = abs(resumo_acao["linha_capital"]["despesa_realizada"]) if \
        resumo_acao["linha_capital"]["despesa_realizada"] != '' else 0

    soma_absoluta_capital = valor_absoluto_linha_capital_saldo_anterior + valor_absoluto_linha_capital_credito \
                            + valor_absoluto_linha_capital_despesa

    # Calcula valor absoluto de livre
    valor_absoluto_linha_livre_saldo_anterior = abs(resumo_acao["linha_livre"]["saldo_anterior"]) if \
        resumo_acao["linha_livre"]["saldo_anterior"] != '' else 0

    valor_absoluto_linha_livre_credito = abs(resumo_acao["linha_livre"]["credito"]) if \
        resumo_acao["linha_livre"]["credito"] != '' else 0

    soma_absoluta_livre = valor_absoluto_linha_livre_saldo_anterior + valor_absoluto_linha_livre_credito

    if soma_absoluta_custeio == 0 and soma_absoluta_capital == 0 and soma_absoluta_livre == 0:
        LOGGER.info(f"A ação: {resumo_acao['acao_associacao']} não tem movimentacão, portanto não entrará na listagem.")
        return False

    return True

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


def gerar_dados_demonstrativo_financeiro(usuario, acoes, periodo, conta_associacao, prestacao, previa=False):
    try:
        LOGGER.info("GERANDO DADOS DEMONSTRATIVO...")
        rateios_conferidos = RateioDespesa.rateios_da_conta_associacao_no_periodo(
            conta_associacao=conta_associacao, periodo=periodo, conferido=True)

        rateios_nao_conferidos = RateioDespesa.rateios_da_conta_associacao_no_periodo(
            conta_associacao=conta_associacao, periodo=periodo, conferido=False)

        rateios_nao_conferidos_periodos_anteriores = RateioDespesa.rateios_da_conta_associacao_em_periodos_anteriores(
            conta_associacao=conta_associacao, periodo=periodo, conferido=False)

        receitas_demonstradas = Receita.receitas_da_conta_associacao_no_periodo(
            conta_associacao=conta_associacao, periodo=periodo, conferido=True)

        cabecalho = cria_cabecalho(periodo, conta_associacao, previa)
        identificacao_apm = cria_identificacao_apm(acoes)
        identificacao_conta = cria_identificacao_conta(conta_associacao)
        resumo_por_acao = cria_resumo_por_acao(acoes, conta_associacao, periodo)
        creditos_demonstrados = cria_creditos_demonstrados(receitas_demonstradas)
        despesas_demonstradas = cria_despesas(rateios_conferidos)
        despesas_nao_demonstradas = cria_despesas(rateios_nao_conferidos)
        despesas_anteriores_nao_demonstradas = cria_despesas(rateios_nao_conferidos_periodos_anteriores)
        observacoes = cria_observacoes(periodo, conta_associacao)
        data_geracao_documento = cria_data_geracao_documento(usuario, previa)
        data_geracao = cria_data_geracao()

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

    nome_associacao = associacao.nome
    cnpj_associacao = associacao.cnpj
    codigo_eol_associacao = associacao.unidade.codigo_eol or ""
    nome_dre_associacao = associacao.unidade.dre.nome if associacao.unidade.dre else ""

    _presidente_diretoria_executiva = \
        MembroAssociacao.objects.filter(associacao=associacao,
                                        cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.name).first()

    _presidente_conselho_fiscal = \
        MembroAssociacao.objects.filter(associacao=associacao,
                                        cargo_associacao=MembroEnum.PRESIDENTE_CONSELHO_FISCAL.name).first()

    presidente_diretoria_executiva = _presidente_diretoria_executiva.nome if _presidente_diretoria_executiva else ''
    presidente_conselho_fiscal = _presidente_conselho_fiscal.nome if _presidente_conselho_fiscal else ''

    identificacao_apm = {
        "nome_associacao": nome_associacao,
        "cnpj_associacao": cnpj_associacao,
        "codigo_eol_associacao": codigo_eol_associacao,
        "nome_dre_associacao": nome_dre_associacao,
        "presidente_diretoria_executiva": presidente_diretoria_executiva,
        "presidente_conselho_fiscal": presidente_conselho_fiscal
    }

    return identificacao_apm


def cria_identificacao_conta(conta_associacao):
    identificacao_conta = {
        "banco": conta_associacao.banco_nome,
        "agencia": conta_associacao.agencia,
        "conta": conta_associacao.numero_conta,
        "data_extrato": date.today().strftime("%d/%m/%Y"),
        "saldo_extrato": 0
    }

    return identificacao_conta


def cria_resumo_por_acao(acoes, conta_associacao, periodo):
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

    saldo_anterior = ""
    credito = ""
    despesa_realizada = ""
    despesa_nao_realizada = ""
    despesa_nao_demostrada_outros_periodos = ""
    saldo_reprogramado_proximo = ""
    saldo_bancario = ""
    valor_saldo_reprogramado_proximo_periodo_custeio = 0
    valor_saldo_bancario_custeio = 0

    if saldo_reprogramado_anterior_custeio or valor_custeio_receitas_demonstradas or valor_custeio_rateios_demonstrados or valor_custeio_rateios_nao_demonstrados or valor_custeio_rateios_nao_demonstrados_periodos_anteriores:
        saldo_anterior = saldo_reprogramado_anterior_custeio
        credito =valor_custeio_receitas_demonstradas
        despesa_realizada = valor_custeio_rateios_demonstrados
        despesa_nao_realizada = valor_custeio_rateios_nao_demonstrados


        valor_saldo_reprogramado_proximo_periodo_custeio = saldo_reprogramado_anterior_custeio + \
                                                           valor_custeio_receitas_demonstradas - \
                                                           valor_custeio_rateios_demonstrados - \
                                                           valor_custeio_rateios_nao_demonstrados

        saldo_reprogramado_proximo = valor_saldo_reprogramado_proximo_periodo_custeio if valor_saldo_reprogramado_proximo_periodo_custeio > 0 else 0


        despesa_nao_demostrada_outros_periodos = valor_custeio_rateios_nao_demonstrados_periodos_anteriores
        valor_saldo_bancario_custeio = valor_saldo_reprogramado_proximo_periodo_custeio + valor_custeio_rateios_nao_demonstrados + valor_custeio_rateios_nao_demonstrados_periodos_anteriores
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
    totalizador['saldo_reprogramado_proximo']['C'] += valor_saldo_reprogramado_proximo_periodo_custeio
    # totalizador['saldo_bancario']['C'] += valor_saldo_bancario_custeio
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

    saldo_anterior = ""
    credito = ""
    despesa_realizada = ""
    despesa_nao_realizada = ""
    despesa_nao_demostrada_outros_periodos = ""
    saldo_reprogramado_proximo = ""
    saldo_bancario = ""
    valor_saldo_reprogramado_proximo_periodo_capital = 0
    valor_saldo_bancario_capital = 0

    if saldo_reprogramado_anterior_capital or valor_capital_receitas_demonstradas or valor_capital_rateios_demonstrados or valor_capital_rateios_nao_demonstrados or valor_capital_rateios_nao_demonstrados_outros_periodos:
        saldo_anterior = saldo_reprogramado_anterior_capital
        credito = valor_capital_receitas_demonstradas
        despesa_realizada = valor_capital_rateios_demonstrados
        despesa_nao_realizada = valor_capital_rateios_nao_demonstrados
        valor_saldo_reprogramado_proximo_periodo_capital = saldo_reprogramado_anterior_capital + \
                                                           valor_capital_receitas_demonstradas - \
                                                           valor_capital_rateios_demonstrados - \
                                                           valor_capital_rateios_nao_demonstrados
        saldo_reprogramado_proximo = valor_saldo_reprogramado_proximo_periodo_capital if valor_saldo_reprogramado_proximo_periodo_capital > 0 else 0
        despesa_nao_demostrada_outros_periodos = valor_capital_rateios_nao_demonstrados_outros_periodos
        valor_saldo_bancario_capital = valor_saldo_reprogramado_proximo_periodo_capital + valor_capital_rateios_nao_demonstrados + valor_capital_rateios_nao_demonstrados_outros_periodos
        valor_saldo_bancario_capital = valor_saldo_bancario_capital if valor_saldo_bancario_capital > 0 else 0
        saldo_bancario =valor_saldo_bancario_capital

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
    totalizador['saldo_reprogramado_proximo'][
        'K'] += valor_saldo_reprogramado_proximo_periodo_capital if valor_saldo_reprogramado_proximo_periodo_capital > 0 else 0
    # totalizador['saldo_bancario']['K'] += valor_saldo_bancario_capital
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

    saldo_anterior = ""
    credito = ""
    saldo_reprogramado_proximo = ""
    valor_saldo_reprogramado_proximo_periodo_livre = 0

    if saldo_reprogramado_anterior_livre or valor_livre_receitas_demonstradas or valor_saldo_reprogramado_proximo_periodo_custeio < 0 or valor_saldo_reprogramado_proximo_periodo_capital < 0:
        saldo_anterior = saldo_reprogramado_anterior_livre
        credito = valor_livre_receitas_demonstradas
        valor_saldo_reprogramado_proximo_periodo_livre = saldo_reprogramado_anterior_livre + valor_livre_receitas_demonstradas
        valor_saldo_reprogramado_proximo_periodo_livre = valor_saldo_reprogramado_proximo_periodo_livre + \
                                                         valor_saldo_reprogramado_proximo_periodo_capital if valor_saldo_reprogramado_proximo_periodo_capital < 0 else valor_saldo_reprogramado_proximo_periodo_livre
        valor_saldo_reprogramado_proximo_periodo_livre = valor_saldo_reprogramado_proximo_periodo_livre + \
                                                         valor_saldo_reprogramado_proximo_periodo_custeio if valor_saldo_reprogramado_proximo_periodo_custeio < 0 else valor_saldo_reprogramado_proximo_periodo_livre
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
    totalizador['saldo_reprogramado_proximo']['L'] += valor_saldo_reprogramado_proximo_periodo_livre
    # totalizador['saldo_bancario']['L'] += 0
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
        cnpj_cpf = rateio.despesa.cpf_cnpj_fornecedor
        tipo_documento = rateio.despesa.tipo_documento.nome if rateio.despesa.tipo_documento else ''
        numero_documento = rateio.despesa.numero_documento
        nome_acao_documento = rateio.acao_associacao.acao.nome
        especificacao_material = \
            rateio.especificacao_material_servico.descricao if rateio.especificacao_material_servico else ''
        tipo_despesa = rateio.aplicacao_recurso

        tipo_transacao = ''
        if rateio.conta_associacao.tipo_conta:
            if rateio.conta_associacao.tipo_conta.nome == 'Cheque':
                tipo_transacao = rateio.despesa.documento_transacao
            else:
                tipo_transacao = rateio.despesa.tipo_transacao.nome

        data_documento = rateio.despesa.data_documento.strftime("%d/%m/%Y") if rateio.despesa.data_documento else ''
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
            "valor": valor
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

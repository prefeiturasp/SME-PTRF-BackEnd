import logging
import os

import re
from copy import copy
from tempfile import NamedTemporaryFile

from datetime import date

from django.db.models import Sum
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files import File

from sme_ptrf_apps.core.choices import MembroEnum

from sme_ptrf_apps.core.models import (FechamentoPeriodo, MembroAssociacao, ObservacaoConciliacao,
                                       DemonstrativoFinanceiro)
from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.receitas.models import Receita
from sme_ptrf_apps.receitas.tipos_aplicacao_recurso_receitas import (APLICACAO_CAPITAL, APLICACAO_CUSTEIO,
                                                                     APLICACAO_LIVRE)


LOGGER = logging.getLogger(__name__)


def gerar_dados_demonstrativo_financeiro(usuario, acoes, periodo, conta_associacao, previa=False):

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

        fechamento_periodo = FechamentoPeriodo.objects.filter(
            conta_associacao=conta_associacao, periodo__uuid=periodo.uuid).first()

        cabecalho = cria_cabecalho(periodo, conta_associacao, previa)
        identificacao_apm = cria_identificacao_apm(acoes)
        identificacao_conta = cria_identificacao_conta(conta_associacao)
        resumo_por_acao = cria_resumo_por_acao(acoes, conta_associacao, periodo, fechamento_periodo)
        creditos_demonstrados = cria_creditos_demonstrados(receitas_demonstradas)
        despesas_demonstradas = cria_despesas(rateios_conferidos)
        despesas_nao_demonstradas = cria_despesas(rateios_nao_conferidos)
        despesas_anteriores_nao_demonstradas = cria_despesas(rateios_nao_conferidos_periodos_anteriores)
        observacoes_acoes = cria_observacoes(acoes, periodo, conta_associacao)
        data_geracao = cria_data_geracao_documento(usuario, previa)

        dados_demonstrativo = {
            cabecalho,
            identificacao_apm,
            identificacao_conta,
            resumo_por_acao,
            creditos_demonstrados,
            despesas_demonstradas,
            despesas_nao_demonstradas,
            despesas_anteriores_nao_demonstradas,
            observacoes_acoes,
            data_geracao
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
        nome_associacao,
        cnpj_associacao,
        codigo_eol_associacao,
        nome_dre_associacao,
        presidente_diretoria_executiva,
        presidente_conselho_fiscal
    }

    return identificacao_apm


def cria_identificacao_conta(conta_associacao):

    identificacao_conta = {
        "banco": conta_associacao.banco_nome,
        "agencia": conta_associacao.agencia,
        "conta": conta_associacao.numero_conta,
        "data_extrato": date.today().strftime("%d/%m/%Y"),
        "saldo_extrato": formata_valor(0)
    }

    return identificacao_conta


def cria_resumo_por_acao(acoes, conta_associacao, periodo, fechamento_periodo):
    total_valores = 0
    total_conciliacao = 0

    resumo_acoes = []
    for acao_associacao in enumerate(acoes):
        resumo_acao = sintese_receita_despesa(acao_associacao, conta_associacao, periodo, fechamento_periodo)
        total_valores += resumo_acao.total_valores
        total_conciliacao += resumo_acao.total_conciliacao

    total_valores = formata_valor(total_valores)
    total_conciliacao = formata_valor(total_conciliacao)

    resumo = {
        resumo_acoes,
        total_valores,
        total_conciliacao
    }

    return resumo


def sintese_receita_despesa(acao_associacao, conta_associacao, periodo, fechamento_periodo):
    valor_saldo_reprogramado_proximo_periodo_custeio, valor_saldo_bancario_custeio, linha = sintese_custeio(
        row_custeio, linha, acao_associacao, conta_associacao, periodo, fechamento_periodo
    )

    valor_saldo_reprogramado_proximo_periodo_capital, valor_saldo_bancario_capital, linha = sintese_capital(
        row_capital, linha, acao_associacao, conta_associacao, periodo, fechamento_periodo
    )

    valor_saldo_reprogramado_proximo_periodo_livre, linha = sintese_livre(
        row_livre, linha, valor_saldo_reprogramado_proximo_periodo_custeio,
        valor_saldo_reprogramado_proximo_periodo_capital, acao_associacao,
        conta_associacao, periodo, fechamento_periodo
    )

    valor_total_reprogramado_proximo = valor_saldo_reprogramado_proximo_periodo_livre
    valor_total_reprogramado_proximo = valor_total_reprogramado_proximo + \
                                       valor_saldo_reprogramado_proximo_periodo_capital if valor_saldo_reprogramado_proximo_periodo_capital > 0 else valor_total_reprogramado_proximo
    valor_total_reprogramado_proximo = valor_total_reprogramado_proximo + \
                                       valor_saldo_reprogramado_proximo_periodo_custeio if valor_saldo_reprogramado_proximo_periodo_custeio > 0 else valor_total_reprogramado_proximo
    row_livre[
        SALDO_BANCARIO].value = f'L {formata_valor(valor_saldo_reprogramado_proximo_periodo_livre)}' if valor_saldo_reprogramado_proximo_periodo_livre != 0 else ''

    total_valores = valor_total_reprogramado_proximo
    total_conciliacao = \
        valor_saldo_bancario_capital + valor_saldo_bancario_custeio + valor_saldo_reprogramado_proximo_periodo_livre

    sintese = {
        total_valores,
        total_conciliacao
    }
    return sintese


def sintese_custeio(row_custeio, linha, acao_associacao, conta_associacao, periodo, fechamento_periodo):
    """
    retorna uma tupla de saldos relacionados aos custeios
    """
    saldo_reprogramado_anterior_custeio = fechamento_periodo.fechamento_anterior.saldo_reprogramado_custeio if fechamento_periodo and fechamento_periodo.fechamento_anterior else 0
    # Custeio
    receitas_demonstradas_custeio = Receita.receitas_da_acao_associacao_no_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=True,
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
    valor_custeio_rateios_demonstrados = rateios_demonstrados_custeio['valor'] or 0
    valor_custeio_rateios_nao_demonstrados = rateios_nao_conferidos_custeio['valor'] or 0
    valor_custeio_rateios_nao_demonstrados_periodos_anteriores = rateios_nao_conferidos_custeio_periodos_anteriores[
                                                                     'valor'] or 0

    if saldo_reprogramado_anterior_custeio or valor_custeio_receitas_demonstradas or valor_custeio_rateios_demonstrados or valor_custeio_rateios_nao_demonstrados or valor_custeio_rateios_nao_demonstrados_periodos_anteriores:
        row_custeio[SALDO_ANTERIOR].value = f'C {formata_valor(saldo_reprogramado_anterior_custeio)}'
        row_custeio[CREDITO].value = f'C {formata_valor(valor_custeio_receitas_demonstradas)}'
        row_custeio[DESPESA_REALIZADA].value = f'C {formata_valor(valor_custeio_rateios_demonstrados)}'
        row_custeio[DESPESA_NAO_REALIZADA].value = f'C {formata_valor(valor_custeio_rateios_nao_demonstrados)}'
        valor_saldo_reprogramado_proximo_periodo_custeio = saldo_reprogramado_anterior_custeio + \
                                                           valor_custeio_receitas_demonstradas - \
                                                           valor_custeio_rateios_demonstrados - \
                                                           valor_custeio_rateios_nao_demonstrados
        row_custeio[
            SALDO_REPROGRAMADO_PROXIMO].value = f'C {formata_valor(valor_saldo_reprogramado_proximo_periodo_custeio if valor_saldo_reprogramado_proximo_periodo_custeio > 0 else 0)}'

        row_custeio[
            DESPESA_NAO_DEMONSTRADA_OUTROS_PERIODOS].value = f'C {formata_valor(valor_custeio_rateios_nao_demonstrados_periodos_anteriores)}'
        valor_saldo_bancario_custeio = valor_saldo_reprogramado_proximo_periodo_custeio + valor_custeio_rateios_nao_demonstrados + valor_custeio_rateios_nao_demonstrados_periodos_anteriores
        valor_saldo_bancario_custeio = valor_saldo_bancario_custeio if valor_saldo_bancario_custeio > 0 else 0
        row_custeio[SALDO_BANCARIO].value = f'C {formata_valor(valor_saldo_bancario_custeio)}'
        linha += 1

        return valor_saldo_reprogramado_proximo_periodo_custeio, valor_saldo_bancario_custeio, linha

    return (0, 0, linha)


def sintese_capital(row_capital, linha, acao_associacao, conta_associacao, periodo, fechamento_periodo):
    """
    retorna uma tupla de saldos relacionados aos capitais
    """
    saldo_reprogramado_anterior_capital = fechamento_periodo.fechamento_anterior.saldo_reprogramado_capital if fechamento_periodo and fechamento_periodo.fechamento_anterior else 0
    receitas_demonstradas_capital = Receita.receitas_da_acao_associacao_no_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=True,
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
    valor_capital_rateios_demonstrados = rateios_demonstrados_capital['valor'] or 0
    valor_capital_rateios_nao_demonstrados = rateios_nao_conferidos_capital['valor'] or 0
    valor_capital_rateios_nao_demonstrados_outros_periodos = rateios_nao_conferidos_outros_periodos['valor'] or 0

    if saldo_reprogramado_anterior_capital or valor_capital_receitas_demonstradas or valor_capital_rateios_demonstrados or valor_capital_rateios_nao_demonstrados or valor_capital_rateios_nao_demonstrados_outros_periodos:
        row_capital[SALDO_ANTERIOR].value = f'K {formata_valor(saldo_reprogramado_anterior_capital)}'
        row_capital[CREDITO].value = f'K {formata_valor(valor_capital_receitas_demonstradas)}'
        row_capital[DESPESA_REALIZADA].value = f'K {formata_valor(valor_capital_rateios_demonstrados)}'
        row_capital[DESPESA_NAO_REALIZADA].value = f'K {formata_valor(valor_capital_rateios_nao_demonstrados)}'
        valor_saldo_reprogramado_proximo_periodo_capital = saldo_reprogramado_anterior_capital + \
                                                           valor_capital_receitas_demonstradas - \
                                                           valor_capital_rateios_demonstrados - \
                                                           valor_capital_rateios_nao_demonstrados
        row_capital[
            SALDO_REPROGRAMADO_PROXIMO].value = f'K {formata_valor(valor_saldo_reprogramado_proximo_periodo_capital if valor_saldo_reprogramado_proximo_periodo_capital > 0 else 0)}'
        row_capital[
            DESPESA_NAO_DEMONSTRADA_OUTROS_PERIODOS].value = f'K {formata_valor(valor_capital_rateios_nao_demonstrados_outros_periodos)}'
        valor_saldo_bancario_capital = valor_saldo_reprogramado_proximo_periodo_capital + valor_capital_rateios_nao_demonstrados + valor_capital_rateios_nao_demonstrados_outros_periodos
        valor_saldo_bancario_capital = valor_saldo_bancario_capital if valor_saldo_bancario_capital > 0 else 0
        row_capital[SALDO_BANCARIO].value = f'K {formata_valor(valor_saldo_bancario_capital)}'
        linha += 1

        return valor_saldo_reprogramado_proximo_periodo_capital, valor_saldo_bancario_capital, linha

    return (0, 0, linha)


def sintese_livre(row_livre, linha, valor_saldo_reprogramado_proximo_periodo_custeio,
                  valor_saldo_reprogramado_proximo_periodo_capital, acao_associacao,
                  conta_associacao, periodo, fechamento_periodo):

    saldo_reprogramado_anterior_livre = fechamento_periodo.fechamento_anterior.saldo_reprogramado_livre if fechamento_periodo and fechamento_periodo.fechamento_anterior else 0

    receitas_demonstradas_livre = Receita.receitas_da_acao_associacao_no_periodo(
        acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo=periodo, conferido=True,
        categoria_receita=APLICACAO_LIVRE).aggregate(valor=Sum('valor'))

    valor_livre_receitas_demonstradas = receitas_demonstradas_livre['valor'] or 0

    if saldo_reprogramado_anterior_livre or valor_livre_receitas_demonstradas or valor_saldo_reprogramado_proximo_periodo_custeio < 0 or valor_saldo_reprogramado_proximo_periodo_capital < 0:
        row_livre[SALDO_ANTERIOR].value = f'L {formata_valor(saldo_reprogramado_anterior_livre)}'
        row_livre[CREDITO].value = f'L {formata_valor(valor_livre_receitas_demonstradas)}'
        cor_cinza = styles.colors.Color(rgb='808080')
        fill = styles.fills.PatternFill(patternType='solid', fgColor=cor_cinza)
        row_livre[DESPESA_REALIZADA].fill = fill
        row_livre[DESPESA_NAO_REALIZADA].fill = fill
        row_livre[DESPESA_NAO_DEMONSTRADA_OUTROS_PERIODOS].fill = fill
        valor_saldo_reprogramado_proximo_periodo_livre = saldo_reprogramado_anterior_livre + valor_livre_receitas_demonstradas
        valor_saldo_reprogramado_proximo_periodo_livre = valor_saldo_reprogramado_proximo_periodo_livre + \
                                                         valor_saldo_reprogramado_proximo_periodo_capital if valor_saldo_reprogramado_proximo_periodo_capital < 0 else valor_saldo_reprogramado_proximo_periodo_livre
        valor_saldo_reprogramado_proximo_periodo_livre = valor_saldo_reprogramado_proximo_periodo_livre + \
                                                         valor_saldo_reprogramado_proximo_periodo_custeio if valor_saldo_reprogramado_proximo_periodo_custeio < 0 else valor_saldo_reprogramado_proximo_periodo_livre
        row_livre[
            SALDO_REPROGRAMADO_PROXIMO].value = f'L {formata_valor(valor_saldo_reprogramado_proximo_periodo_livre)}'

        return valor_saldo_reprogramado_proximo_periodo_livre, linha

    return (0, linha)


def cria_creditos_demonstrados(receitas_demonstradas):

    linhas = []
    for receita in enumerate(receitas_demonstradas):
        linha = {
            "tipo_receita": receita.tipo_receita.nome,
            "detalhamento": receita.detalhamento,
            "nome_acao": receita.acao_associacao.acao.nome,
            "data": receita.data.strftime("%d/%m/%Y"),
            "valor": formata_valor(receita.valor)
        }
        linhas.append(linha)

    valor_total = formata_valor(sum(r.valor for r in receitas_demonstradas))

    creditos_demonstradors = {
        linhas,
        valor_total
    }

    return creditos_demonstradors


def cria_despesas(rateios):
    valor_total = formata_valor(sum(r.valor_rateio for r in rateios))

    linhas = []
    for rateio in enumerate(rateios):
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
        valor = formata_valor(rateio.valor_rateio)
        linha = {
            razao_social,
            cnpj_cpf,
            tipo_documento,
            numero_documento,
            nome_acao_documento,
            especificacao_material,
            tipo_despesa,
            tipo_transacao,
            data_documento,
            valor
        }
        linhas.append(linha)

    despesas = {
        linhas,
        valor_total
    }
    return despesas


def cria_observacoes(acoes, periodo, conta_associacao):

    observacoes = []
    for acao_associacao in enumerate(acoes):
        observacao = ObservacaoConciliacao.objects.filter(
            acao_associacao=acao_associacao,
            conta_associacao=conta_associacao,
            periodo__uuid=periodo.uuid
        ).first().texto if ObservacaoConciliacao.objects.filter(
            acao_associacao=acao_associacao, conta_associacao=conta_associacao, periodo__uuid=periodo.uuid
        ).exists() else ''
        if len(observacao) > 0:
            observacoes.append({
                "nome_acao_associacao": acao_associacao.acao.nome,
                "observacao": observacao
            })

    return observacoes


def cria_data_geracao_documento(usuario, previa):

    data_geracao = date.today().strftime("%d/%m/%Y")
    tipo_texto = "parcial" if previa else "final"
    quem_gerou = "" if usuario == "" else f"pelo usuário {usuario}, "
    texto = f"Documento {tipo_texto} gerado {quem_gerou}via SIG - Escola, em: {data_geracao}"

    return texto


def formata_valor(valor):
    from babel.numbers import format_currency
    sinal, valor_formatado = format_currency(valor, 'BRL', locale='pt_BR').split('\xa0')
    sinal = '-' if '-' in sinal else ''
    return f'{sinal}{valor_formatado}'


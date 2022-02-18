"""Gerador da planilha de relatórios consolidados

Esse serviço gera uma planilha no formato .xlsx com base na planilha modelo (modelo_relatorio_dre_sme.xlsx)
que foi fornecida pela PO e está nos statics da aplicação.

Esse script tem as seguintes funções:
    * gera_relatorio_dre - Cria o modelo RelatorioConsolidadoDRE que armazenará a planilha.
    * gerar - Função inicial para gerar a planilha.
    * cabecalho - Preenche o cabeçalho da planilha.
    * identificacao_dre - Preenche o bloco de identificação da DRE da planilha.
    * assinatura_dre - Preenche o bloco de assinaturas.
    * data_geracao_documento - Preenche a data de geração do documento.
    * execucao_financeira - Preenche o bloco de execuções financeiras.
    * execucao_fisica - Preenche o bloco de execuções fisicas.
    * associacoes_nao_regularizadas - Preenche as associações não regularizadas do bloco de execuções físicas.
    * dados_fisicos_financeiros - Dadis físicos finceiros do bloco 4 da planiha.
"""

import logging
import os
from datetime import date
from tempfile import NamedTemporaryFile

from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files import File
from openpyxl import load_workbook

from sme_ptrf_apps.core.models import Associacao, PrestacaoConta
from sme_ptrf_apps.core.services.xlsx_copy_row import copy_row, copy_row_direct
from sme_ptrf_apps.dre.models import JustificativaRelatorioConsolidadoDRE, RelatorioConsolidadoDRE

from .relatorio_consolidado_service import (
    informacoes_devolucoes_a_conta_ptrf,
    informacoes_devolucoes_ao_tesouro,
    informacoes_execucao_financeira,
    informacoes_execucao_financeira_unidades,
)

LOGGER = logging.getLogger(__name__)

# Cabeçalho
COL_CABECALHO = 9
COL_TEXTO_CABECALHO = 6
LINHA_TEXTO_CABECALHO = 2
LINHA_PERIODO_CABECALHO = 4
LINHA_TIPO_CONTA_CABECALHO = 5

# Identificação
LINHA_IDENTIFICACAO = 9
COL_IDENTIFICACAO_DRE = 0
COL_IDENTIFICACAO_CNPJ = 7

# Execução Financeira
LINHA_CUSTEIO = 13
LINHA_CAPITAL = 14
LINHA_RLA = 15
LINHA_TOTAL = 16
COL_SALDO_REPROGRAMADO_ANTERIOR = 1
COL_REPASSES_PREVISTOS = 2
COL_REPASSES_NO_PERIODO = 3
COL_RENDIMENTO = 4
COL_RECEITAS_DEVOLUCAO = 5
COL_DEMAIS_CREDITOS = 6
COL_VALOR_TOTAL = 7
COL_DESPESA_NO_PERIODO = 8
COL_SALDO_REPROGRAMADO_PROXIMO = 9
COL_DEVOLUCAO_TESOURO = 11

# Execução Financeira - Justificativa
LINHA_JUSTIFICATIVA = 19

# Execução Física
LINHA_EXECUCAO_FISICA = 25

LAST_LINE = 56


def gera_relatorio_dre(dre, periodo, tipo_conta, parcial=False):

    LOGGER.info("Relatório consolidado em processamento...")

    relatorio_consolidado, _ = RelatorioConsolidadoDRE.objects.update_or_create(
        dre=dre,
        periodo=periodo,
        tipo_conta=tipo_conta,
        defaults={
            'status': RelatorioConsolidadoDRE.STATUS_EM_PROCESSAMENTO,
            'versao': RelatorioConsolidadoDRE.VERSAO_FINAL
        }
    )

    filename = 'relatorio_consolidade_dre_%s.xlsx'

    xlsx = gerar(dre, periodo, tipo_conta, parcial=parcial)

    with NamedTemporaryFile() as tmp:
        xlsx.save(tmp.name)
        relatorio_consolidado.arquivo.save(name=filename % relatorio_consolidado.pk, content=File(tmp))

    relatorio_consolidado.status = (
        RelatorioConsolidadoDRE.STATUS_GERADO_PARCIAL if parcial
        else RelatorioConsolidadoDRE.STATUS_GERADO_TOTAL
    )
    relatorio_consolidado.save()

    LOGGER.info("Relatório Consolidado Gerado: uuid: %s, status: %s",
                relatorio_consolidado.uuid, relatorio_consolidado.status)


def gera_previa_relatorio_dre(dre, periodo, tipo_conta, parcial=False):
    LOGGER.info("Prévia relatório consolidado em processamento...")

    relatorio_consolidado, _ = RelatorioConsolidadoDRE.objects.update_or_create(
        dre=dre,
        periodo=periodo,
        tipo_conta=tipo_conta,
        defaults={'status': RelatorioConsolidadoDRE.STATUS_EM_PROCESSAMENTO},
        versao=RelatorioConsolidadoDRE.VERSAO_PREVIA
    )

    filename = 'previa_relatorio_consolidade_dre_%s.xlsx'

    xlsx = gerar(dre, periodo, tipo_conta, parcial=parcial)

    with NamedTemporaryFile() as tmp:
        xlsx.save(tmp.name)
        relatorio_consolidado.arquivo.save(name=filename % relatorio_consolidado.pk, content=File(tmp))

    relatorio_consolidado.status = (
        RelatorioConsolidadoDRE.STATUS_GERADO_PARCIAL if parcial
        else RelatorioConsolidadoDRE.STATUS_GERADO_TOTAL
    )
    relatorio_consolidado.save()

    LOGGER.info("Prévia relatório Consolidado Gerado: uuid: %s, status: %s",
                relatorio_consolidado.uuid, relatorio_consolidado.status)


def gerar(dre, periodo, tipo_conta, parcial=False):
    LOGGER.info("Gerando relatório consolidado...")

    path = os.path.join(os.path.basename(staticfiles_storage.location), 'cargas')
    nome_arquivo = os.path.join(path, 'modelo_relatorio_dre_sme.xlsx')
    workbook = load_workbook(nome_arquivo)
    worksheet = workbook.active
    try:
        LOGGER.info("Iniciando cabecalho...")
        cabecalho(worksheet, periodo, tipo_conta, parcial)
        LOGGER.info("Iniciando identificacao...")
        identificacao_dre(worksheet, dre)
        LOGGER.info("Iniciando assinatura...")
        assinatura_dre(worksheet, dre)
        LOGGER.info("Iniciando data geracao...")
        data_geracao_documento(worksheet, parcial)
        LOGGER.info("Iniciando execucao financeira...")
        execucao_financeira(worksheet, dre, periodo, tipo_conta)
        LOGGER.info("Iniciando execucao fisica...")
        execucao_fisica(worksheet, dre, periodo)

        LOGGER.info("Iniciando associacoes pendentes...")


        #TODO Impmentar busca de regularidade pendente por ano
        associacoes_pendentes = Associacao.objects.filter(
            unidade__dre=dre).exclude(cnpj__exact='')

        associacoes_nao_regularizadas(worksheet, associacoes_pendentes)
        LOGGER.info("Iniciando dados fisicos financeiros...")
        acc = len(associacoes_pendentes) - 1 if len(associacoes_pendentes) > 1 else 0
        dados_fisicos_financeiros(worksheet, dre, periodo, tipo_conta, acc=acc)
    except Exception as err:
        LOGGER.info("Erro %s", str(err))
        raise err

    return workbook


def cabecalho(worksheet, periodo, tipo_conta, parcial):
    rows = list(worksheet.rows)
    status = "PARCIAL" if parcial else "FINAL"
    texto = f"Demonstrativo financeiro e do acompanhamento das prestações de conta das Associações - {status}"
    rows[LINHA_TEXTO_CABECALHO][COL_TEXTO_CABECALHO].value = texto
    rows[LINHA_PERIODO_CABECALHO][COL_CABECALHO].value = str(periodo)
    rows[LINHA_TIPO_CONTA_CABECALHO][COL_CABECALHO].value = tipo_conta.nome


def identificacao_dre(worksheet, dre):
    """BLOCO 1 - IDENTIFICAÇÃO"""
    rows = list(worksheet.rows)
    rows[LINHA_IDENTIFICACAO][COL_IDENTIFICACAO_DRE].value = dre.nome
    rows[LINHA_IDENTIFICACAO][COL_IDENTIFICACAO_CNPJ].value = dre.dre_cnpj


def assinatura_dre(worksheet, dre):
    """Bloco 5 - Autenticação: Parte de assinaturas"""

    rows = list(worksheet.rows)
    rows[53][0].value = f"""________________________________________
    Assinatura e carimbo do responsável pela área contábil da DRE {dre.nome}"""

    rows[53][4].value = f"""________________________________________
    Assinatura e carimbo do responsável do Presidente da Comissão Específica da DRE {dre.nome}"""

    rows[53][8].value = f"""________________________________________
    Assinatura e carimbo do Diretor Regional de Educação da DRE {dre.nome}"""


def execucao_financeira(worksheet, dre, periodo, tipo_conta):
    """BLOCO 2 - EXECUÇÃO FINANCEIRA"""
    rows = list(worksheet.rows)
    info = informacoes_execucao_financeira(dre, periodo, tipo_conta)

    # LINHA CUSTEIO
    rows[LINHA_CUSTEIO][COL_SALDO_REPROGRAMADO_ANTERIOR].value = formata_valor(
        info['saldo_reprogramado_periodo_anterior_custeio'])
    rows[LINHA_CUSTEIO][COL_REPASSES_PREVISTOS].value = formata_valor(info['repasses_previstos_sme_custeio'])
    rows[LINHA_CUSTEIO][COL_REPASSES_NO_PERIODO].value = formata_valor(info['repasses_no_periodo_custeio'])
    rows[LINHA_CUSTEIO][COL_RECEITAS_DEVOLUCAO].value = formata_valor(info['receitas_devolucao_no_periodo_custeio'])
    rows[LINHA_CUSTEIO][COL_DEMAIS_CREDITOS].value = formata_valor(info['demais_creditos_no_periodo_custeio'])
    valor_total_custeio = info['saldo_reprogramado_periodo_anterior_custeio'] + info['repasses_no_periodo_custeio'] +\
        info['receitas_devolucao_no_periodo_custeio'] + info['demais_creditos_no_periodo_custeio']
    rows[LINHA_CUSTEIO][COL_VALOR_TOTAL].value = formata_valor(valor_total_custeio)
    rows[LINHA_CUSTEIO][COL_DESPESA_NO_PERIODO].value = formata_valor(info['despesas_no_periodo_custeio'])
    rows[LINHA_CUSTEIO][COL_SALDO_REPROGRAMADO_PROXIMO].value = formata_valor(valor_total_custeio)

    # LINHA CAPITAL
    rows[LINHA_CAPITAL][COL_SALDO_REPROGRAMADO_ANTERIOR].value = formata_valor(
        info['saldo_reprogramado_periodo_anterior_capital'])
    rows[LINHA_CAPITAL][COL_REPASSES_PREVISTOS].value = formata_valor(info['repasses_previstos_sme_capital'])
    rows[LINHA_CAPITAL][COL_REPASSES_NO_PERIODO].value = formata_valor(info['repasses_no_periodo_capital'])
    rows[LINHA_CAPITAL][COL_RECEITAS_DEVOLUCAO].value = formata_valor(info['receitas_devolucao_no_periodo_capital'])
    rows[LINHA_CAPITAL][COL_DEMAIS_CREDITOS].value = formata_valor(info['demais_creditos_no_periodo_capital'])
    valor_total_capital = info['saldo_reprogramado_periodo_anterior_capital'] + info['repasses_no_periodo_capital'] +\
        info['receitas_devolucao_no_periodo_capital'] + info['demais_creditos_no_periodo_capital']
    rows[LINHA_CAPITAL][COL_VALOR_TOTAL].value = formata_valor(valor_total_capital)
    rows[LINHA_CAPITAL][COL_DESPESA_NO_PERIODO].value = formata_valor(info['despesas_no_periodo_capital'])
    rows[LINHA_CAPITAL][COL_SALDO_REPROGRAMADO_PROXIMO].value = formata_valor(valor_total_capital)

    # LINHA RLA
    rows[LINHA_RLA][COL_SALDO_REPROGRAMADO_ANTERIOR].value = formata_valor(
        info['saldo_reprogramado_periodo_anterior_livre'])
    rows[LINHA_RLA][COL_REPASSES_PREVISTOS].value = formata_valor(info['repasses_previstos_sme_livre'])
    rows[LINHA_RLA][COL_REPASSES_NO_PERIODO].value = formata_valor(info['repasses_no_periodo_livre'])
    rows[LINHA_RLA][COL_RENDIMENTO].value = formata_valor(info['receitas_rendimento_no_periodo_livre'])
    rows[LINHA_RLA][COL_RECEITAS_DEVOLUCAO].value = formata_valor(info['receitas_devolucao_no_periodo_livre'])
    rows[LINHA_RLA][COL_DEMAIS_CREDITOS].value = formata_valor(info['demais_creditos_no_periodo_livre'])
    valor_total_livre = info['saldo_reprogramado_periodo_anterior_livre'] + info['receitas_rendimento_no_periodo_livre'] +\
        info['repasses_no_periodo_livre'] + info['receitas_devolucao_no_periodo_livre'] + \
        info['demais_creditos_no_periodo_livre']
    rows[LINHA_RLA][COL_VALOR_TOTAL].value = formata_valor(valor_total_livre)
    rows[LINHA_RLA][COL_SALDO_REPROGRAMADO_PROXIMO].value = formata_valor(valor_total_livre)

    # LINHA TOTAIS
    rows[LINHA_TOTAL][COL_SALDO_REPROGRAMADO_ANTERIOR].value = formata_valor(
        info['saldo_reprogramado_periodo_anterior_total'])
    rows[LINHA_TOTAL][COL_REPASSES_PREVISTOS].value = formata_valor(info['repasses_previstos_sme_total'])
    rows[LINHA_TOTAL][COL_REPASSES_NO_PERIODO].value = formata_valor(info['repasses_no_periodo_total'])
    rows[LINHA_TOTAL][COL_RENDIMENTO].value = formata_valor(info['receitas_rendimento_no_periodo_livre'])
    rows[LINHA_TOTAL][COL_RECEITAS_DEVOLUCAO].value = formata_valor(info['receitas_devolucao_no_periodo_total'])
    rows[LINHA_TOTAL][COL_DEMAIS_CREDITOS].value = formata_valor(info['demais_creditos_no_periodo_total'])
    valor_total = info['saldo_reprogramado_periodo_anterior_total'] + info['receitas_rendimento_no_periodo_livre'] +\
        info['repasses_no_periodo_total'] + info['receitas_devolucao_no_periodo_total'] + \
        info['demais_creditos_no_periodo_total']
    rows[LINHA_TOTAL][COL_VALOR_TOTAL].value = formata_valor(valor_total)
    rows[LINHA_TOTAL][COL_DESPESA_NO_PERIODO].value = formata_valor(info['despesas_no_periodo_total'])
    rows[LINHA_TOTAL][COL_SALDO_REPROGRAMADO_PROXIMO].value = formata_valor(valor_total)

    rows[LINHA_TOTAL][COL_DEVOLUCAO_TESOURO].value = formata_valor(info['devolucoes_ao_tesouro_no_periodo_total'])

    # Justificativa
    justificativa = JustificativaRelatorioConsolidadoDRE.objects.first()
    rows[LINHA_JUSTIFICATIVA][0].value = justificativa.texto if justificativa else ''


def execucao_fisica(worksheet, dre, periodo):
    """BLOCO 3 - EXECUÇÃO FÍSICA"""
    rows = list(worksheet.rows)

    rows[LINHA_EXECUCAO_FISICA][0].value = dre.unidades_da_dre.count()
    quantidade_ues_cnpj = Associacao.objects.filter(unidade__dre=dre).exclude(cnpj__exact='').count()
    rows[LINHA_EXECUCAO_FISICA][2].value = quantidade_ues_cnpj

    #TODO Implementar contagem de regulares considerando o ano
    quantidade_regular = Associacao.objects.filter(unidade__dre=dre).exclude(cnpj__exact='').count()

    rows[LINHA_EXECUCAO_FISICA][4].value = quantidade_regular

    cards = PrestacaoConta.dashboard(periodo.uuid, dre.uuid, add_aprovado_ressalva=True)

    quantidade_aprovada = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'APROVADA'][0]
    quantidade_aprovada_ressalva = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'APROVADA_RESSALVA'][0]
    quantidade_nao_aprovada = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'REPROVADA'][0]
    quantidade_nao_recebida = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'NAO_RECEBIDA'][0]
    quantidade_recebida = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'RECEBIDA'][0]
    quantidade_em_analise = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'RECEBIDA'][0]

    rows[LINHA_EXECUCAO_FISICA][6].value = quantidade_aprovada
    rows[LINHA_EXECUCAO_FISICA][7].value = quantidade_aprovada_ressalva
    quantidade_nao_apresentada = quantidade_ues_cnpj - quantidade_aprovada - quantidade_aprovada_ressalva -\
        quantidade_nao_aprovada - quantidade_nao_recebida - quantidade_recebida - quantidade_em_analise
    rows[LINHA_EXECUCAO_FISICA][8].value = quantidade_nao_apresentada
    rows[LINHA_EXECUCAO_FISICA][9].value = quantidade_nao_aprovada
    quantidade_devida = quantidade_nao_apresentada + quantidade_nao_aprovada
    rows[LINHA_EXECUCAO_FISICA][10].value = quantidade_devida
    rows[LINHA_EXECUCAO_FISICA][11].value = quantidade_aprovada + quantidade_devida


def associacoes_nao_regularizadas(worksheet, associacoes_pendetes, acc=0, start_line=29):
    quantidade = acc
    last_line = LAST_LINE + quantidade
    ind = start_line

    for linha, associacao in enumerate(associacoes_pendetes):
        # Movendo as linhas para baixo antes de inserir os dados novos
        ind = start_line + quantidade + linha
        if linha > 0:
            for row_idx in range(last_line + linha, ind - 2, -1):
                copy_row(worksheet, row_idx, 1, copy_data=True)

        rows = list(worksheet.rows)
        row = rows[ind - 1]
        row[0].value = linha + 1
        row[1].value = associacao.nome


def dados_fisicos_financeiros(worksheet, dre, periodo, tipo_conta, acc=0, start_line=34):
    """Dados Físicos financeiros do bloco 4."""
    quantidade = acc
    last_line = LAST_LINE + quantidade
    ind = start_line + quantidade
    lin = ind

    last = last_line + 1
    start = 35 + quantidade

    total_saldo_reprogramado_anterior_custeio = 0
    total_repasse_custeio = 0
    total_devolucao_custeio = 0
    total_demais_creditos_custeio = 0
    total_despesas_custeio = 0
    total_saldo_custeio = 0

    total_saldo_reprogramado_anterior_capital = 0
    total_repasse_capital = 0
    total_devolucao_capital = 0
    total_demais_creditos_capital = 0
    total_despesas_capital = 0
    total_saldo_capital = 0

    total_saldo_reprogramado_anterior_livre = 0
    total_repasse_livre = 0
    total_receita_rendimento_livre = 0
    total_devolucao_livre = 0
    total_demais_creditos_livre = 0
    total_saldo_livre = 0

    informacao_unidades = informacoes_execucao_financeira_unidades(dre, periodo, tipo_conta)
    for linha, info in enumerate(informacao_unidades):
        if linha > 0:
            for i in range(3):
                for inx in range(last, start, -1):
                    copy_row_direct(worksheet, inx, inx+1, copy_data=True)
                last += 1
                start += 1

            for x in range(ind, ind+3):
               copy_row_direct(worksheet, x, x+3, copy_data=True)
            ind += 3

        saldo_custeio = 0
        saldo_capital = 0
        saldo_livre = 0

        for index in range(3):
            if index == 0:
                rows = list(worksheet.rows)
                row = rows[lin - 1]
                saldo_reprogramado_anterior_custeio = info.get("valores").get(
                    'saldo_reprogramado_periodo_anterior_custeio')
                repasse_custeio = info.get("valores").get('repasses_no_periodo_custeio')
                devolucao_custeio = info.get("valores").get('receitas_devolucao_no_periodo_custeio')
                demais_creditos_custeio = info.get("valores").get('demais_creditos_no_periodo_custeio')
                despesas_custeio = info.get("valores").get('despesas_no_periodo_custeio')
                saldo_custeio = info.get("valores").get('saldo_reprogramado_proximo_periodo_custeio')

                row[3].value = formata_valor(saldo_reprogramado_anterior_custeio)
                row[4].value = formata_valor(repasse_custeio)
                row[6].value = formata_valor(devolucao_custeio)
                row[7].value = formata_valor(demais_creditos_custeio)
                row[8].value = formata_valor(despesas_custeio)
                row[9].value = formata_valor(saldo_custeio)

                total_saldo_reprogramado_anterior_custeio += saldo_reprogramado_anterior_custeio
                total_repasse_custeio += repasse_custeio
                total_devolucao_custeio += devolucao_custeio
                total_demais_creditos_custeio += demais_creditos_custeio
                total_despesas_custeio += despesas_custeio
                total_saldo_custeio += saldo_custeio
            elif index == 1:
                row = rows[lin - 1]
                saldo_reprogramado_anterior_capital = info.get("valores").get(
                    'saldo_reprogramado_periodo_anterior_capital')
                repasse_capital = info.get("valores").get('repasses_no_periodo_capital')
                devolucao_capital = info.get("valores").get('receitas_devolucao_no_periodo_capital')
                demais_creditos_capital = info.get("valores").get('demais_creditos_no_periodo_capital')
                despesas_capital = info.get("valores").get('despesas_no_periodo_capital')
                saldo_capital = info.get("valores").get('saldo_reprogramado_proximo_periodo_capital')

                row[0].value = linha + 1
                row[1].value = info["unidade"]["nome"]
                row[3].value = formata_valor(saldo_reprogramado_anterior_capital)
                row[4].value = formata_valor(repasse_capital)
                row[6].value = formata_valor(devolucao_capital)
                row[7].value = formata_valor(demais_creditos_capital)
                row[8].value = formata_valor(despesas_capital)
                row[9].value = formata_valor(saldo_capital)

                total_saldo_reprogramado_anterior_capital += saldo_reprogramado_anterior_capital
                total_repasse_capital += repasse_capital
                total_devolucao_capital += devolucao_capital
                total_demais_creditos_capital += demais_creditos_capital
                total_despesas_capital += despesas_capital
                total_saldo_capital += saldo_capital
            else:
                rows = list(worksheet.rows)
                row = rows[lin - 1]

                saldo_reprogramado_anterior_livre = info.get("valores").get('saldo_reprogramado_periodo_anterior_livre')
                repasse_livre = info.get("valores").get('repasses_no_periodo_livre')
                receita_rendimento_livre = info.get("valores").get('receitas_rendimento_no_periodo_livre')
                devolucao_livre = info.get("valores").get('receitas_devolucao_no_periodo_livre')
                demais_creditos_livre = info.get("valores").get('demais_creditos_no_periodo_livre')
                saldo_livre = info.get("valores").get('saldo_reprogramado_proximo_periodo_livre')

                row[3].value = formata_valor(saldo_reprogramado_anterior_livre)
                row[4].value = formata_valor(repasse_livre)
                row[5].value = formata_valor(receita_rendimento_livre)
                row[6].value = formata_valor(devolucao_livre)
                row[7].value = formata_valor(demais_creditos_livre)
                row[9].value = formata_valor(saldo_livre)

                # total_saldo_reprogramado_anterior_custeio += saldo_reprogramado_anterior_livre
                total_saldo_reprogramado_anterior_livre += saldo_reprogramado_anterior_livre

                total_repasse_custeio += repasse_livre
                total_receita_rendimento_livre += receita_rendimento_livre
                total_devolucao_custeio += devolucao_livre

                #total_demais_creditos_custeio += demais_creditos_livre
                total_demais_creditos_livre += demais_creditos_livre

                # total_saldo_custeio += saldo_livre
                total_saldo_livre += saldo_livre
            lin += 1

    rows = list(worksheet.rows)
    row = rows[lin - 1]
    row[3].value = formata_valor(total_saldo_reprogramado_anterior_custeio)
    row[4].value = formata_valor(total_repasse_custeio)
    row[6].value = formata_valor(total_devolucao_custeio)
    row[7].value = formata_valor(total_demais_creditos_custeio)
    row[8].value = formata_valor(total_despesas_custeio)
    row[9].value = formata_valor(total_saldo_custeio)

    row = rows[lin]
    row[3].value = formata_valor(total_saldo_reprogramado_anterior_capital)
    row[4].value = formata_valor(total_repasse_capital)
    row[6].value = formata_valor(total_devolucao_capital)
    row[7].value = formata_valor(total_demais_creditos_capital)
    row[8].value = formata_valor(total_despesas_capital)
    row[9].value = formata_valor(total_saldo_capital)

    row = rows[lin + 1]
    row[3].value = formata_valor(total_saldo_reprogramado_anterior_livre)
    row[4].value = formata_valor(total_repasse_livre)
    row[5].value = formata_valor(total_receita_rendimento_livre)
    row[6].value = formata_valor(total_devolucao_livre)
    row[7].value = formata_valor(total_demais_creditos_livre)
    row[9].value = formata_valor(total_saldo_livre)

    devolucoes_ao_tesouro = informacoes_devolucoes_ao_tesouro(dre, periodo, tipo_conta)
    for linha, devolucao in enumerate(devolucoes_ao_tesouro):
        ind = lin + 6
        if linha > 0:
            for row_idx in range(last + linha, ind - 2, -1):
                copy_row(worksheet, row_idx, 1, copy_data=True)
            last += 1

        rows = list(worksheet.rows)

        row = rows[ind - 1]
        row[0].value = devolucao['tipo_nome']
        row[0].value = devolucao['tipo_nome']
        row[2].value = devolucao['ocorrencias']
        row[4].value = formata_valor(devolucao['valor'])
        row[6].value = devolucao['observacao']
        lin += 1

    for linha, info_devolucao in enumerate(informacoes_devolucoes_a_conta_ptrf(dre, periodo, tipo_conta)):
        ind = lin + (8 if devolucoes_ao_tesouro else 9)
        if linha > 0:
            for row_idx in range(last + linha, ind - 2, -1):
                copy_row(worksheet, row_idx, 1, copy_data=True)

        rows = list(worksheet.rows)
        row = rows[ind-1]
        row[0].value = info_devolucao['tipo_nome']
        row[2].value = info_devolucao['ocorrencias']
        row[4].value = formata_valor(info_devolucao['valor'])
        row[6].value = info_devolucao['observacao']
        lin += 1


def data_geracao_documento(worksheet, parcial=False):
    rows = list(worksheet.rows)
    data_geracao = date.today().strftime("%d/%m/%Y")
    texto = f"Documento parcial gerado em: {data_geracao}" if parcial else f"Documento final gerado em: {data_geracao}"
    rows[LAST_LINE][0].value = texto


def formata_valor(valor):
    from babel.numbers import format_currency
    sinal, valor_formatado = format_currency(valor, 'BRL', locale='pt_BR').split('\xa0')
    sinal = '-' if '-' in sinal else ''
    return f'{sinal}{valor_formatado}'

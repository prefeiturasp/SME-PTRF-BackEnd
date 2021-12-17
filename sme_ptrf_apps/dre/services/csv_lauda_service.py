import csv
import logging
from django.core.files import File
from tempfile import NamedTemporaryFile
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from .relatorio_consolidado_service import (
    informacoes_execucao_financeira_unidades
)

logger = logging.getLogger(__name__)


def gerar_csv(dre, periodo, tipo_conta, obj_arquivo_download, parcial=False):
    logger.info("csv lauda em processamento...")
    with NamedTemporaryFile(mode="r+", newline='', encoding='utf-8') as tmp:
        w = csv.writer(tmp.file)

        cabecalho = ["Ordem", "Cód. EOL", "Unidade",
                     "Receita - Custeio", "Receita - Livre Aplic.", "Receita - Capital",
                     "Despesa - Custeio", "Despesa - Capital",
                     "Saldo - Custeio", "Saldo - Livre Aplic.", "Saldo - Capital",
                     "Resultado da análise"]
        w.writerow(cabecalho)

        dados = gerar_dados_lauda(dre, periodo, tipo_conta)
        for dado in dados:
            linha = [dado["ordem"], dado["codigo_eol"], dado["unidade"],
                     dado["receita"]["custeio"], dado["receita"]["livre_aplicacao"], dado["receita"]["capital"],
                     dado["despesa"]["custeio"], dado["despesa"]["capital"],
                     dado["saldo"]["custeio"], dado["saldo"]["livre_aplicacao"], dado["saldo"]["capital"],
                     dado["status_prestacao_contas"]]
            w.writerow(linha)

        tmp.seek(0)
        try:
            obj_arquivo_download.arquivo.save(name=obj_arquivo_download.identificador, content=File(tmp))
            obj_arquivo_download.status = ArquivoDownload.STATUS_CONCLUIDO
            obj_arquivo_download.save()
        except Exception as e:
            obj_arquivo_download.status = ArquivoDownload.STATUS_ERRO
            obj_arquivo_download.msg_erro = str(e)
            obj_arquivo_download.save()


def gerar_dados_lauda(dre, periodo, tipo_conta):
    lista = []
    ordem = 1
    informacao_unidades = informacoes_execucao_financeira_unidades(dre, periodo, tipo_conta)
    for linha, info in enumerate(informacao_unidades):
        if pc_em_analise(info["status_prestacao_contas"]):
            continue

        saldo_custeio = formata_valor(0)
        saldo_capital = formata_valor(0)
        saldo_livre = formata_valor(0)

        unidade = info["unidade"]["tipo_unidade"] + " " + info["unidade"]["nome"]

        dado = {
            "ordem": ordem,
            "codigo_eol": str(info["unidade"]["codigo_eol"]),
            "unidade": str(unidade),
            "receita": {
                "custeio": formata_valor(0),
                "capital": formata_valor(0),
                "livre_aplicacao": formata_valor(0)
            },
            "despesa": {
                "custeio": formata_valor(0),
                "capital": formata_valor(0),
            },
            "saldo": {
                "custeio": formata_valor(0),
                "capital": formata_valor(0),
                "livre_aplicacao": formata_valor(0)
            },
            "status_prestacao_contas": formata_resultado_analise(info["status_prestacao_contas"])
        }

        for index in range(3):
            if index == 0:
                # CUSTEIO

                # Receita
                repasse_custeio = info.get("valores").get('repasses_no_periodo_custeio')
                devolucao_custeio = info.get("valores").get('receitas_devolucao_no_periodo_custeio')
                demais_creditos_custeio = info.get("valores").get('demais_creditos_no_periodo_custeio')

                dado["receita"]["custeio"] = formata_valor(repasse_custeio + devolucao_custeio + demais_creditos_custeio)

                # Despesa
                despesas_custeio = info.get("valores").get('despesas_no_periodo_custeio')

                dado["despesa"]["custeio"] = formata_valor(despesas_custeio)

                # Saldo
                saldo_reprogramado_anterior_custeio = info.get("valores").get(
                    'saldo_reprogramado_periodo_anterior_custeio')
                saldo_custeio = saldo_reprogramado_anterior_custeio + repasse_custeio + devolucao_custeio + \
                                demais_creditos_custeio + despesas_custeio

                dado["saldo"]["custeio"] = formata_valor(saldo_custeio)
            elif index == 1:
                # CAPITAL

                # Receita
                repasse_capital = info.get("valores").get('repasses_no_periodo_capital')
                devolucao_capital = info.get("valores").get('receitas_devolucao_no_periodo_capital')
                demais_creditos_capital = info.get("valores").get('demais_creditos_no_periodo_capital')

                dado["receita"]["capital"] = formata_valor(repasse_capital + devolucao_capital + demais_creditos_capital)

                # Despesa
                despesas_capital = info.get("valores").get('despesas_no_periodo_capital')
                dado["despesa"]["capital"] = formata_valor(despesas_capital)

                # Saldo
                saldo_reprogramado_anterior_capital = info.get("valores").get(
                    'saldo_reprogramado_periodo_anterior_capital')
                saldo_capital = saldo_reprogramado_anterior_capital + repasse_capital + devolucao_capital + \
                                demais_creditos_capital + despesas_capital

                dado["saldo"]["capital"] = formata_valor(saldo_capital)
            else:
                # LIVRE APLICACAO

                # Receita
                repasse_livre = info.get("valores").get('repasses_no_periodo_livre')
                receita_rendimento_livre = info.get("valores").get('receitas_rendimento_no_periodo_livre')
                devolucao_livre = info.get("valores").get('receitas_devolucao_no_periodo_livre')
                demais_creditos_livre = info.get("valores").get('demais_creditos_no_periodo_livre')

                dado["receita"]["livre_aplicacao"] = formata_valor(repasse_livre + receita_rendimento_livre + devolucao_livre + \
                                                     demais_creditos_livre)

                # Saldo
                saldo_reprogramado_anterior_livre = info.get("valores").get('saldo_reprogramado_periodo_anterior_livre')
                saldo_livre = saldo_reprogramado_anterior_livre + repasse_livre + devolucao_livre + \
                              demais_creditos_livre + receita_rendimento_livre

                dado["saldo"]["livre_aplicacao"] = formata_valor(saldo_livre)

        lista.append(dado)
        ordem = ordem + 1

    return lista


def formata_valor(valor):
    from babel.numbers import format_currency
    sinal, valor_formatado = format_currency(valor, 'BRL', locale='pt_BR').split('\xa0')
    sinal = '-' if '-' in sinal else ''
    return f'{sinal}{valor_formatado}'


def formata_resultado_analise(resultado):
    if resultado == "APROVADA_RESSALVA":
        return "Aprovada com ressalvas"
    elif resultado == "APROVADA":
        return "Aprovada"
    elif resultado == "NAO_APRESENTADA" or resultado == "REPROVADA":
        return "Rejeitada"

    return resultado


def pc_em_analise(resultado):
    if resultado == "DEVOLVIDA":
        return True

    if resultado == "DEVOLVIDA_RECEBIDA":
        return True

    if resultado == "DEVOLVIDA_RETORNADA":
        return True

    if resultado == "EM_ANALISE":
        return True

    if resultado == "EM_PROCESSAMENTO":
        return True

    return False

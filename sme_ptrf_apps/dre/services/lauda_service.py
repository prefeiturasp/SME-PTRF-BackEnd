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


def gerar_arquivo_lauda_txt_consolidado_dre(lauda, dre, periodo, tipo_conta, ata, nome_dre, nome_conta,  parcial, apenas_nao_publicadas=False):
    logger.info("Arquivo Lauda txt em processamento.")

    with NamedTemporaryFile(mode="r+", newline='', encoding='utf-8', prefix='lauda', suffix='.docx.txt') as tmp:
        dados = gerar_dados_lauda(dre, periodo, tipo_conta, apenas_nao_publicadas)
        status_separados = separa_status(dados)
        linhas = []

        eh_parcial = "Parcial" if parcial['parcial'] else "Final"

        sequencia_de_publicacao = parcial['sequencia_de_publicacao_atual']

        if eh_parcial == "Parcial":
            titulo_sequencia_publicacao = f'Parcial #{sequencia_de_publicacao}'
        else:
            titulo_sequencia_publicacao = "Lauda final"

        titulo = f"((TITULO))DIRETORIA REGIONAL DE EDUCAÇÃO - {formata_nome_dre(dre)} " \
                 f"PROGRAMA DE TRANSFERÊNCIA DE RECURSOS FINANCEIROS PTRF - {titulo_sequencia_publicacao} \n\n"

        texto = f"((TEXTO)) No exercício da atribuição a mim conferida pela Portaria SME nº 5.318/2020, torno " \
                f"público o Parecer Técnico Conclusivo da Comissão de Prestação de Contas do PTRF da DRE " \
                f"{formata_nome_dre(dre, capitalize=True)}, expedido através da ata nº {formata_numero_ata(ata)}, " \
                f"relativo à prestação de contas do Programa de Transferência de Recursos Financeiros - PTRF " \
                f"- {formata_nome_tipo_conta(tipo_conta, upper=True)} - {formata_periodo_repasse(ata)}:\n\n"

        linhas.append(titulo)
        linhas.append(texto)

        if len(status_separados["aprovadas"]) > 0:
            # Atenção para não mudar a formatação da string
            ng_aprovadas = "((NG)) Prestações de contas aprovadas((CL))\n" \
                           "			RECEITA			DESPESAS		SALDO	\n" \
                           "ORDEM	CÓD EOL	UNIDADE	" \
                           "CUSTEIO	LIVRE APLIC.	CAPITAL	" \
                           "CUSTEIO	CAPITAL	" \
                           "CUSTEIO	LIVRE APLIC.	CAPITAL\n"

            linhas.append(ng_aprovadas)

            for status in status_separados["aprovadas"]:
                # Atenção para não mudar a formatação da string
                linha = f"{status['ordem']}	{status['codigo_eol']}	{status['unidade']}	" \
                        f"{status['receita']['custeio']}	{status['receita']['livre_aplicacao']}	{status['receita']['capital']}	" \
                        f"{status['despesa']['custeio']}	{status['despesa']['capital']}	" \
                        f"{status['saldo']['custeio']}	{status['saldo']['livre_aplicacao']}	{status['saldo']['capital']}\n"
                linhas.append(linha)

            linhas.append("\n")

        if len(status_separados["aprovadas_ressalva"]) > 0:
            # Atenção para não mudar a formatação da string
            ng_aprovadas_ressalva = "((NG)) Prestações de contas aprovadas com ressalva((CL))\n" \
                                    "			RECEITA			DESPESAS		SALDO	\n" \
                                    "ORDEM	CÓD EOL	UNIDADE	" \
                                    "CUSTEIO	LIVRE APLIC.	CAPITAL	" \
                                    "CUSTEIO	CAPITAL	" \
                                    "CUSTEIO	LIVRE APLIC.	CAPITAL\n"

            linhas.append(ng_aprovadas_ressalva)

            for status in status_separados["aprovadas_ressalva"]:
                # Atenção para não mudar a formatação da string
                linha = f"{status['ordem']}	{status['codigo_eol']}	{status['unidade']}	" \
                        f"{status['receita']['custeio']}	{status['receita']['livre_aplicacao']}	{status['receita']['capital']}	" \
                        f"{status['despesa']['custeio']}	{status['despesa']['capital']}	" \
                        f"{status['saldo']['custeio']}	{status['saldo']['livre_aplicacao']}	{status['saldo']['capital']}\n"
                linhas.append(linha)

            linhas.append("\n")

        if len(status_separados["rejeitadas"]) > 0:
            # Atenção para não mudar a formatação da string
            ng_rejeitadas = "((NG)) Prestações de contas rejeitadas((CL))\n" \
                            "			RECEITA			DESPESAS		SALDO	\n" \
                            "ORDEM	CÓD EOL	UNIDADE	" \
                            "CUSTEIO	LIVRE APLIC.	CAPITAL	" \
                            "CUSTEIO	CAPITAL	" \
                            "CUSTEIO	LIVRE APLIC.	CAPITAL\n"

            linhas.append(ng_rejeitadas)

            for status in status_separados["rejeitadas"]:
                # Atenção para não mudar a formatação da string
                linha = f"{status['ordem']}	{status['codigo_eol']}	{status['unidade']}	" \
                        f"{status['receita']['custeio']}	{status['receita']['livre_aplicacao']}	{status['receita']['capital']}	" \
                        f"{status['despesa']['custeio']}	{status['despesa']['capital']}	" \
                        f"{status['saldo']['custeio']}	{status['saldo']['livre_aplicacao']}	{status['saldo']['capital']}\n"
                linhas.append(linha)

        tmp.file.writelines(linhas)

        tmp.seek(0)

        try:
            nome_lauda = f"Lauda_{nome_dre}_{nome_conta}.docx.txt"
            lauda.arquivo_lauda_txt.save(name=f'{nome_lauda}', content=File(tmp))
            eh_parcial = parcial['parcial']
            lauda.passar_para_status_gerado(eh_parcial)
        except Exception as err:
            logger.error("Erro ao gerar arquivo txt lauda: %s", str(err))
            raise Exception(err)


def gerar_txt(dre, periodo, tipo_conta, obj_arquivo_download, ata, parcial=False):
    logger.info("txt lauda em processamento.")

    with NamedTemporaryFile(mode="r+", newline='', encoding='utf-8', prefix='lauda', suffix='.docx.txt') as tmp:
        dados = gerar_dados_lauda(dre, periodo, tipo_conta)
        status_separados = separa_status(dados)
        linhas = []

        titulo = f"((TITULO))DIRETORIA REGIONAL DE EDUCAÇÃO - {formata_nome_dre(dre)} " \
                 f"PROGRAMA DE TRANSFERÊNCIA DE RECURSOS FINANCEIROS PTRF \n\n"

        texto = f"((TEXTO)) No exercício da atribuição a mim conferida pela Portaria SME nº 5.318/2020, torno " \
                f"público o Parecer Técnico Conclusivo da Comissão de Prestação de Contas do PTRF da DRE " \
                f"{formata_nome_dre(dre, capitalize=True)}, expedido através da ata nº {formata_numero_ata(ata)}, " \
                f"relativo à prestação de contas do Programa de Transferência de Recursos Financeiros - PTRF " \
                f"- {formata_nome_tipo_conta(tipo_conta, upper=True)} - {formata_periodo_repasse(ata)}:\n\n"

        linhas.append(titulo)
        linhas.append(texto)

        if len(status_separados["aprovadas"]) > 0:
            # Atenção para não mudar a formatação da string
            ng_aprovadas = "((NG)) Prestações de contas aprovadas((CL))\n" \
                           "			RECEITA			DESPESAS		SALDO	\n" \
                           "ORDEM	CÓD EOL	UNIDADE	" \
                           "CUSTEIO	LIVRE APLIC.	CAPITAL	" \
                           "CUSTEIO	CAPITAL	" \
                           "CUSTEIO	LIVRE APLIC.	CAPITAL\n"

            linhas.append(ng_aprovadas)

            for status in status_separados["aprovadas"]:
                # Atenção para não mudar a formatação da string
                linha = f"{status['ordem']}	{status['codigo_eol']}	{status['unidade']}	" \
                        f"{status['receita']['custeio']}	{status['receita']['livre_aplicacao']}	{status['receita']['capital']}	" \
                        f"{status['despesa']['custeio']}	{status['despesa']['capital']}	" \
                        f"{status['saldo']['custeio']}	{status['saldo']['livre_aplicacao']}	{status['saldo']['capital']}\n"
                linhas.append(linha)

            linhas.append("\n")

        if len(status_separados["aprovadas_ressalva"]) > 0:
            # Atenção para não mudar a formatação da string
            ng_aprovadas_ressalva = "((NG)) Prestações de contas aprovadas com ressalva((CL))\n" \
                                    "			RECEITA			DESPESAS		SALDO	\n" \
                                    "ORDEM	CÓD EOL	UNIDADE	" \
                                    "CUSTEIO	LIVRE APLIC.	CAPITAL	" \
                                    "CUSTEIO	CAPITAL	" \
                                    "CUSTEIO	LIVRE APLIC.	CAPITAL\n"

            linhas.append(ng_aprovadas_ressalva)

            for status in status_separados["aprovadas_ressalva"]:
                # Atenção para não mudar a formatação da string
                linha = f"{status['ordem']}	{status['codigo_eol']}	{status['unidade']}	" \
                        f"{status['receita']['custeio']}	{status['receita']['livre_aplicacao']}	{status['receita']['capital']}	" \
                        f"{status['despesa']['custeio']}	{status['despesa']['capital']}	" \
                        f"{status['saldo']['custeio']}	{status['saldo']['livre_aplicacao']}	{status['saldo']['capital']}\n"
                linhas.append(linha)

            linhas.append("\n")

        if len(status_separados["rejeitadas"]) > 0:
            # Atenção para não mudar a formatação da string
            ng_rejeitadas = "((NG)) Prestações de contas rejeitadas((CL))\n" \
                            "			RECEITA			DESPESAS		SALDO	\n" \
                            "ORDEM	CÓD EOL	UNIDADE	" \
                            "CUSTEIO	LIVRE APLIC.	CAPITAL	" \
                            "CUSTEIO	CAPITAL	" \
                            "CUSTEIO	LIVRE APLIC.	CAPITAL\n"

            linhas.append(ng_rejeitadas)

            for status in status_separados["rejeitadas"]:
                # Atenção para não mudar a formatação da string
                linha = f"{status['ordem']}	{status['codigo_eol']}	{status['unidade']}	" \
                        f"{status['receita']['custeio']}	{status['receita']['livre_aplicacao']}	{status['receita']['capital']}	" \
                        f"{status['despesa']['custeio']}	{status['despesa']['capital']}	" \
                        f"{status['saldo']['custeio']}	{status['saldo']['livre_aplicacao']}	{status['saldo']['capital']}\n"
                linhas.append(linha)

        tmp.file.writelines(linhas)

        tmp.seek(0)

        try:
            obj_arquivo_download.arquivo.save(name=obj_arquivo_download.identificador, content=File(tmp))
            obj_arquivo_download.status = ArquivoDownload.STATUS_CONCLUIDO
            obj_arquivo_download.save()
        except Exception as e:
            obj_arquivo_download.status = ArquivoDownload.STATUS_ERRO
            obj_arquivo_download.msg_erro = str(e)
            obj_arquivo_download.save()


def gerar_dados_lauda(dre, periodo, tipo_conta, apenas_nao_publicadas):
    lista = []
    ordem_aprovadas = 0
    ordem_aprovadas_ressalva = 0
    ordem_rejeitadas = 0
    informacao_unidades = informacoes_execucao_financeira_unidades(dre, periodo, tipo_conta, apenas_nao_publicadas)
    for linha, info in enumerate(informacao_unidades):
        if pc_em_analise(info["status_prestacao_contas"]):
            continue

        unidade = info["unidade"]["tipo_unidade"] + " " + info["unidade"]["nome"]

        dado = {
            "ordem": None,
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

        if info["status_prestacao_contas"] == "APROVADA":
            ordem_aprovadas = ordem_aprovadas + 1
            dado["ordem"] = ordem_aprovadas
        elif info["status_prestacao_contas"] == "APROVADA_RESSALVA":
            ordem_aprovadas_ressalva = ordem_aprovadas_ressalva + 1
            dado["ordem"] = ordem_aprovadas_ressalva
        elif info["status_prestacao_contas"] == "NAO_APRESENTADA" or info["status_prestacao_contas"] == "REPROVADA":
            ordem_rejeitadas = ordem_rejeitadas + 1
            dado["ordem"] = ordem_rejeitadas

        for index in range(3):
            if index == 0:
                # CUSTEIO

                # Receita
                repasse_custeio = info.get("valores").get('repasses_no_periodo_custeio')
                dado["receita"]["custeio"] = formata_valor(repasse_custeio)

                # Despesa
                despesas_custeio = info.get("valores").get('despesas_no_periodo_custeio')
                dado["despesa"]["custeio"] = formata_valor(despesas_custeio)

                # Saldo
                saldo_reprogramado_proximo_periodo_custeio = info.get("valores").get(
                    'saldo_reprogramado_proximo_periodo_custeio')
                dado["saldo"]["custeio"] = formata_valor(saldo_reprogramado_proximo_periodo_custeio)
            elif index == 1:
                # CAPITAL

                # Receita
                repasse_capital = info.get("valores").get('repasses_no_periodo_capital')
                dado["receita"]["capital"] = formata_valor(repasse_capital)

                # Despesa
                despesas_capital = info.get("valores").get('despesas_no_periodo_capital')
                dado["despesa"]["capital"] = formata_valor(despesas_capital)

                # Saldo
                saldo_reprogramado_proximo_periodo_capital = info.get("valores").get(
                    'saldo_reprogramado_proximo_periodo_capital')
                dado["saldo"]["capital"] = formata_valor(saldo_reprogramado_proximo_periodo_capital)
            else:
                # LIVRE APLICACAO

                # Receita
                repasse_livre = info.get("valores").get('repasses_no_periodo_livre')
                dado["receita"]["livre_aplicacao"] = formata_valor(repasse_livre)

                # Despesa
                # Despesa não possui livre aplicação

                # Saldo
                saldo_reprogramado_proximo_periodo_livre = info.get("valores").get(
                    'saldo_reprogramado_proximo_periodo_livre')
                dado["saldo"]["livre_aplicacao"] = formata_valor(saldo_reprogramado_proximo_periodo_livre)

        lista.append(dado)

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


def formata_nome_tipo_conta(tipo_conta, upper=False, capitalize=False):
    nome_conta = tipo_conta.nome

    if upper:
        nome_conta = nome_conta.upper()

    if capitalize:
        nome_conta = nome_conta.capitalize()

    return nome_conta


def formata_nome_dre(dre, capitalize=False):
    nome_dre = dre.nome.upper()
    if "DIRETORIA REGIONAL DE EDUCACAO" in nome_dre:
        nome_dre = nome_dre.replace("DIRETORIA REGIONAL DE EDUCACAO", "")
        nome_dre = nome_dre.strip()

    if capitalize:
        nome_dre = nome_dre.capitalize()

    return nome_dre


def formata_numero_ata(ata):
    numero_ata = ata.numero_ata
    data_reuniao = ata.data_reuniao

    if numero_ata and data_reuniao:
        return f"{numero_ata}/{data_reuniao.strftime('%Y')}"
    return "-"


def formata_periodo_repasse(ata):
    return ata.periodo.referencia_por_extenso


def separa_status(dados):
    lista_aprovadas = []
    lista_aprovadas_ressalva = []
    lista_rejeitadas = []
    for dado in dados:
        if dado['status_prestacao_contas'] == "Aprovada":
            lista_aprovadas.append(dado)
        elif dado['status_prestacao_contas'] == "Aprovada com ressalvas":
            lista_aprovadas_ressalva.append(dado)
        elif dado['status_prestacao_contas'] == "Rejeitada":
            lista_rejeitadas.append(dado)

    status = {
        "aprovadas": lista_aprovadas,
        "aprovadas_ressalva": lista_aprovadas_ressalva,
        "rejeitadas": lista_rejeitadas
    }

    return status

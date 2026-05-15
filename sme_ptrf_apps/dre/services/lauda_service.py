import csv
import logging
from django.core.files import File
from tempfile import NamedTemporaryFile
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.utils.string_to_float import string_to_float
from .relatorio_consolidado_service import (
    informacoes_execucao_financeira_unidades
)
from sme_ptrf_apps.core.models import (
    TipoConta
)

logger = logging.getLogger(__name__)


def _linha_lauda_txt_por_status_com_tipo_conta(status):
    rc, dp, sd = status["receita"], status["despesa"], status["saldo"]
    return (
        f"{status['ordem']}\t{status['codigo_eol']}\t{status['unidade']}\t{status['tipo_conta']}\t"
        f"{rc['custeio']}\t{rc['livre_aplicacao']}\t{rc['capital']}\t"
        f"{dp['custeio']}\t{dp['capital']}\t"
        f"{sd['custeio']}\t{sd['livre_aplicacao']}\t{sd['capital']}\n"
    )


def _linha_lauda_txt_por_status_sem_tipo_conta(status):
    rc, dp, sd = status["receita"], status["despesa"], status["saldo"]
    return (
        f"{status['ordem']}\t{status['codigo_eol']}\t{status['unidade']}\t"
        f"{rc['custeio']}\t{rc['livre_aplicacao']}\t{rc['capital']}\t"
        f"{dp['custeio']}\t{dp['capital']}\t"
        f"{sd['custeio']}\t{sd['livre_aplicacao']}\t{sd['capital']}\n"
    )


def _consolidado_lauda_esta_sem_movimentacao(status_separados):
    for chave in ("aprovadas", "aprovadas_ressalva", "rejeitadas"):
        for status in status_separados[chave]:
            if not verificar_se_todos_os_valores_da_conta_estao_zerados(status):
                return False
    return True


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


def gerar_arquivo_lauda_txt_consolidado_dre(lauda, dre, periodo, ata, nome_dre, parcial, apenas_nao_publicadas=False):
    """
    Gera apenas o PDF da Lauda vinculado ao consolidado DRE.
    O texto .docx.txt do consolidado não é mais gerado; o código que o produzia foi
    preservado em referencia_legacy_gerar_arquivo_lauda_txt_consolidado_dre (não chamado).
    """
    from sme_ptrf_apps.core.services.lauda_pdf_service import gerar_arquivo_lauda_pdf_consolidado_dre

    eh_retificacao = bool(lauda and lauda.consolidado_dre and lauda.consolidado_dre.eh_retificacao)
    if eh_retificacao:
        logger.info("Lauda PDF (retificação) em processamento.")
    else:
        logger.info("Lauda PDF consolidado DRE em processamento.")

    dados = gerar_dados_lauda(dre, periodo, apenas_nao_publicadas, lauda)
    status_separados = separa_status(dados)
    lauda_vazia = _consolidado_lauda_esta_sem_movimentacao(status_separados)

    try:
        if not lauda_vazia:
            lauda.sem_movimentacao = False
            lauda.save()
            eh_parcial = parcial['parcial']
            lauda.passar_para_status_gerado(eh_parcial)
            gerar_arquivo_lauda_pdf_consolidado_dre(
                lauda,
                dre,
                periodo,
                ata,
                nome_dre,
                parcial,
                apenas_nao_publicadas,
            )
        else:
            logger.info(
                "Os registros das contas bancárias das PCs estão zerados; Lauda PDF não será gerada.",
            )
            lauda.sem_movimentacao = True
            lauda.save()
            eh_parcial = parcial['parcial']
            lauda.passar_para_status_gerado(eh_parcial)
    except Exception as err:
        logger.error("Erro ao gerar lauda consolidada (PDF): %s", str(err))
        raise Exception(err)


def referencia_legacy_gerar_arquivo_lauda_txt_consolidado_dre(
    lauda, dre, periodo, ata, nome_dre, parcial, apenas_nao_publicadas=False
):
    """
    Referência: fluxo antigo que gerava Lauda .docx.txt no consolidado (tags ((TITULO)), etc.).
    Não é invocado pelo sistema — mantido apenas para consulta futura.
    """
    eh_retificacao = True if lauda and lauda.consolidado_dre and lauda.consolidado_dre.eh_retificacao else False

    if eh_retificacao:
        logger.info("Arquivo Lauda txt de uma retificação em processamento.")
    else:
        logger.info("Arquivo Lauda txt em processamento.")

    with NamedTemporaryFile(mode="r+", newline='', encoding='utf-8', prefix='lauda', suffix='.docx.txt') as tmp:
        dados = gerar_dados_lauda(dre, periodo, apenas_nao_publicadas, lauda)
        status_separados = separa_status(dados)
        linhas = []

        eh_parcial = "Parcial" if parcial['parcial'] else "Final"

        sequencia_de_publicacao = parcial['sequencia_de_publicacao_atual']

        if eh_retificacao:
            seq_pub = lauda.consolidado_dre.consolidado_retificado.sequencia_de_publicacao
            titulo_sequencia_publicacao = f'Parcial #{seq_pub} \n'
        elif eh_parcial == "Parcial":
            titulo_sequencia_publicacao = f'Parcial #{sequencia_de_publicacao} \n\n'
        else:
            titulo_sequencia_publicacao = "Lauda final \n\n"

        titulo = f"((TITULO))DIRETORIA REGIONAL DE EDUCAÇÃO - {formata_nome_dre(dre)} \n"

        titulo_continuacao = f"((TITULO))PROGRAMA DE TRANSFERÊNCIA DE RECURSOS FINANCEIROS PTRF" \
                             f" - {titulo_sequencia_publicacao}"

        titulo_retificacao = None
        titulo_retificacao_continuacao = None

        if eh_retificacao:
            doc_pub = formata_data_publicacao(lauda.consolidado_dre)
            pag_pub = lauda.consolidado_dre.consolidado_retificado.pagina_publicacao
            titulo_retificacao = (
                f"((TITULO))RETIFICAÇÃO DA PUBLICAÇÃO DO DOC {doc_pub} "
                f"- PÁGINA {pag_pub} \n"
            )

            titulo_retificacao_continuacao = "((TITULO))LEIA - SE COMO SEGUE E NÃO COMO CONSTOU: \n\n"

        texto = f"((TEXTO)) No exercício da atribuição a mim conferida pela Portaria SME nº 5.318/2020, torno " \
                f"público o Parecer Técnico Conclusivo da Comissão de Prestação de Contas do PTRF da DRE " \
                f"{formata_nome_dre(dre, capitalize=True)}, expedido através da ata nº {formata_numero_ata(ata)}, " \
                f"relativo à prestação de contas do Programa de Transferência de Recursos Financeiros - PTRF " \
                f"- {formata_periodo_repasse(ata)}:\n\n"

        linhas.append(titulo)
        linhas.append(titulo_continuacao)

        if titulo_retificacao and titulo_retificacao_continuacao:
            linhas.append(titulo_retificacao)
            linhas.append(titulo_retificacao_continuacao)

        linhas.append(texto)

        lauda_vazia = True
        if len(status_separados["aprovadas"]) > 0:
            # Atenção para não mudar a formatação da string
            ng_aprovadas = "((NG)) Prestações de contas aprovadas((CL))\n" \
                           "				RECEITA			DESPESAS		SALDO	\n" \
                           "ORDEM	CÓD EOL	UNIDADE	CONTA	" \
                           "CUSTEIO	LIVRE APLIC.	CAPITAL	" \
                           "CUSTEIO	CAPITAL	" \
                           "CUSTEIO	LIVRE APLIC.	CAPITAL\n"

            linhas.append(ng_aprovadas)

            for status in status_separados["aprovadas"]:
                # Atenção para não mudar a formatação da string
                linha = _linha_lauda_txt_por_status_com_tipo_conta(status)

                if not verificar_se_todos_os_valores_da_conta_estao_zerados(status):
                    lauda_vazia = False
                    linhas.append(linha)

            linhas.append("\n")

        if len(status_separados["aprovadas_ressalva"]) > 0:
            # Atenção para não mudar a formatação da string
            ng_aprovadas_ressalva = "((NG)) Prestações de contas aprovadas com ressalva((CL))\n" \
                                    "				RECEITA			DESPESAS		SALDO	\n" \
                                    "ORDEM	CÓD EOL	UNIDADE	CONTA	" \
                                    "CUSTEIO	LIVRE APLIC.	CAPITAL	" \
                                    "CUSTEIO	CAPITAL	" \
                                    "CUSTEIO	LIVRE APLIC.	CAPITAL\n"

            linhas.append(ng_aprovadas_ressalva)

            for status in status_separados["aprovadas_ressalva"]:
                # Atenção para não mudar a formatação da string
                linha = _linha_lauda_txt_por_status_com_tipo_conta(status)

                if not verificar_se_todos_os_valores_da_conta_estao_zerados(status):
                    lauda_vazia = False
                    linhas.append(linha)

            linhas.append("\n")

        if len(status_separados["rejeitadas"]) > 0:
            # Atenção para não mudar a formatação da string
            ng_rejeitadas = "((NG)) Prestações de contas rejeitadas((CL))\n" \
                            "				RECEITA			DESPESAS		SALDO	\n" \
                            "ORDEM	CÓD EOL	UNIDADE	CONTA	" \
                            "CUSTEIO	LIVRE APLIC.	CAPITAL	" \
                            "CUSTEIO	CAPITAL	" \
                            "CUSTEIO	LIVRE APLIC.	CAPITAL\n"

            linhas.append(ng_rejeitadas)

            for status in status_separados["rejeitadas"]:
                # Atenção para não mudar a formatação da string
                linha = _linha_lauda_txt_por_status_com_tipo_conta(status)

                if not verificar_se_todos_os_valores_da_conta_estao_zerados(status):
                    lauda_vazia = False
                    linhas.append(linha)

        tmp.file.writelines(linhas)

        tmp.seek(0)

        if not lauda_vazia:
            nome_lauda = f"Lauda_{nome_dre}.docx.txt"
            lauda.arquivo_lauda_txt.save(name=f'{nome_lauda}', content=File(tmp))
            lauda.sem_movimentacao = False
            lauda.save()
            eh_parcial = parcial['parcial']
            lauda.passar_para_status_gerado(eh_parcial)
        else:
            logger.info(
                "Os registros das contas bancárias das PCs estão zerados, "
                "logo o arquivo txt lauda não foi gerado."
            )
            lauda.sem_movimentacao = True
            lauda.save()
            eh_parcial = parcial['parcial']
            lauda.passar_para_status_gerado(eh_parcial)


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
                linha = _linha_lauda_txt_por_status_sem_tipo_conta(status)
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
                linha = _linha_lauda_txt_por_status_sem_tipo_conta(status)
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
                linha = _linha_lauda_txt_por_status_sem_tipo_conta(status)
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


def gerar_dados_lauda(dre, periodo, apenas_nao_publicadas, lauda):
    eh_retificacao = True if lauda and lauda.consolidado_dre and lauda.consolidado_dre.eh_retificacao else False

    lista = []

    tipo_contas = TipoConta.objects.all().order_by('nome')
    for tipo_conta in tipo_contas:
        informacao_unidades = informacoes_execucao_financeira_unidades(
            dre,
            periodo,
            tipo_conta,
            apenas_nao_publicadas,
            consolidado_dre=lauda.consolidado_dre if eh_retificacao else None
        )

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
                "status_prestacao_contas": formata_resultado_analise(info["status_prestacao_contas"]),
                "tipo_conta": tipo_conta.nome
            }

            for index in range(3):
                if index == 0:
                    # CUSTEIO

                    # Receita
                    saldo_reprogramado_periodo_anterior_custeio = info.get("valores").get(
                        'saldo_reprogramado_periodo_anterior_custeio')
                    receitas_totais_no_periodo_custeio = info.get("valores").get('receitas_totais_no_periodo_custeio')
                    receita_custeio = saldo_reprogramado_periodo_anterior_custeio + receitas_totais_no_periodo_custeio

                    dado["receita"]["custeio"] = formata_valor(receita_custeio)

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
                    saldo_reprogramado_periodo_anterior_capital = info.get("valores").get(
                        'saldo_reprogramado_periodo_anterior_capital')
                    receitas_totais_no_periodo_capital = info.get("valores").get('receitas_totais_no_periodo_capital')
                    receita_capital = saldo_reprogramado_periodo_anterior_capital + receitas_totais_no_periodo_capital

                    dado["receita"]["capital"] = formata_valor(receita_capital)

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
                    saldo_reprogramado_periodo_anterior_livre = info.get("valores").get(
                        'saldo_reprogramado_periodo_anterior_livre')
                    receitas_totais_no_periodo_livre = info.get("valores").get('receitas_totais_no_periodo_livre')
                    receita_livre = saldo_reprogramado_periodo_anterior_livre + receitas_totais_no_periodo_livre

                    dado["receita"]["livre_aplicacao"] = formata_valor(receita_livre)

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


def formata_periodo_referencia_lauda_pdf(ata):
    ref = ata.periodo.referencia
    if not ref:
        return ""
    ano, parte = ref.split(".")
    if parte == "u":
        return f"Período {ano}"
    return f"{parte}° período de {ano}"


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

    lista_aprovadas = calcula_ordem(lista_aprovadas)
    lista_aprovadas_ressalva = calcula_ordem(lista_aprovadas_ressalva)
    lista_rejeitadas = calcula_ordem(lista_rejeitadas)

    status = {
        "aprovadas": lista_aprovadas,
        "aprovadas_ressalva": lista_aprovadas_ressalva,
        "rejeitadas": lista_rejeitadas
    }

    return status


def calcula_ordem(lista):
    lista = sorted(lista, key=lambda row: row['unidade'])
    ordem = 0

    unidades_que_ja_entraram_na_lista = []
    lista_final = []

    for indice_lista_inicial, informacoes_lista_inicial in enumerate(lista):
        codigo_eol_lista_inicial = informacoes_lista_inicial["codigo_eol"]

        if codigo_eol_lista_inicial in unidades_que_ja_entraram_na_lista:
            for indice_lista_final, informacoes_lista_final in enumerate(lista_final):
                if informacoes_lista_final["codigo_eol"] == codigo_eol_lista_inicial:
                    informacoes_lista_inicial["ordem"] = informacoes_lista_final["ordem"]
                    lista_final.insert(indice_lista_final, informacoes_lista_inicial)
                    break
        else:
            unidades_que_ja_entraram_na_lista.append(codigo_eol_lista_inicial)
            ordem = ordem + 1
            informacoes_lista_inicial["ordem"] = ordem
            lista_final.append(informacoes_lista_inicial)

    return lista_final


def formata_data_publicacao(consolidado_dre):
    consolidado_original = consolidado_dre.consolidado_retificado

    if consolidado_original and consolidado_original.data_publicacao:
        return consolidado_original.data_publicacao.strftime("%d/%m/%Y")

    return ""


def verificar_se_todos_os_valores_da_conta_estao_zerados(status):
    receita = status["receita"]
    despesa = status["despesa"]
    saldo = status["saldo"]
    valores = (
        receita["custeio"],
        receita["livre_aplicacao"],
        receita["capital"],
        despesa["custeio"],
        despesa["capital"],
        saldo["custeio"],
        saldo["livre_aplicacao"],
        saldo["capital"],
    )
    return not any(string_to_float(x) for x in valores)


def gerar_dados_lauda_agregados_por_unidade(dre, periodo, apenas_nao_publicadas, lauda):
    """
    Uma linha por unidade (código EOL), somando todos os tipos de conta,
    para exibição na Lauda em PDF.
    """
    cons = lauda.consolidado_dre if lauda else None
    eh_retificacao = bool(cons and cons.eh_retificacao)

    por_eol = {}

    tipo_contas = TipoConta.objects.all().order_by('nome')
    for tipo_conta in tipo_contas:
        informacao_unidades = informacoes_execucao_financeira_unidades(
            dre,
            periodo,
            tipo_conta,
            apenas_nao_publicadas,
            consolidado_dre=cons if eh_retificacao else None
        )

        for info in informacao_unidades:
            if pc_em_analise(info["status_prestacao_contas"]):
                continue

            eol = str(info["unidade"]["codigo_eol"])
            status_txt = formata_resultado_analise(info["status_prestacao_contas"])
            v = info["valores"]

            r_rend = v["receitas_rendimento_no_periodo_total"]
            r_dev = v["receitas_devolucao_no_periodo_total"]
            demais = v["demais_creditos_no_periodo_total"]
            outros_creditos = r_rend + r_dev + demais

            if eol not in por_eol:
                por_eol[eol] = {
                    "codigo_eol": eol,
                    "unidade": f"{info['unidade']['tipo_unidade']} {info['unidade']['nome']}",
                    "tipo_unidade_sort": info["unidade"]["tipo_unidade"] or "",
                    "nome_sort": info["unidade"]["nome"] or "",
                    "status_prestacao_contas": status_txt,
                    "saldo_inicial": 0.0,
                    "repasses": 0.0,
                    "outros_creditos": 0.0,
                    "despesas": 0.0,
                    "saldo_final": 0.0,
                }
            else:
                if por_eol[eol]["status_prestacao_contas"] != status_txt:
                    logger.warning(
                        "Lauda PDF: status divergente para mesmo EOL %s (mantendo o primeiro encontrado).",
                        eol,
                    )

            agg = por_eol[eol]
            agg["saldo_inicial"] += float(v["saldo_reprogramado_periodo_anterior_total"] or 0)
            agg["repasses"] += float(v["repasses_no_periodo_total"] or 0)
            agg["outros_creditos"] += float(outros_creditos or 0)
            agg["despesas"] += float(v["despesas_no_periodo_total"] or 0)
            agg["saldo_final"] += float(v["saldo_reprogramado_proximo_periodo_total"] or 0)

    return list(por_eol.values())


def atribui_ordem_lauda_pdf(lista):
    lista_ordenada = sorted(
        lista,
        key=lambda row: (
            (row["tipo_unidade_sort"] or "").lower(),
            (row["nome_sort"] or "").lower(),
        ),
    )
    for i, row in enumerate(lista_ordenada, start=1):
        row["ordem"] = i
    return lista_ordenada


def separa_status_lauda_pdf(dados_agregados):
    lista_aprovadas = []
    lista_aprovadas_ressalva = []
    lista_reprovadas = []

    for dado in dados_agregados:
        st = dado["status_prestacao_contas"]
        if st == "Aprovada":
            lista_aprovadas.append(dado.copy())
        elif st == "Aprovada com ressalvas":
            lista_aprovadas_ressalva.append(dado.copy())
        elif st == "Rejeitada":
            lista_reprovadas.append(dado.copy())

    lista_aprovadas = atribui_ordem_lauda_pdf(lista_aprovadas)
    lista_aprovadas_ressalva = atribui_ordem_lauda_pdf(lista_aprovadas_ressalva)
    lista_reprovadas = atribui_ordem_lauda_pdf(lista_reprovadas)

    def _format_rows(lista):
        out = []
        for row in lista:
            out.append({
                "ordem": row["ordem"],
                "codigo_eol": row["codigo_eol"],
                "unidade": row["unidade"],
                "saldo_inicial": formata_valor(row["saldo_inicial"]),
                "repasses": formata_valor(row["repasses"]),
                "outros_creditos": formata_valor(row["outros_creditos"]),
                "despesas": formata_valor(row["despesas"]),
                "saldo_final": formata_valor(row["saldo_final"]),
            })
        return out

    return {
        "aprovadas": _format_rows(lista_aprovadas),
        "aprovadas_ressalva": _format_rows(lista_aprovadas_ressalva),
        "reprovadas": _format_rows(lista_reprovadas),
    }

import logging
import os
import datetime

from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files import File
from django.template.loader import get_template
from tempfile import NamedTemporaryFile
from weasyprint import CSS, HTML

from sme_ptrf_apps.dre.services.lauda_service import (
    formata_data_publicacao,
    formata_nome_dre,
    formata_numero_ata,
    formata_periodo_referencia_lauda_pdf,
    gerar_dados_lauda_agregados_por_unidade,
    separa_status_lauda_pdf,
)

logger = logging.getLogger(__name__)


def _rodape_lauda_sem_identificacao_pessoal(dre):
    data_geracao = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    return (
        f"DRE {formata_nome_dre(dre)} — Lauda gerada via SIG-Escola, em {data_geracao}"
    )


def _montar_titulos_publicacao_lauda(lauda, parcial):
    eh_retificacao = bool(lauda and lauda.consolidado_dre and lauda.consolidado_dre.eh_retificacao)
    eh_parcial = "Parcial" if parcial["parcial"] else "Final"
    sequencia_de_publicacao = parcial["sequencia_de_publicacao_atual"]

    if eh_retificacao:
        cons_ret = getattr(lauda.consolidado_dre, "consolidado_retificado", None)
        seq_num = getattr(cons_ret, "sequencia_de_publicacao", None) if cons_ret else None
        if seq_num is not None:
            titulo_sequencia_publicacao = f"Lauda referente à Parcial #{seq_num}"
        else:
            titulo_sequencia_publicacao = "Lauda referente à retificação da publicação"
    elif eh_parcial == "Parcial":
        titulo_sequencia_publicacao = f"Lauda referente à Publicação Parcial #{sequencia_de_publicacao}"
    else:
        titulo_sequencia_publicacao = "Lauda final"

    titulo_retificacao = None
    subtitulo_retificacao = None
    if eh_retificacao:
        cons_ret = getattr(lauda.consolidado_dre, "consolidado_retificado", None)
        if cons_ret:
            pagina = getattr(cons_ret, "pagina_publicacao", None) or "-"
            titulo_retificacao = (
                f"RETIFICAÇÃO DA PUBLICAÇÃO DO DOC {formata_data_publicacao(lauda.consolidado_dre)} "
                f"- PÁGINA {pagina}"
            )
            subtitulo_retificacao = "LEIA-SE COMO SEGUE E NÃO COMO CONSTOU:"

    return {
        "titulo_sequencia_publicacao": titulo_sequencia_publicacao,
        "titulo_retificacao": titulo_retificacao,
        "subtitulo_retificacao": subtitulo_retificacao,
    }


def gerar_arquivo_lauda_pdf_consolidado_dre(
    lauda,
    dre,
    periodo,
    ata,
    nome_dre,
    parcial,
    apenas_nao_publicadas=False,
):
    logger.info("Arquivo Lauda PDF em processamento.")

    dados_agg = gerar_dados_lauda_agregados_por_unidade(dre, periodo, apenas_nao_publicadas, lauda)
    tabelas = separa_status_lauda_pdf(dados_agg)

    inicio = (
        periodo.data_inicio_realizacao_despesas.strftime("%d/%m/%Y")
        if periodo.data_inicio_realizacao_despesas
        else ""
    )
    fim = (
        periodo.data_fim_realizacao_despesas.strftime("%d/%m/%Y")
        if periodo.data_fim_realizacao_despesas
        else ""
    )
    periodo_datas = f"{inicio} a {fim}" if inicio and fim else (inicio or fim or "")

    titulos_pub = _montar_titulos_publicacao_lauda(lauda, parcial)

    periodo_referencia = periodo.referencia or ""

    cabecalho = {
        "linha_programa_ptrf": "Programa de Transferência de Recursos Financeiros - PTRF",
        "titulo_lauda_publicacao": titulos_pub["titulo_sequencia_publicacao"],
        "periodo_referencia": periodo_referencia,
        "periodo_data_inicio": inicio,
        "periodo_data_fim": fim,
        "data_geracao_documento": _rodape_lauda_sem_identificacao_pessoal(dre),
    }

    titulo_corpo = {
        "dre_maiusculo": (
            f"DIRETORIA REGIONAL DE EDUCAÇÃO - {formata_nome_dre(dre).upper()}"
        ),
        "programa_ptrf_maiusculo": "PROGRAMA DE TRANSFERÊNCIA DE RECURSOS FINANCEIROS PTRF",
    }

    texto_intro = (
        f"No exercício da atribuição a mim conferida pela Portaria SME nº 5.318/2020, torno "
        f"público o Parecer Técnico Conclusivo da Comissão de Prestação de Contas do PTRF da DRE "
        f"{formata_nome_dre(dre, capitalize=True)}, expedido através da ata nº {formata_numero_ata(ata)}, "
        f"relativo à prestação de contas do Programa de Transferência de Recursos Financeiros - PTRF "
        f"- {formata_periodo_referencia_lauda_pdf(ata)}:"
    )

    contexto = {
        "cabecalho": cabecalho,
        "titulo_corpo": titulo_corpo,
        "titulo_retificacao": titulos_pub["titulo_retificacao"],
        "subtitulo_retificacao": titulos_pub["subtitulo_retificacao"],
        "texto_intro": texto_intro,
        "periodo_datas": periodo_datas,
        "col_saldo_inicial": f"Saldo reprogramado inicial em {inicio}" if inicio else "Saldo reprogramado inicial",
        "col_saldo_final": f"Saldo reprogramado final em {fim}" if fim else "Saldo reprogramado final",
        "tabelas": tabelas,
    }

    html_template = get_template("pdf/lauda/pdf.html")
    rendered = html_template.render(
        {
            "dados": contexto,
            "base_static_url": staticfiles_storage.location,
        }
    )

    logger.info("base_url: %s", os.path.basename(staticfiles_storage.location))

    pdf_bytes = HTML(
        string=rendered,
        base_url=staticfiles_storage.location,
    ).write_pdf(
        stylesheets=[CSS(staticfiles_storage.location + "/css/lauda-pdf.css")],
    )

    nome_pdf = f"Lauda_{nome_dre}.pdf"
    with NamedTemporaryFile(mode="w+b", suffix=".pdf") as tmp:
        tmp.write(pdf_bytes)
        tmp.seek(0)
        lauda.arquivo_lauda_pdf.save(name=nome_pdf, content=File(tmp))

    logger.info("Arquivo Lauda PDF gerado com sucesso.")

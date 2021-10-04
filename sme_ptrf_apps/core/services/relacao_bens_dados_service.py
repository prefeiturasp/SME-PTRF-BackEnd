import logging
from datetime import datetime

from datetime import date

from sme_ptrf_apps.core.choices import MembroEnum

from sme_ptrf_apps.core.models import (MembroAssociacao)

LOGGER = logging.getLogger(__name__)


def gerar_dados_relacao_de_bens(usuario, conta_associacao=None, periodo=None, previa=False, rateios=None):

    try:
        LOGGER.info("GERANDO DADOS RELAÇÃO DE BENS...")

        cabecalho = cria_cabecalho(periodo, conta_associacao, previa)
        identificacao_apm = cria_identificacao_apm(conta_associacao)
        data_geracao = cria_data_geracao()
        relacao_de_bens_adquiridos_ou_produzidos = cria_relacao_de_bens_adquiridos_ou_produzidos(rateios)
        data_geracao_documento = cria_data_geracao_documento(usuario, previa)

        dados_relacao_de_bens = {
            "cabecalho": cabecalho,
            "identificacao_apm": identificacao_apm,
            "data_geracao": data_geracao,
            "relacao_de_bens_adquiridos_ou_produzidos": relacao_de_bens_adquiridos_ou_produzidos,
            "data_geracao_documento": data_geracao_documento
        }
    finally:
        LOGGER.info("DADOS RELAÇÃO DE BENS GERADO")

    return dados_relacao_de_bens


def cria_cabecalho(periodo, conta_associacao, previa):
    """ GERA CABECALHO DOCUMENTO EM PDF RELACAO DE BENS """

    cabecalho = {
        "titulo": "Relação de Bens - PRÉVIA" if previa else "Relação de Bens - FINAL",
        "periodo": str(periodo),
        "periodo_referencia": periodo.referencia,
        "periodo_data_inicio": formata_data(periodo.data_inicio_realizacao_despesas),
        "periodo_data_fim": formata_data(periodo.data_fim_realizacao_despesas),
        "conta": conta_associacao.tipo_conta.nome,
    }

    return cabecalho


def cria_identificacao_apm(conta_associacao):
    """BLOCO 1 - IDENTIFICAÇÃO DA APM/APMSUAC DA UNIDADE EDUCACIONAL DOCUMENTO EM PDF RELACAO DE BENS """
    associacao = conta_associacao.associacao

    nome_associacao = associacao.nome
    cnpj_associacao = associacao.cnpj
    codigo_eol_associacao = associacao.unidade.codigo_eol or ""
    nome_dre_associacao = associacao.unidade.dre.nome if associacao.unidade.dre else ""
    _presidente_diretoria_executiva = MembroAssociacao.objects.filter(associacao=associacao,
                                                                     cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.name).first()
    presidente_diretoria_executiva = _presidente_diretoria_executiva.nome if _presidente_diretoria_executiva else ''
    tipo_unidade = associacao.unidade.tipo_unidade
    nome_unidade = associacao.unidade.nome

    identificacao_apm = {
        "nome_associacao": nome_associacao,
        "cnpj_associacao": cnpj_associacao,
        "codigo_eol_associacao": codigo_eol_associacao,
        "nome_dre_associacao": nome_dre_associacao,
        "presidente_diretoria_executiva": presidente_diretoria_executiva,
        "tipo_unidade": tipo_unidade,
        "nome_unidade": nome_unidade,
    }

    return identificacao_apm


def cria_relacao_de_bens_adquiridos_ou_produzidos(rateios):
    """ BLOCO 2 - IDENTIFICAÇÃO DOS BENS ADQUIRIDOS OU PRODUZIDOS DOCUMENTO EM PDF RELACAO DE BENS """
    if not rateios:
        return

    valor_total = sum(r.valor_rateio for r in rateios)

    linhas = []
    for _, rateio in enumerate(rateios):
        tipo_documento = rateio.despesa.tipo_documento.nome if rateio.despesa.tipo_documento else ''
        numero_documento = rateio.despesa.numero_documento
        data_documento = rateio.despesa.data_documento.strftime("%d/%m/%Y") if rateio.despesa.data_documento else ''
        especificacao_material = \
            rateio.especificacao_material_servico.descricao if rateio.especificacao_material_servico else ''
        numero_documento_incorporacao = rateio.numero_processo_incorporacao_capital
        quantidade = rateio.quantidade_itens_capital
        valor_item = formata_valor(rateio.valor_item_capital)
        valor_rateio = formata_valor(rateio.valor_rateio)

        linha = {
            "tipo_documento": tipo_documento,
            "numero_documento": numero_documento,
            "especificacao_material": especificacao_material,
            "numero_documento_incorporacao": numero_documento_incorporacao,
            "quantidade": quantidade,
            "data_documento": data_documento,
            "valor_item": valor_item,
            "valor_rateio": valor_rateio
        }
        linhas.append(linha)

    despesas = {
        "linhas": linhas,
        "valor_total": valor_total
    }
    return despesas


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

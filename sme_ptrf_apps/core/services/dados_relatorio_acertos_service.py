from sme_ptrf_apps.core.services.prestacao_contas_services import (lancamentos_da_prestacao)
from ..api.serializers.analise_documento_prestacao_conta_serializer import AnaliseDocumentoPrestacaoContaRetrieveSerializer
from datetime import date
from ...utils.numero_ordinal import formata_numero_ordinal

import logging

logger = logging.getLogger(__name__)


def gerar_dados_relatorio_acertos(analise_prestacao_conta, previa, usuario=""):
    info_cabecalho = {
        'periodo_referencia': analise_prestacao_conta.prestacao_conta.periodo.referencia,
        'data_inicio_periodo': analise_prestacao_conta.prestacao_conta.periodo.data_inicio_realizacao_despesas,
        'data_fim_periodo': analise_prestacao_conta.prestacao_conta.periodo.data_fim_realizacao_despesas
    }

    dados_associacao = {
        'nome_associacao': analise_prestacao_conta.prestacao_conta.associacao.nome,
        'cnpj_associacao': analise_prestacao_conta.prestacao_conta.associacao.cnpj,
        'codigo_eol_associacao': analise_prestacao_conta.prestacao_conta.associacao.unidade.codigo_eol,
        'nome_dre': analise_prestacao_conta.prestacao_conta.associacao.unidade.dre.nome,
        'data_devolucao_dre': analise_prestacao_conta.devolucao_prestacao_conta.data if analise_prestacao_conta.devolucao_prestacao_conta else "-",
        'prazo_devolucao_associacao': analise_prestacao_conta.devolucao_prestacao_conta.data_limite_ue if analise_prestacao_conta.devolucao_prestacao_conta else "-"
    }

    dados_contas = []
    for conta in analise_prestacao_conta.prestacao_conta.associacao.contas.all():
        lancamentos = lancamentos_da_prestacao(
            analise_prestacao_conta=analise_prestacao_conta,
            conta_associacao=conta,
            com_ajustes=True
        )

        dados = {
            'nome_conta': conta.tipo_conta.nome,
            'lancamentos': lancamentos
        }

        dados_contas.append(dados)

    dados_tecnico = {
        "responsavel": formata_tecnico_dre(analise_prestacao_conta),
        "data_devolucao": analise_prestacao_conta.devolucao_prestacao_conta.data if analise_prestacao_conta.devolucao_prestacao_conta else "-",
    }

    documentos = analise_prestacao_conta.analises_de_documento.filter(resultado='AJUSTE').all().order_by(
        'tipo_documento_prestacao_conta__nome')

    dados_documentos = AnaliseDocumentoPrestacaoContaRetrieveSerializer(documentos, many=True).data

    data_geracao_documento = cria_data_geracao_documento(usuario, previa)

    dados = {
        'info_cabecalho': info_cabecalho,
        'dados_associacao': dados_associacao,
        'versao_devolucao': "Rascunho" if previa else verifica_versao_devolucao(analise_prestacao_conta),
        'dados_contas': dados_contas,
        'dados_documentos': dados_documentos,
        'dados_tecnico': dados_tecnico,
        'data_geracao_documento': data_geracao_documento
    }

    return dados


def cria_data_geracao_documento(usuario, previa):
    data_geracao = date.today().strftime("%d/%m/%Y")
    tipo_texto = "rascunho" if previa else "final"
    quem_gerou = "" if usuario == "" else f"pelo usuário {usuario}. "
    texto = f"Documento {tipo_texto} gerado pelo Sig_Escola em {data_geracao} {quem_gerou}"

    return texto


def verifica_versao_devolucao(analise_prestacao_conta):
    try:
        devolucoes = analise_prestacao_conta.prestacao_conta.analises_da_prestacao.filter(status='DEVOLVIDA').order_by(
            'id')
        index_ultima_devolucao = len(devolucoes)
        numero_ordinal = formata_numero_ordinal(index_ultima_devolucao)
    except Exception as e:
        numero_ordinal = ""
        logger.info(f"ocorreu o seguinte o erro: {e}")

    return numero_ordinal


def formata_tecnico_dre(analise_prestacao_conta):
    tecnico = analise_prestacao_conta.prestacao_conta.tecnico_responsavel

    if tecnico is not None:
        return f"{tecnico.nome} - RF: {tecnico.rf}"

    return "-"

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
        'nome_dre': formata_nome_dre(analise_prestacao_conta.prestacao_conta.associacao),
        'data_devolucao_dre': analise_prestacao_conta.devolucao_prestacao_conta.data if analise_prestacao_conta.devolucao_prestacao_conta else "-",
        'prazo_devolucao_associacao': analise_prestacao_conta.devolucao_prestacao_conta.data_limite_ue if analise_prestacao_conta.devolucao_prestacao_conta else "-"
    }

    dados_ajustes_contas = []
    logger.info(f'Análise de PC {analise_prestacao_conta.id}')
    for analise_conta in analise_prestacao_conta.analises_de_extratos.all():
        logger.info(f'Análise de conta {analise_conta.id}')
        if analise_conta.data_extrato or analise_conta.saldo_extrato is not None:
            dados = {
                'nome_conta': analise_conta.conta_associacao.tipo_conta.nome,
                'data_extrato': analise_conta.data_extrato,
                'saldo_extrato': analise_conta.saldo_extrato,
            }
            logger.info(f'Ajuste em conta:{dados["nome_conta"]} data:{dados["data_extrato"]} saldo:{dados["saldo_extrato"]}')
            dados_ajustes_contas.append(dados)

    dados_lancamentos = []
    for conta in analise_prestacao_conta.prestacao_conta.associacao.contas.all():
        lancamentos = lancamentos_da_prestacao(
            analise_prestacao_conta=analise_prestacao_conta,
            conta_associacao=conta,
            com_ajustes=True
        )

        if lancamentos:
            dados = {
                'nome_conta': conta.tipo_conta.nome,
                'lancamentos': lancamentos
            }

            dados_lancamentos.append(dados)

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
        'dados_ajustes_contas': dados_ajustes_contas,
        'dados_lancamentos': dados_lancamentos,
        'dados_documentos': dados_documentos,
        'dados_tecnico': dados_tecnico,
        'data_geracao_documento': data_geracao_documento,
        'blocos': nome_blocos(dados_ajustes_contas, dados_lancamentos, dados_documentos, dados_tecnico, previa)
    }

    return dados


def nome_blocos(dados_ajustes_contas, dados_lancamentos, dados_documentos, dados_tecnico, previa):
    dados = {}
    numero_bloco = 1

    dados[f'identificacao_associacao'] = 'Bloco 1 - Identificação da Associação da Unidade Educacional'

    if dados_ajustes_contas:
        numero_bloco = numero_bloco + 1
        dados[f'acertos_contas'] = f'Bloco {numero_bloco} - Acertos nas informações de extrato bancário'

    if dados_lancamentos:
        numero_bloco = numero_bloco + 1
        dados[f'acertos_lancamentos'] = f'Bloco {numero_bloco} - Acertos nos lançamentos'

    if dados_documentos:
        numero_bloco = numero_bloco + 1
        dados[f'acertos_documentos'] = f'Bloco {numero_bloco} - Acertos nos documentos'

    if not previa and dados_tecnico:
        numero_bloco = numero_bloco + 1
        dados[f'responsavel_analise'] = f'Bloco {numero_bloco} - Responsável pela análise da Prestação de Contas'

    return dados


def cria_data_geracao_documento(usuario, previa):
    data_geracao = date.today().strftime("%d/%m/%Y")
    tipo_texto = "prévia" if previa else "final"
    quem_gerou = "" if usuario == "" else f"pelo usuário {usuario}. "
    texto = f"Documento {tipo_texto} gerado pelo SIG-Escola em {data_geracao} {quem_gerou}"

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

import logging
from datetime import datetime

from datetime import date

from sme_ptrf_apps.dre.models import JustificativaRelatorioConsolidadoDRE, AnoAnaliseRegularidade, ConsolidadoDRE
from sme_ptrf_apps.core.models import Associacao, PrestacaoConta, TipoConta
from sme_ptrf_apps.dre.models import ParametrosDre

from django.db.models import Max, Value, Count
from django.db.models.functions import Coalesce


LOGGER = logging.getLogger(__name__)


def gerar_dados_demo_execucao_fisico_financeira(dre, periodo, usuario, parcial, previa=False, apenas_nao_publicadas=False, eh_consolidado_de_publicacoes_parciais=False, consolidado_dre=None):
    try:
        LOGGER.info("Gerando relatório consolidado...")

        cabecalho = cria_cabecalho(periodo, parcial, previa, consolidado_dre)
        bloco_consolidado_das_publicacoes_parciais = cria_bloco_consolidado_das_publicacoes_parciais(dre, periodo) if eh_consolidado_de_publicacoes_parciais else None
        data_geracao_documento = cria_data_geracao_documento(usuario, dre, parcial, previa)
        identificacao_dre = cria_identificacao_dre(dre)
        execucao_financeira = cria_execucao_financeira(dre, periodo, apenas_nao_publicadas, consolidado_dre, eh_consolidado_de_publicacoes_parciais, previa)
        execucao_fisica = cria_execucao_fisica(dre, periodo, apenas_nao_publicadas, consolidado_dre, eh_consolidado_de_publicacoes_parciais)
        dados_fisicos_financeiros = cria_dados_fisicos_financeiros(dre, periodo, apenas_nao_publicadas, eh_consolidado_de_publicacoes_parciais, consolidado_dre)

        assinatura_dre = cria_assinaturas_dre(dre)

        """
            Mapeamento campos x pdf - Campos usados em cada um dos blocos do PDF:

            Bloco 1 - Identificação
                cabecalho
                identificacao_dre
                Consolidação das Publicações(cria_bloco_consolidado_das_publicacoes_parciais)

            Bloco 2 - SÍNTESE DA EXECUÇÃO FINANCEIRA (R$)
                execucao_financeira
                associacoes_nao_regularizadas

            Bloco 3 - EXECUÇÃO FÍSICA
                execucao_fisica

            Bloco 4 - DADOS FÍSICO-FINANCEIROS DA EXECUÇÃO (R$)
                dados_fisicos_financeiros

            Bloco 5 - AUTENTICAÇÃO
                assinatura_dre
        """

        dados_demonstrativo = {
            "cabecalho": cabecalho,
            "bloco_consolidado_das_publicacoes_parciais": bloco_consolidado_das_publicacoes_parciais,
            "data_geracao_documento": data_geracao_documento,
            "identificacao_dre": identificacao_dre,
            "execucao_financeira": execucao_financeira,
            "execucao_fisica": execucao_fisica,
            "dados_fisicos_financeiros": dados_fisicos_financeiros,
            "assinatura_dre": assinatura_dre,
            "versao_relatorio": "PARCIAL" if parcial else "FINAL",
            "previa": previa
        }

    finally:
        LOGGER.info("DADOS DEMONSTRATIVO GERADO")

    return dados_demonstrativo


def cria_bloco_consolidado_das_publicacoes_parciais(dre, periodo):
    consolidados_dre = ConsolidadoDRE.objects.filter(dre=dre, periodo=periodo, versao="FINAL").order_by("sequencia_de_publicacao", "alterado_em")
    consolidado_das_publicacoes_parciais_list = []

    for consolidado in consolidados_dre:
        numero_sequencia = consolidado.sequencia_de_publicacao if consolidado.sequencia_de_publicacao else ""

        titulo_parcial = ""
        if(consolidado.eh_parcial and consolidado.consolidado_retificado_id):
            consolidado_origem_retificacao = ConsolidadoDRE.objects.filter(pk=consolidado.consolidado_retificado_id)

            if(consolidado_origem_retificacao.count() > 0 and consolidado_origem_retificacao[0].data_publicacao):
                data_publicacao_consolidado_origem_retificacao = consolidado_origem_retificacao[0].data_publicacao.strftime("%d/%m/%Y")
                titulo_parcial = f"Retificação da publicação de {data_publicacao_consolidado_origem_retificacao}"

        elif(not consolidado.eh_parcial):
            titulo_parcial = f"Única"

        else:
            titulo_parcial = f"Parcial #{numero_sequencia}"

        data_publicacao = consolidado.data_publicacao.strftime("%d/%m/%Y") if consolidado.data_publicacao else ""
        numero_unidades = len(consolidado.pcs_vinculadas_ao_consolidado())
        result = {
            'titulo_parcial': titulo_parcial,
            'data_publicacao': data_publicacao,
            'numero_unidades': numero_unidades,
        }

        consolidado_das_publicacoes_parciais_list.append(result)

    return consolidado_das_publicacoes_parciais_list


def cria_cabecalho(periodo, parcial, previa, consolidado_dre):
    LOGGER.info("Iniciando cabecalho...")

    eh_parcial = parcial['parcial']
    sequencia_de_publicacao = parcial['sequencia_de_publicacao_atual']
    eh_retificacao = True if consolidado_dre and consolidado_dre.eh_retificacao else False

    if previa and eh_retificacao:
        titulo_sequencia_publicacao = f'{consolidado_dre.referencia} (Prévia)'
    elif previa and eh_parcial:
        titulo_sequencia_publicacao = f'Publicação Parcial #{sequencia_de_publicacao} (Prévia)'
    elif previa and not eh_parcial:
        titulo_sequencia_publicacao = f'Publicação Única (Prévia)'
    elif not previa and eh_retificacao:
        titulo_sequencia_publicacao = f'{consolidado_dre.referencia}'
    elif not previa and eh_parcial:
        titulo_sequencia_publicacao = f'Publicação Parcial #{sequencia_de_publicacao}'
    elif not previa and not eh_parcial and sequencia_de_publicacao == 0:
        titulo_sequencia_publicacao = 'Publicação Única'
    else:
        # Nesse caso é o relatório do consolidado de publicações parciais
        titulo_sequencia_publicacao = f'Relatório Consolidado'

    cabecalho = {
        "periodo": str(periodo),
        "periodo_referencia": periodo.referencia,
        "periodo_data_inicio": formata_data(periodo.data_inicio_realizacao_despesas),
        "periodo_data_fim": formata_data(periodo.data_fim_realizacao_despesas),
        "status": "PARCIAL" if parcial else "FINAL",
        "titulo_sequencia_publicacao": titulo_sequencia_publicacao
    }

    return cabecalho


def cria_identificacao_dre(dre):
    """BLOCO 1 - IDENTIFICAÇÃO"""
    identificacao = {
        "nome_dre": formata_nome_dre(dre),
        "cnpj_dre": dre.dre_cnpj if dre.dre_cnpj else ""
    }

    return identificacao


def cria_execucao_financeira(dre, periodo, apenas_nao_publicadas, consolidado_dre, eh_consolidado_de_publicacoes_parciais, previa):
    """BLOCO 2 - EXECUÇÃO FINANCEIRA"""
    from .relatorio_consolidado_service import informacoes_execucao_financeira

    tipos_contas = TipoConta.objects.all()
    execucao_financeira_list = {
        'por_tipo_de_conta': [],
        'total_todas_as_contas': []
    }
    for tipo_conta in tipos_contas:
        info = informacoes_execucao_financeira(dre, periodo, tipo_conta, apenas_nao_publicadas, consolidado_dre)

        soma_dos_totais = sum(info.values())

        """
            Verificando se existe algum valor para incluir os dados no resultado
            Não devem ser exibidas as linhas de contas que tenham valores zerados em todas as colunas.
        """

        if soma_dos_totais:
            # LINHA CUSTEIO

            # Bug 80480
            # valor_total_custeio = info['saldo_reprogramado_periodo_anterior_custeio'] + info['repasses_no_periodo_custeio'] + \
            #     info['receitas_devolucao_no_periodo_custeio'] + info['demais_creditos_no_periodo_custeio']
            valor_total_custeio = info['saldo_reprogramado_periodo_anterior_custeio'] + info['receitas_totais_no_periodo_custeio']

            # outros_creditos = info['receitas_rendimento_no_periodo_livre'] + info['receitas_devolucao_no_periodo_custeio'] + \
            #     info['demais_creditos_no_periodo_custeio']

            outros_creditos_custeio = info['receitas_totais_no_periodo_custeio'] - info['repasses_no_periodo_custeio']

            custeio = {
                "saldo_reprogramado_periodo_anterior_custeio": formata_valor(info['saldo_reprogramado_periodo_anterior_custeio']),
                "repasses_previstos_sme_custeio": formata_valor(info['repasses_previstos_sme_custeio']),
                "repasses_no_periodo_custeio": formata_valor(info['repasses_no_periodo_custeio']),
                "demais_creditos_no_periodo_custeio": formata_valor(info['demais_creditos_no_periodo_custeio']),
                "valor_total_custeio": formata_valor(valor_total_custeio),
                "despesas_no_periodo_custeio": formata_valor(info['despesas_no_periodo_custeio']),
                "saldo_reprogramado_proximo_periodo_custeio": formata_valor(info['saldo_reprogramado_proximo_periodo_custeio']),
                "outros_creditos": formata_valor(outros_creditos_custeio)
            }

            # LINHA CAPITAL

            # Bug 80480
            # valor_total_capital = info['saldo_reprogramado_periodo_anterior_capital'] + info['repasses_no_periodo_capital'] + \
            #     info['receitas_devolucao_no_periodo_capital'] + info['demais_creditos_no_periodo_capital']
            valor_total_capital = info['saldo_reprogramado_periodo_anterior_capital'] + info['receitas_totais_no_periodo_capital']

            outros_creditos_capital = info['receitas_totais_no_periodo_capital'] - info['repasses_no_periodo_capital']
            # outros_creditos = info['receitas_rendimento_no_periodo_livre'] + info['receitas_devolucao_no_periodo_capital'] + \
            #     info['demais_creditos_no_periodo_capital']


            capital = {
                "saldo_reprogramado_periodo_anterior_capital": formata_valor(info['saldo_reprogramado_periodo_anterior_capital']),
                "repasses_previstos_sme_capital": formata_valor(info['repasses_previstos_sme_capital']),
                "repasses_no_periodo_capital": formata_valor(info['repasses_no_periodo_capital']),
                "demais_creditos_no_periodo_capital": formata_valor(info['demais_creditos_no_periodo_capital']),
                "valor_total_capital": formata_valor(valor_total_capital),
                "despesas_no_periodo_capital": formata_valor(info['despesas_no_periodo_capital']),
                "saldo_reprogramado_proximo_periodo_capital": formata_valor(info['saldo_reprogramado_proximo_periodo_capital']),
                "outros_creditos": formata_valor(outros_creditos_capital)
            }

            # LINHA RLA

            # Bug 80480
            # valor_total_livre = info['saldo_reprogramado_periodo_anterior_livre'] + \
            #     info['receitas_rendimento_no_periodo_livre'] + \
            #     info['repasses_no_periodo_livre'] + info['receitas_devolucao_no_periodo_livre'] + \
            #     info['demais_creditos_no_periodo_livre']
            valor_total_livre = info['saldo_reprogramado_periodo_anterior_livre'] + info['receitas_totais_no_periodo_livre']

            # outros_creditos = info['receitas_rendimento_no_periodo_livre'] + info['receitas_devolucao_no_periodo_livre'] + \
            #     info['demais_creditos_no_periodo_livre']

            outros_creditos_livre = info['receitas_totais_no_periodo_livre'] - info['repasses_no_periodo_livre']

            rla = {
                "saldo_reprogramado_periodo_anterior_livre": formata_valor(info['saldo_reprogramado_periodo_anterior_livre']),
                "repasses_previstos_sme_livre": formata_valor(info['repasses_previstos_sme_livre']),
                "repasses_no_periodo_livre": formata_valor(info['repasses_no_periodo_livre']),
                "demais_creditos_no_periodo_livre": formata_valor(info['demais_creditos_no_periodo_livre']),
                "valor_total_livre": formata_valor(valor_total_livre),
                "saldo_reprogramado_proximo_periodo_livre": formata_valor(info['saldo_reprogramado_proximo_periodo_livre']),
                "devolucoes_ao_tesouro_no_periodo_total": formata_valor(info['devolucoes_ao_tesouro_no_periodo_total']),
                "outros_creditos": formata_valor(outros_creditos_livre)
            }

            # LINHA TOTAIS

            # Bug 80480
            # valor_total = info['saldo_reprogramado_periodo_anterior_total'] + info['receitas_rendimento_no_periodo_livre'] + \
            #     info['repasses_no_periodo_total'] + info['receitas_devolucao_no_periodo_total'] + \
            #     info['demais_creditos_no_periodo_total']
            valor_total = info['saldo_reprogramado_periodo_anterior_total'] + info['receitas_totais_no_periodo_total']

            # outros_creditos = info['receitas_rendimento_no_periodo_livre'] + \
            #     info['receitas_devolucao_no_periodo_total'] + info['demais_creditos_no_periodo_total']

            outros_creditos_total = info['receitas_totais_no_periodo_total'] - info['repasses_no_periodo_total']

            totais = {
                "saldo_reprogramado_periodo_anterior_total": formata_valor(info['saldo_reprogramado_periodo_anterior_total']),
                "repasses_previstos_sme_total": formata_valor(info['repasses_previstos_sme_total']),
                "repasses_no_periodo_total": formata_valor(info['repasses_no_periodo_total']),
                "demais_creditos_no_periodo_total": formata_valor(info['demais_creditos_no_periodo_total']),
                "valor_total": formata_valor(valor_total),
                "despesas_no_periodo_total": formata_valor(info['despesas_no_periodo_total']),
                "saldo_reprogramado_proximo_periodo_total": formata_valor(info['saldo_reprogramado_proximo_periodo_total']),
                "devolucoes_ao_tesouro_no_periodo_total": formata_valor(info['devolucoes_ao_tesouro_no_periodo_total']),
                "outros_creditos": formata_valor(outros_creditos_total)
            }

            # Justificativa #
            justificativa = None
            obj_justificativas_list = []

            if consolidado_dre and consolidado_dre.eh_retificacao:
                if previa:
                    justificativa = JustificativaRelatorioConsolidadoDRE.objects.filter(
                        dre=dre,
                        tipo_conta=tipo_conta,
                        periodo=periodo,
                        consolidado_dre__isnull=True,
                        eh_retificacao=True
                    ).last()
                else:
                    justificativa = JustificativaRelatorioConsolidadoDRE.objects.filter(
                        dre=dre,
                        tipo_conta=tipo_conta,
                        periodo=periodo,
                        consolidado_dre=consolidado_dre,
                        eh_retificacao=True
                    ).last()
            elif eh_consolidado_de_publicacoes_parciais:
                justificativas = JustificativaRelatorioConsolidadoDRE.objects.filter(
                    dre=dre,
                    tipo_conta=tipo_conta,
                    periodo=periodo,
                    eh_retificacao=False
                )

                for just in justificativas:
                    texto_justificativa = ''
                    if just:
                        texto_justificativa = f"{just.texto}"
                    if just and just.consolidado_dre:
                        texto_justificativa = f"{texto_justificativa} - {just.consolidado_dre.referencia}"

                    obj_justificativa = {
                        "justificativa": texto_justificativa,
                    }
                    obj_justificativas_list.append(obj_justificativa)

            elif consolidado_dre and consolidado_dre.versao == 'FINAL':
                justificativa = JustificativaRelatorioConsolidadoDRE.objects.filter(
                    dre=dre,
                    tipo_conta=tipo_conta,
                    periodo=periodo,
                    consolidado_dre=consolidado_dre,
                    eh_retificacao=False
                ).last()
            else:
                justificativa = JustificativaRelatorioConsolidadoDRE.objects.filter(
                    dre=dre,
                    tipo_conta=tipo_conta,
                    periodo=periodo,
                    consolidado_dre__isnull=True,
                    eh_retificacao=False
                ).last()

            if not eh_consolidado_de_publicacoes_parciais:
                execucao_financeira = {
                    "tipo_conta": tipo_conta.nome if tipo_conta.nome else "",
                    "custeio": custeio,
                    "capital": capital,
                    "livre": rla,
                    "totais": totais,
                    "justificativa": justificativa.texto if justificativa else '',
                }
            else:
                execucao_financeira = {
                    "tipo_conta": tipo_conta.nome if tipo_conta.nome else "",
                    "custeio": custeio,
                    "capital": capital,
                    "livre": rla,
                    "totais": totais,
                    "justificativa": obj_justificativas_list,
                }

            execucao_financeira_list['por_tipo_de_conta'].append(execucao_financeira)

    execucao_financeira_list['total_todas_as_contas'].append(retorna_total_todas_as_contas_execucao_financeira(execucao_financeira_list['por_tipo_de_conta']))

    return execucao_financeira_list


def retorna_objeto_totais_todas_as_contas_execucao_financeira_vazio():
    totais_todas_as_contas = {
        "tipo_conta": 'TOTAL',
        'custeio': {
            'saldo_reprogramado_periodo_anterior_custeio': 0,
            'repasses_previstos_sme_custeio': 0,
            "repasses_no_periodo_custeio": 0,
            "demais_creditos_no_periodo_custeio": 0,
            "valor_total_custeio": 0,
            "despesas_no_periodo_custeio": 0,
            "saldo_reprogramado_proximo_periodo_custeio": 0,
            "outros_creditos": 0,
        },
        'capital': {
            "saldo_reprogramado_periodo_anterior_capital": 0,
            "repasses_previstos_sme_capital": 0,
            "repasses_no_periodo_capital": 0,
            "demais_creditos_no_periodo_capital": 0,
            "valor_total_capital": 0,
            "despesas_no_periodo_capital": 0,
            "saldo_reprogramado_proximo_periodo_capital": 0,
            "outros_creditos": 0
        },

        'livre': {
            "saldo_reprogramado_periodo_anterior_livre": 0,
            "repasses_previstos_sme_livre": 0,
            "repasses_no_periodo_livre": 0,
            "demais_creditos_no_periodo_livre": 0,
            "valor_total_livre": 0,
            "saldo_reprogramado_proximo_periodo_livre": 0,
            "devolucoes_ao_tesouro_no_periodo_total": 0,
            "outros_creditos": 0
        },
        'totais': {
            "saldo_reprogramado_periodo_anterior_total": 0,
            "repasses_previstos_sme_total": 0,
            "repasses_no_periodo_total": 0,
            "demais_creditos_no_periodo_total": 0,
            "valor_total": 0,
            "despesas_no_periodo_total": 0,
            "saldo_reprogramado_proximo_periodo_total": 0,
            "devolucoes_ao_tesouro_no_periodo_total": 0,
            "outros_creditos": 0
        }
    }

    return totais_todas_as_contas


def retorna_total_todas_as_contas_execucao_financeira(execucao_financeira_list):

    totais_todas_as_contas = retorna_objeto_totais_todas_as_contas_execucao_financeira_vazio()

    for ex in execucao_financeira_list:
        # Custeio
       totais_todas_as_contas['custeio']['saldo_reprogramado_periodo_anterior_custeio'] += converte_string_value_formatada_para_float(ex['custeio']['saldo_reprogramado_periodo_anterior_custeio'])
       totais_todas_as_contas['custeio']['repasses_previstos_sme_custeio'] += converte_string_value_formatada_para_float(ex['custeio']['repasses_previstos_sme_custeio'])
       totais_todas_as_contas['custeio']['repasses_no_periodo_custeio'] += converte_string_value_formatada_para_float(ex['custeio']['repasses_no_periodo_custeio'])
       totais_todas_as_contas['custeio']['demais_creditos_no_periodo_custeio'] += converte_string_value_formatada_para_float(ex['custeio']['demais_creditos_no_periodo_custeio'])
       totais_todas_as_contas['custeio']['valor_total_custeio'] += converte_string_value_formatada_para_float(ex['custeio']['valor_total_custeio'])
       totais_todas_as_contas['custeio']['despesas_no_periodo_custeio'] += converte_string_value_formatada_para_float(ex['custeio']['despesas_no_periodo_custeio'])
       totais_todas_as_contas['custeio']['saldo_reprogramado_proximo_periodo_custeio'] += converte_string_value_formatada_para_float(ex['custeio']['saldo_reprogramado_proximo_periodo_custeio'])
       totais_todas_as_contas['custeio']['outros_creditos'] += converte_string_value_formatada_para_float(ex['custeio']['outros_creditos'])

        # Capital
       totais_todas_as_contas['capital']['saldo_reprogramado_periodo_anterior_capital'] += converte_string_value_formatada_para_float(ex['capital']['saldo_reprogramado_periodo_anterior_capital'])
       totais_todas_as_contas['capital']['repasses_previstos_sme_capital'] += converte_string_value_formatada_para_float(ex['capital']['repasses_previstos_sme_capital'])
       totais_todas_as_contas['capital']['repasses_no_periodo_capital'] += converte_string_value_formatada_para_float(ex['capital']['repasses_no_periodo_capital'])
       totais_todas_as_contas['capital']['demais_creditos_no_periodo_capital'] += converte_string_value_formatada_para_float(ex['capital']['demais_creditos_no_periodo_capital'])
       totais_todas_as_contas['capital']['valor_total_capital'] += converte_string_value_formatada_para_float(ex['capital']['valor_total_capital'])
       totais_todas_as_contas['capital']['despesas_no_periodo_capital'] += converte_string_value_formatada_para_float(ex['capital']['despesas_no_periodo_capital'])
       totais_todas_as_contas['capital']['saldo_reprogramado_proximo_periodo_capital'] += converte_string_value_formatada_para_float(ex['capital']['saldo_reprogramado_proximo_periodo_capital'])
       totais_todas_as_contas['capital']['outros_creditos'] += converte_string_value_formatada_para_float(ex['capital']['outros_creditos'])

        # Livre Aplicacao - RLA
       totais_todas_as_contas['livre']['saldo_reprogramado_periodo_anterior_livre'] += converte_string_value_formatada_para_float(ex['livre']['saldo_reprogramado_periodo_anterior_livre'])
       totais_todas_as_contas['livre']['repasses_previstos_sme_livre'] += converte_string_value_formatada_para_float(ex['livre']['repasses_previstos_sme_livre'])
       totais_todas_as_contas['livre']['repasses_no_periodo_livre'] += converte_string_value_formatada_para_float(ex['livre']['repasses_no_periodo_livre'])
       totais_todas_as_contas['livre']['demais_creditos_no_periodo_livre'] += converte_string_value_formatada_para_float(ex['livre']['demais_creditos_no_periodo_livre'])
       totais_todas_as_contas['livre']['valor_total_livre'] += converte_string_value_formatada_para_float(ex['livre']['valor_total_livre'])
       totais_todas_as_contas['livre']['saldo_reprogramado_proximo_periodo_livre'] += converte_string_value_formatada_para_float(ex['livre']['saldo_reprogramado_proximo_periodo_livre'])
       totais_todas_as_contas['livre']['devolucoes_ao_tesouro_no_periodo_total'] += converte_string_value_formatada_para_float(ex['livre']['devolucoes_ao_tesouro_no_periodo_total'])
       totais_todas_as_contas['livre']['outros_creditos'] += converte_string_value_formatada_para_float(ex['livre']['outros_creditos'])

        # Totais
       totais_todas_as_contas['totais']['saldo_reprogramado_periodo_anterior_total'] += converte_string_value_formatada_para_float(ex['totais']['saldo_reprogramado_periodo_anterior_total'])
       totais_todas_as_contas['totais']['repasses_previstos_sme_total'] += converte_string_value_formatada_para_float(ex['totais']['repasses_previstos_sme_total'])
       totais_todas_as_contas['totais']['repasses_no_periodo_total'] += converte_string_value_formatada_para_float(ex['totais']['repasses_no_periodo_total'])
       totais_todas_as_contas['totais']['demais_creditos_no_periodo_total'] += converte_string_value_formatada_para_float(ex['totais']['demais_creditos_no_periodo_total'])
       totais_todas_as_contas['totais']['valor_total'] += converte_string_value_formatada_para_float(ex['totais']['valor_total'])
       totais_todas_as_contas['totais']['despesas_no_periodo_total'] += converte_string_value_formatada_para_float(ex['totais']['despesas_no_periodo_total'])
       totais_todas_as_contas['totais']['saldo_reprogramado_proximo_periodo_total'] += converte_string_value_formatada_para_float(ex['totais']['saldo_reprogramado_proximo_periodo_total'])
       totais_todas_as_contas['totais']['devolucoes_ao_tesouro_no_periodo_total'] += converte_string_value_formatada_para_float(ex['totais']['devolucoes_ao_tesouro_no_periodo_total'])
       totais_todas_as_contas['totais']['outros_creditos'] += converte_string_value_formatada_para_float(ex['totais']['outros_creditos'])

    # Formatando os valores após terem sido somados corretamente
    for chave, valor in totais_todas_as_contas.items():
        if type(valor) == dict:
            for c, v in valor.items():
                totais_todas_as_contas[chave][c] = formata_valor(v)

    return totais_todas_as_contas


def cria_execucao_fisica(dre, periodo, apenas_nao_publicadas, consolidado_dre, eh_consolidado_de_publicacoes_parciais=False):
    """BLOCO 3 - EXECUÇÃO FÍSICA"""

    publicada = not apenas_nao_publicadas

    quantidade_associacoes_ativas = Associacao.get_associacoes_ativas_no_periodo(periodo=periodo, dre=dre).count()

    # TODO Implementar contagem de regulares considerando o ano
    quantidade_regular = quantidade_associacoes_ativas

    cards = PrestacaoConta.dashboard(periodo.uuid, dre.uuid, add_aprovado_ressalva=True, add_info_devolvidas_retornadas=True, apenas_nao_publicadas=apenas_nao_publicadas)

    if consolidado_dre and consolidado_dre.eh_retificacao:
        prestacoes_do_consolidado = consolidado_dre.prestacoes_de_conta_do_consolidado_dre.all()

        quantidade_publicacoes_anteriores = ConsolidadoDRE.objects.filter(
            dre=dre,
            periodo=periodo
        ).exclude(
            id__gt=consolidado_dre.id
        ).aggregate(qtde_publicacoes_anteriores=Coalesce(Count('prestacoes_de_conta_do_consolidado_dre'), Value(0)))[
            'qtde_publicacoes_anteriores']

        quantidade_aprovada = prestacoes_do_consolidado.filter(status="APROVADA", publicada=publicada).count()
        quantidade_aprovada_ressalva = prestacoes_do_consolidado.filter(status="APROVADA_RESSALVA",
                                                                        publicada=publicada).count()
        quantidade_nao_aprovada = prestacoes_do_consolidado.filter(status="REPROVADA", publicada=publicada).count()
        # Fim Dados do Consolidado DRE Retificacao

    # Se não for o Consolidado de Publicações Parciais
    elif not eh_consolidado_de_publicacoes_parciais:
        # Dados do Consolidado DRE
        sequencia_de_publicacao_atual = ConsolidadoDRE.objects.filter(
            dre=dre,
            periodo=periodo
        ).aggregate(max_sequencia_de_publicacao=Coalesce(Max('sequencia_de_publicacao'), Value(0)))['max_sequencia_de_publicacao']

        consolidado_dre = ConsolidadoDRE.objects.filter(dre=dre, periodo=periodo, sequencia_de_publicacao=sequencia_de_publicacao_atual).last()

        prestacoes_do_consolidado = consolidado_dre.prestacoes_de_conta_do_consolidado_dre.all()

        quantidade_publicacoes_anteriores = ConsolidadoDRE.objects.filter(
            dre=dre,
            periodo=periodo
        ).exclude(
            uuid=consolidado_dre.uuid
        ).aggregate(qtde_publicacoes_anteriores=Coalesce(Count('prestacoes_de_conta_do_consolidado_dre'), Value(0)))['qtde_publicacoes_anteriores']

        quantidade_aprovada = prestacoes_do_consolidado.filter(status="APROVADA", publicada=publicada).count()
        quantidade_aprovada_ressalva = prestacoes_do_consolidado.filter(status="APROVADA_RESSALVA", publicada=publicada).count()
        quantidade_nao_aprovada = prestacoes_do_consolidado.filter(status="REPROVADA", publicada=publicada).count()
        # Fim Dados do Consolidado DRE
    else:
        quantidade_publicacoes_anteriores = ConsolidadoDRE.objects.filter(
            dre=dre,
            periodo=periodo
        ).aggregate(qtde_publicacoes_anteriores=Coalesce(Count('prestacoes_de_conta_do_consolidado_dre'), Value(0)))['qtde_publicacoes_anteriores']

        quantidade_aprovada = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'APROVADA'][0]
        quantidade_aprovada_ressalva = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'APROVADA_RESSALVA'][0]
        quantidade_nao_aprovada = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'REPROVADA'][0]


    quantidade_em_analise = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'EM_ANALISE'][0]
    quantidade_recebida = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'RECEBIDA'][0]
    quantidade_devolvida = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'DEVOLVIDA'][0]
    quantidade_nao_recebida = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'NAO_RECEBIDA'][0]

    if consolidado_dre and consolidado_dre.eh_retificacao:
        quantidade_nao_apresentada = \
            quantidade_associacoes_ativas \
            - quantidade_aprovada \
            - quantidade_aprovada_ressalva \
            - quantidade_nao_aprovada \
            - quantidade_em_analise \
            - quantidade_publicacoes_anteriores

    # (-) todos os outros status com exceção dos quantidade_recebida e quantidade_devolvida (Porque não aparecem nesse bloco)
    elif not eh_consolidado_de_publicacoes_parciais:
        quantidade_nao_apresentada = \
            quantidade_associacoes_ativas \
            - quantidade_aprovada \
            - quantidade_aprovada_ressalva \
            - quantidade_nao_aprovada\
            - quantidade_em_analise \
            - quantidade_publicacoes_anteriores
    else:
        quantidade_nao_apresentada = \
            quantidade_associacoes_ativas \
            - quantidade_aprovada \
            - quantidade_aprovada_ressalva \
            - quantidade_nao_aprovada\
            - quantidade_em_analise

    total = \
        quantidade_nao_recebida \
        + quantidade_aprovada \
        + quantidade_aprovada_ressalva \
        + quantidade_nao_aprovada \
        + quantidade_em_analise \
        + quantidade_recebida \
        + quantidade_devolvida

    execucao_fisica = {
        "ues_da_dre": dre.unidades_da_dre.count(),
        "ues_com_associacao": quantidade_associacoes_ativas,
        "associacoes_regulares": quantidade_regular,
        "aprovada": quantidade_aprovada,
        "aprovada_ressalva": quantidade_aprovada_ressalva,
        "rejeitada": quantidade_nao_aprovada,
        "analise": quantidade_em_analise,
        "nao_apresentadas": quantidade_nao_apresentada,
        "publicadas_anteriormente": quantidade_publicacoes_anteriores,
        "total": total
    }

    return execucao_fisica


def cria_associacoes_nao_regularizadas(dre, periodo):
    from .regularidade_associacao_service import get_lista_associacoes_e_status_regularidade_no_ano

    ano = str(periodo.data_inicio_realizacao_despesas.year)
    ano_analise_regularidade = AnoAnaliseRegularidade.objects.get(ano=ano)
    associacoes_pendentes = get_lista_associacoes_e_status_regularidade_no_ano(
        dre=dre,
        ano_analise_regularidade=ano_analise_regularidade,
        filtro_nome=None,
        filtro_tipo_unidade=None,
        filtro_status='PENDENTE'
    )

    qtde_associacoes_pendentes = len(associacoes_pendentes)

    dados = []
    regularizacao = {}

    if qtde_associacoes_pendentes > 0:
        regularizacao["todas_regularizadas"] = False

        for linha, associacao in enumerate(associacoes_pendentes):
            dado = {
                "linha": linha + 1,
                "associacao": associacao['associacao']['nome'],
                "motivo": associacao['motivo']
            }

            dados.append(dado)

        regularizacao["dados"] = dados
    else:
        regularizacao["todas_regularizadas"] = True
        regularizacao["texto"] = "Todas as Associações constam como regularizadas, no que se refere à habilitação."

    return regularizacao


def cria_dados_fisicos_financeiros(dre, periodo, apenas_nao_publicadas, eh_consolidado_de_publicacoes_parciais, consolidado_dre):
    """Dados Físicos financeiros do bloco 4."""
    from .relatorio_consolidado_service import get_status_label, informacoes_execucao_financeira_unidades_do_consolidado_dre

    total_saldo_reprogramado_anterior_custeio = 0
    total_repasse_custeio = 0
    total_devolucao_custeio = 0
    total_demais_creditos_custeio = 0
    total_despesas_custeio = 0
    total_saldo_custeio = 0
    total_outros_creditos_custeio = 0
    total_valor_total_disponivel_custeio = 0

    total_saldo_reprogramado_anterior_capital = 0
    total_repasse_capital = 0
    total_devolucao_capital = 0
    total_demais_creditos_capital = 0
    total_despesas_capital = 0
    total_saldo_capital = 0
    total_outros_creditos_capital = 0
    total_valor_total_disponivel_capital = 0

    total_saldo_reprogramado_anterior_livre = 0
    total_repasse_livre = 0
    total_receita_rendimento_livre = 0
    total_devolucao_livre = 0
    total_demais_creditos_livre = 0
    total_saldo_livre = 0
    total_outros_creditos_livre = 0
    total_devolucoes_ao_tesouro = 0
    total_valor_total_disponivel_livre = 0

    informacao_unidades = informacoes_execucao_financeira_unidades_do_consolidado_dre(dre, periodo, apenas_nao_publicadas, eh_consolidado_de_publicacoes_parciais, consolidado_dre)

    lista = []

    for linha, infos in enumerate(informacao_unidades):

        lista_de_informacoes_por_conta = []

        dados = {
            "ordem": linha + 1,
            "associacao": {
                "nome": infos["unidade"]["nome"],
                "codigo_eol": infos["unidade"]["codigo_eol"],
                "tipo": infos["unidade"]["tipo_unidade"],
            },
            "situacao_pc": get_status_label(infos['status_prestacao_contas']),
            "referencia_consolidado": f"{infos['referencia_consolidado']}" if infos['referencia_consolidado'] else None,
        }

        for info in infos['por_tipo_de_conta']:

            if info['valores']: # Verifica se existe valores, senão será exibida mensagem Não houve movimentação financeira por conta

                outros_creditos_total = 0
                valor_total_disponivel_total = 0
                for index in range(3):
                    if index == 0:
                        saldo_reprogramado_anterior_custeio = info.get("valores").get('saldo_reprogramado_periodo_anterior_custeio')
                        repasse_custeio = info.get("valores").get('repasses_no_periodo_custeio')
                        devolucao_custeio = info.get("valores").get('receitas_devolucao_no_periodo_custeio')
                        demais_creditos_custeio = info.get("valores").get('demais_creditos_no_periodo_custeio')
                        despesas_custeio = info.get("valores").get('despesas_no_periodo_custeio')
                        saldo_custeio = info.get("valores").get('saldo_reprogramado_proximo_periodo_custeio')
                        total_receitas_custeio = info.get("valores").get('receitas_totais_no_periodo_custeio')

                        outros_creditos_custeio = total_receitas_custeio - repasse_custeio

                        outros_creditos_total += outros_creditos_custeio

                        valor_total_disponivel_custeio = info.get("valores").get('saldo_reprogramado_periodo_anterior_custeio')\
                                                         + info.get("valores").get('repasses_no_periodo_custeio') \
                                                         + outros_creditos_custeio

                        valor_total_disponivel_total += valor_total_disponivel_custeio

                        custeio = {
                            "saldo_reprogramado_anterior_custeio": formata_valor(saldo_reprogramado_anterior_custeio),
                            "repasse_custeio": formata_valor(repasse_custeio),
                            "devolucao_custeio": formata_valor(devolucao_custeio),
                            "demais_creditos_custeio": formata_valor(demais_creditos_custeio),
                            "despesas_custeio": formata_valor(despesas_custeio),
                            "saldo_custeio": formata_valor(saldo_custeio),
                            "outros_creditos": formata_valor(outros_creditos_custeio),
                            "valor_total_disponivel_custeio": formata_valor(valor_total_disponivel_custeio),
                        }

                        dados["custeio"] = custeio

                        total_saldo_reprogramado_anterior_custeio += saldo_reprogramado_anterior_custeio
                        total_repasse_custeio += repasse_custeio
                        total_devolucao_custeio += devolucao_custeio
                        total_demais_creditos_custeio += demais_creditos_custeio
                        total_despesas_custeio += despesas_custeio
                        total_saldo_custeio += saldo_custeio
                        total_outros_creditos_custeio += outros_creditos_custeio
                        total_valor_total_disponivel_custeio += valor_total_disponivel_custeio

                    elif index == 1:
                        saldo_reprogramado_anterior_capital = info.get("valores").get(
                            'saldo_reprogramado_periodo_anterior_capital')
                        repasse_capital = info.get("valores").get('repasses_no_periodo_capital')
                        devolucao_capital = info.get("valores").get('receitas_devolucao_no_periodo_capital')
                        demais_creditos_capital = info.get("valores").get('demais_creditos_no_periodo_capital')
                        despesas_capital = info.get("valores").get('despesas_no_periodo_capital')
                        saldo_capital = info.get("valores").get('saldo_reprogramado_proximo_periodo_capital')
                        total_receitas_capital = info.get("valores").get('receitas_totais_no_periodo_capital')

                        outros_creditos_capital = total_receitas_capital - repasse_capital
                        outros_creditos_total += outros_creditos_capital

                        valor_total_disponivel_capital = info.get("valores").get('saldo_reprogramado_periodo_anterior_capital')\
                                                         + info.get("valores").get('repasses_no_periodo_capital') \
                                                         + outros_creditos_capital

                        valor_total_disponivel_total += valor_total_disponivel_capital

                        capital = {
                            "saldo_reprogramado_anterior_capital": formata_valor(saldo_reprogramado_anterior_capital),
                            "repasse_capital": formata_valor(repasse_capital),
                            "devolucao_capital": formata_valor(devolucao_capital),
                            "demais_creditos_capital": formata_valor(demais_creditos_capital),
                            "despesas_capital": formata_valor(despesas_capital),
                            "saldo_capital": formata_valor(saldo_capital),
                            "outros_creditos": formata_valor(outros_creditos_capital),
                            "valor_total_disponivel_capital": formata_valor(valor_total_disponivel_capital)
                        }

                        dados["capital"] = capital

                        total_saldo_reprogramado_anterior_capital += saldo_reprogramado_anterior_capital
                        total_repasse_capital += repasse_capital
                        total_devolucao_capital += devolucao_capital
                        total_demais_creditos_capital += demais_creditos_capital
                        total_despesas_capital += despesas_capital
                        total_saldo_capital += saldo_capital
                        total_outros_creditos_capital += outros_creditos_capital
                        total_valor_total_disponivel_capital += valor_total_disponivel_capital
                    else:
                        saldo_reprogramado_anterior_livre = info.get("valores").get('saldo_reprogramado_periodo_anterior_livre')
                        repasse_livre = info.get("valores").get('repasses_no_periodo_livre')
                        receita_rendimento_livre = info.get("valores").get('receitas_rendimento_no_periodo_livre')
                        devolucao_livre = info.get("valores").get('receitas_devolucao_no_periodo_livre')
                        demais_creditos_livre = info.get("valores").get('demais_creditos_no_periodo_livre')
                        saldo_livre = info.get("valores").get('saldo_reprogramado_proximo_periodo_livre')
                        total_receitas_livre = info.get("valores").get('receitas_totais_no_periodo_livre')

                        outros_creditos_livre = total_receitas_livre - repasse_livre
                        outros_creditos_total += outros_creditos_livre

                        valor_total_disponivel_livre = info.get("valores").get('saldo_reprogramado_periodo_anterior_livre')\
                                                         + info.get("valores").get('repasses_no_periodo_livre') \
                                                         + outros_creditos_livre

                        valor_total_disponivel_total += valor_total_disponivel_livre

                        # Recupera o valor total de devoluções ao tesouro da associacao
                        devolucoes_ao_tesouro = info.get('valores').get('devolucoes_ao_tesouro_no_periodo_total')

                        livre = {
                            "saldo_reprogramado_anterior_livre": formata_valor(saldo_reprogramado_anterior_livre),
                            "repasse_livre": formata_valor(repasse_livre),
                            "receita_rendimento_livre": formata_valor(receita_rendimento_livre),
                            "devolucao_livre": formata_valor(devolucao_livre),
                            "demais_creditos_livre": formata_valor(demais_creditos_livre),
                            "saldo_livre": formata_valor(saldo_livre),
                            "devolucoes_ao_tesouro": formata_valor(devolucoes_ao_tesouro),
                            "outros_creditos": formata_valor(outros_creditos_livre),
                            "valor_total_disponivel_livre": formata_valor(valor_total_disponivel_livre)
                        }

                        dados["livre"] = livre

                        total_saldo_reprogramado_anterior_livre += saldo_reprogramado_anterior_livre
                        total_repasse_livre += repasse_livre
                        total_receita_rendimento_livre += receita_rendimento_livre
                        total_devolucao_livre += devolucao_livre
                        total_demais_creditos_livre += demais_creditos_livre
                        total_saldo_livre += saldo_livre
                        total_devolucoes_ao_tesouro += devolucoes_ao_tesouro
                        total_outros_creditos_livre += outros_creditos_livre
                        total_valor_total_disponivel_livre += valor_total_disponivel_livre

                saldo_reprogramado_periodo_anterior_total = info.get("valores").get('saldo_reprogramado_periodo_anterior_total')
                repasses_no_periodo_total = info.get("valores").get('repasses_no_periodo_total')
                outros_creditos_total = outros_creditos_total
                valor_total_disponivel_total = valor_total_disponivel_total
                despesas_no_periodo_total = info.get('valores').get('despesas_no_periodo_total')
                saldo_reprogramado_proximo_periodo_total = info.get('valores').get('saldo_reprogramado_proximo_periodo_total')
                devolucoes_ao_tesouro_no_periodo_total = info.get('valores').get('devolucoes_ao_tesouro_no_periodo_total')

                totais = {
                    'saldo_reprogramado_periodo_anterior_total': formata_valor(saldo_reprogramado_periodo_anterior_total),
                    'repasses_no_periodo_total': formata_valor(repasses_no_periodo_total),
                    'outros_creditos_total': formata_valor(outros_creditos_total),
                    'valor_total_disponivel_total': formata_valor(valor_total_disponivel_total),
                    'despesas_no_periodo_total': formata_valor(despesas_no_periodo_total),
                    'saldo_reprogramado_proximo_periodo_total': formata_valor(saldo_reprogramado_proximo_periodo_total),
                    'devolucoes_ao_tesouro_no_periodo_total': formata_valor(devolucoes_ao_tesouro_no_periodo_total),
                }

                dados['totais'] = totais

                lista_de_informacoes_por_conta.append(
                    {
                        'tipo_conta': info.get('tipo_conta'),
                        'encerrada_em': info.get('encerrada_em'),
                        'exibe_valores': True,
                        'mensagem_movimentacao_financeira': '',
                        'custeio': dados["custeio"],
                        'capital': dados["capital"],
                        'livre': dados["livre"],
                        'totais': dados["totais"],
                    }
                )
            else:
                lista_de_informacoes_por_conta.append(
                    {
                        'tipo_conta': info.get('tipo_conta'),
                        'encerrada_em': info.get('encerrada_em'),
                        'exibe_valores': False,
                        'mensagem_movimentacao_financeira': 'Conta inativa.',
                        'custeio': None,
                        'capital': None,
                        'livre': None,
                        'totais': None,
                    }
                )
            # Ordena a lista para primeiro vir todas as contas com valores para não quebrar o layout do template e exibir a devolução ao tesouro
            # lista_de_informacoes_por_conta = sorted(lista_de_informacoes_por_conta, key=lambda d: d['exibe_valores'], reverse=True)

        # TERMINA AQUI

        lista.append({
            'ordem': dados['ordem'],
            'associacao': dados['associacao'],
            'por_tipo_de_conta': lista_de_informacoes_por_conta,
            "situacao_pc": dados['situacao_pc'],
            "referencia_consolidado": dados['referencia_consolidado'] if eh_consolidado_de_publicacoes_parciais else None,
        })

    informacoes = {
        "lista": lista,
    }

    return informacoes


def cria_assinaturas_dre(dre):
    """Bloco 5 - Autenticação: Parte de assinaturas"""

    membros = []

    if ParametrosDre.objects.all():
        comissoes = ParametrosDre.get().comissao_exame_contas
        membros = comissoes.membros.filter(dre=dre).values("rf", "nome", "cargo")
    else:
        LOGGER.info(f"Não foi encontrado nenhum Parametro DRE, verificar no admin")

    dados = {
        "membros": membros,
        "data_assinatura": date.today().strftime("%d/%m/%Y")
    }

    return dados


def cria_data_geracao_documento(usuario, dre, parcial, previa=False):
    eh_parcial = "parcial" if parcial['parcial'] else "final"

    if previa:
        previa_ou_final = 'Versão prévia'
    else:
        previa_ou_final = f'Versão {eh_parcial}'

    LOGGER.info("Iniciando rodapé...")
    data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    quem_gerou = "" if usuario == "" else f"pelo usuário {usuario}"
    dre = formata_nome_dre(dre)
    texto = f"DRE {dre} - {previa_ou_final} do documento gerado {quem_gerou}, via SIG-Escola, em {data_geracao}"
    return texto


def formata_data(data):
    data_formatada = " - "
    if data:
        d = datetime.strptime(str(data), '%Y-%m-%d')
        data_formatada = d.strftime("%d/%m/%Y")

    return f'{data_formatada}'


def formata_nome_dre(dre):
    if dre.nome:
        nome_dre = dre.nome.upper()
        if "DIRETORIA REGIONAL DE EDUCACAO" in nome_dre:
            nome_dre = nome_dre.replace("DIRETORIA REGIONAL DE EDUCACAO", "")
            nome_dre = nome_dre.strip()
            return nome_dre
        else:
            return nome_dre
    else:
        return ""


def formata_valor(valor):
    from babel.numbers import format_currency
    sinal, valor_formatado = format_currency(valor, 'BRL', locale='pt_BR').split('\xa0')
    sinal = '-' if '-' in sinal else ''
    return f'{sinal}{valor_formatado}'


def converte_string_value_formatada_para_float(string):
    result = 0
    if string:
        [num, dec] = string.rsplit(',')
        result += int(num.replace('.', ''))
        result += (int(dec) / 100)

    return result

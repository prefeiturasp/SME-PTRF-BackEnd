import logging
from datetime import datetime

from datetime import date

from sme_ptrf_apps.dre.models import JustificativaRelatorioConsolidadoDRE, AnoAnaliseRegularidade
from sme_ptrf_apps.core.models import Associacao, PrestacaoConta
from sme_ptrf_apps.dre.models import ParametrosDre


LOGGER = logging.getLogger(__name__)


def gerar_dados_demo_execucao_fisico_financeira(dre, periodo, tipo_conta, usuario, parcial=False):
    try:
        LOGGER.info("Gerando relatório consolidado...")

        cabecalho = cria_cabecalho(periodo, tipo_conta, parcial)
        data_geracao_documento = cria_data_geracao_documento(usuario, dre, parcial)
        identificacao_dre = cria_identificacao_dre(dre)
        execucao_financeira = cria_execucao_financeira(dre, periodo, tipo_conta)
        execucao_fisica = cria_execucao_fisica(dre, periodo)
        associacoes_nao_regularizadas = cria_associacoes_nao_regularizadas(dre, periodo)
        dados_fisicos_financeiros = cria_dados_fisicos_financeiros(dre, periodo, tipo_conta)
        assinatura_dre = cria_assinaturas_dre(dre)

        """
            Mapeamento campos x pdf - Campos usados em cada um dos blocos do PDF:

            Bloco 1 - Identificação
                cabecalho
                identificacao_dre

            Bloco 2 - Identificação Bancária e Saldo
                identificacao_conta

            Bloco 3 - Resumo por Ação
                resumo_por_acao

            Bloco 4 - Créditos
                creditos_demonstrados

            Bloco 5 - Despesas Demonstradas
                despesas_demonstradas

            Bloco 6 - Despesas Não Demonstradas
                despesas_nao_demonstradas

            Bloco 7 - Despesas de períodos anteriores não demonstradas
                despesas_anteriores_nao_demonstradas

            Bloco 8 - Justificativas e informações adicionais
                justificativas

            Bloco 9 - Assinaturas
                data_geracao
        """

        dados_demonstrativo = {
            "cabecalho": cabecalho,
            "data_geracao_documento": data_geracao_documento,
            "identificacao_dre": identificacao_dre,
            "execucao_financeira": execucao_financeira,
            "execucao_fisica": execucao_fisica,
            "associacoes_nao_regularizadas": associacoes_nao_regularizadas,
            "dados_fisicos_financeiros": dados_fisicos_financeiros,
            "assinatura_dre": assinatura_dre,
            "versao_relatorio": "PARCIAL" if parcial else "FINAL"
        }

    finally:
        LOGGER.info("DADOS DEMONSTRATIVO GERADO")

    return dados_demonstrativo


def cria_cabecalho(periodo, tipo_conta, parcial):
    LOGGER.info("Iniciando cabecalho...")

    cabecalho = {
        "periodo": str(periodo),
        "periodo_referencia": periodo.referencia,
        "periodo_data_inicio": formata_data(periodo.data_inicio_realizacao_despesas),
        "periodo_data_fim": formata_data(periodo.data_fim_realizacao_despesas),
        "conta": tipo_conta.nome,
        "status": "PARCIAL" if parcial else "FINAL"
    }

    return cabecalho


def cria_identificacao_dre(dre):
    """BLOCO 1 - IDENTIFICAÇÃO"""
    identificacao = {
        "nome_dre": formata_nome_dre(dre),
        "cnpj_dre": dre.dre_cnpj if dre.dre_cnpj else ""
    }

    return identificacao


def cria_execucao_financeira(dre, periodo, tipo_conta):
    """BLOCO 2 - EXECUÇÃO FINANCEIRA"""
    from .relatorio_consolidado_service import informacoes_execucao_financeira

    info = informacoes_execucao_financeira(dre, periodo, tipo_conta)

    # LINHA CUSTEIO

    valor_total_custeio = info['saldo_reprogramado_periodo_anterior_custeio'] + info['repasses_no_periodo_custeio'] + \
        info['receitas_devolucao_no_periodo_custeio'] + info['demais_creditos_no_periodo_custeio']

    outros_creditos = info['receitas_rendimento_no_periodo_livre'] + info['receitas_devolucao_no_periodo_custeio'] + \
        info['demais_creditos_no_periodo_custeio']

    custeio = {
        "saldo_reprogramado_periodo_anterior_custeio": formata_valor(info['saldo_reprogramado_periodo_anterior_custeio']),
        "repasses_previstos_sme_custeio": formata_valor(info['repasses_previstos_sme_custeio']),
        "repasses_no_periodo_custeio": formata_valor(info['repasses_no_periodo_custeio']),
        "demais_creditos_no_periodo_custeio": formata_valor(info['demais_creditos_no_periodo_custeio']),
        "valor_total_custeio": formata_valor(valor_total_custeio),
        "despesas_no_periodo_custeio": formata_valor(info['despesas_no_periodo_custeio']),
        "saldo_reprogramado_proximo_periodo_custeio": formata_valor(info['saldo_reprogramado_proximo_periodo_custeio']),
        "outros_creditos": formata_valor(outros_creditos)
    }

    # LINHA CAPITAL

    valor_total_capital = info['saldo_reprogramado_periodo_anterior_capital'] + info['repasses_no_periodo_capital'] + \
        info['receitas_devolucao_no_periodo_capital'] + info['demais_creditos_no_periodo_capital']

    outros_creditos = info['receitas_rendimento_no_periodo_livre'] + info['receitas_devolucao_no_periodo_capital'] + \
        info['demais_creditos_no_periodo_capital']

    capital = {
        "saldo_reprogramado_periodo_anterior_capital": formata_valor(info['saldo_reprogramado_periodo_anterior_capital']),
        "repasses_previstos_sme_capital": formata_valor(info['repasses_previstos_sme_capital']),
        "repasses_no_periodo_capital": formata_valor(info['repasses_no_periodo_capital']),
        "demais_creditos_no_periodo_capital": formata_valor(info['demais_creditos_no_periodo_capital']),
        "valor_total_capital": formata_valor(valor_total_capital),
        "despesas_no_periodo_capital": formata_valor(info['despesas_no_periodo_capital']),
        "saldo_reprogramado_proximo_periodo_capital": formata_valor(info['saldo_reprogramado_proximo_periodo_capital']),
        "outros_creditos": formata_valor(outros_creditos)
    }

    # LINHA RLA

    valor_total_livre = info['saldo_reprogramado_periodo_anterior_livre'] + \
        info['receitas_rendimento_no_periodo_livre'] + \
        info['repasses_no_periodo_livre'] + info['receitas_devolucao_no_periodo_livre'] + \
        info['demais_creditos_no_periodo_livre']

    outros_creditos = info['receitas_rendimento_no_periodo_livre'] + info['receitas_devolucao_no_periodo_livre'] + \
        info['demais_creditos_no_periodo_livre']

    rla = {
        "saldo_reprogramado_periodo_anterior_livre": formata_valor(info['saldo_reprogramado_periodo_anterior_livre']),
        "repasses_previstos_sme_livre": formata_valor(info['repasses_previstos_sme_livre']),
        "repasses_no_periodo_livre": formata_valor(info['repasses_no_periodo_livre']),
        "demais_creditos_no_periodo_livre": formata_valor(info['demais_creditos_no_periodo_livre']),
        "valor_total_livre": formata_valor(valor_total_livre),
        "saldo_reprogramado_proximo_periodo_livre": formata_valor(info['saldo_reprogramado_proximo_periodo_livre']),
        "devolucoes_ao_tesouro_no_periodo_total": formata_valor(info['devolucoes_ao_tesouro_no_periodo_total']),
        "outros_creditos": formata_valor(outros_creditos)
    }

    # LINHA TOTAIS

    valor_total = info['saldo_reprogramado_periodo_anterior_total'] + info['receitas_rendimento_no_periodo_livre'] + \
        info['repasses_no_periodo_total'] + info['receitas_devolucao_no_periodo_total'] + \
        info['demais_creditos_no_periodo_total']

    outros_creditos = info['receitas_rendimento_no_periodo_livre'] + \
        info['receitas_devolucao_no_periodo_total'] + info['demais_creditos_no_periodo_total']

    totais = {
        "saldo_reprogramado_periodo_anterior_total": formata_valor(info['saldo_reprogramado_periodo_anterior_total']),
        "repasses_previstos_sme_total": formata_valor(info['repasses_previstos_sme_total']),
        "repasses_no_periodo_total": formata_valor(info['repasses_no_periodo_total']),
        "demais_creditos_no_periodo_total": formata_valor(info['demais_creditos_no_periodo_total']),
        "valor_total": formata_valor(valor_total),
        "despesas_no_periodo_total": formata_valor(info['despesas_no_periodo_total']),
        "saldo_reprogramado_proximo_periodo_total": formata_valor(info['saldo_reprogramado_proximo_periodo_total']),
        "devolucoes_ao_tesouro_no_periodo_total": formata_valor(info['devolucoes_ao_tesouro_no_periodo_total']),
        "outros_creditos": formata_valor(outros_creditos)
    }

    # Justificativa
    justificativa = JustificativaRelatorioConsolidadoDRE.objects.filter(dre=dre).filter(
        tipo_conta=tipo_conta).filter(periodo=periodo).first()

    execucao_financeira = {
        "custeio": custeio,
        "capital": capital,
        "livre": rla,
        "totais": totais,
        "justificativa": justificativa.texto if justificativa else ''
    }

    return execucao_financeira


def cria_execucao_fisica(dre, periodo):
    """BLOCO 3 - EXECUÇÃO FÍSICA"""
    quantidade_ues_cnpj = Associacao.objects.filter(unidade__dre=dre).exclude(cnpj__exact='').count()

    # TODO Implementar contagem de regulares considerando o ano
    quantidade_regular = Associacao.objects.filter(unidade__dre=dre).exclude(cnpj__exact='').count()

    cards = PrestacaoConta.dashboard(periodo.uuid, dre.uuid, add_aprovado_ressalva=True)

    quantidade_aprovada = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'APROVADA'][0]
    quantidade_aprovada_ressalva = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'APROVADA_RESSALVA'][0]
    quantidade_nao_aprovada = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'REPROVADA'][0]
    quantidade_em_analise = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'EM_ANALISE'][0]
    quantidade_recebida = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'RECEBIDA'][0]
    quantidade_nao_recebida = [c['quantidade_prestacoes'] for c in cards if c['status'] == 'NAO_RECEBIDA'][0]

    quantidade_nao_apresentada = quantidade_ues_cnpj - quantidade_aprovada - quantidade_aprovada_ressalva - \
        quantidade_nao_aprovada - quantidade_recebida

    total = quantidade_aprovada + quantidade_aprovada_ressalva + quantidade_nao_apresentada + quantidade_nao_aprovada

    execucao_fisica = {
        "ues_da_dre": dre.unidades_da_dre.count(),
        "ues_com_associacao": quantidade_ues_cnpj,
        "ues_desativadas": 0,
        "associacoes_regulares": quantidade_regular,
        "aprovada": quantidade_aprovada,
        "aprovada_ressalva": quantidade_aprovada_ressalva,
        "rejeitada": quantidade_nao_aprovada,
        "analise": quantidade_em_analise,
        "nao_apresentadas": quantidade_nao_apresentada,
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


def cria_dados_fisicos_financeiros(dre, periodo, tipo_conta):
    """Dados Físicos financeiros do bloco 4."""
    from .relatorio_consolidado_service import informacoes_execucao_financeira_unidades, get_status_label

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

    total_devolucoes_ao_tesouro = 0

    informacao_unidades = informacoes_execucao_financeira_unidades(dre, periodo, tipo_conta)

    lista = []

    for linha, info in enumerate(informacao_unidades):
        saldo_custeio = 0
        saldo_capital = 0
        saldo_livre = 0

        dados = {
            "ordem": linha + 1,
            "associacao": {
                "nome": info["unidade"]["nome"],
                "codigo_eol": info["unidade"]["codigo_eol"],
                "tipo": info["unidade"]["tipo_unidade"],
            },
            "situacao_pc": get_status_label(info['status_prestacao_contas']),
            "custeio": None,
            "capital": None,
            "livre": None
        }

        for index in range(3):
            if index == 0:
                saldo_reprogramado_anterior_custeio = info.get("valores").get(
                    'saldo_reprogramado_periodo_anterior_custeio')
                repasse_custeio = info.get("valores").get('repasses_no_periodo_custeio')
                devolucao_custeio = info.get("valores").get('receitas_devolucao_no_periodo_custeio')
                demais_creditos_custeio = info.get("valores").get('demais_creditos_no_periodo_custeio')
                despesas_custeio = info.get("valores").get('despesas_no_periodo_custeio')
                saldo_custeio = info.get("valores").get('saldo_reprogramado_proximo_periodo_custeio')
                receitas_rendimento_livre = info.get("valores").get('receitas_rendimento_no_periodo_livre')

                outros_creditos = receitas_rendimento_livre + devolucao_custeio + demais_creditos_custeio

                custeio = {
                    "saldo_reprogramado_anterior_custeio": formata_valor(saldo_reprogramado_anterior_custeio),
                    "repasse_custeio": formata_valor(repasse_custeio),
                    "devolucao_custeio": formata_valor(devolucao_custeio),
                    "demais_creditos_custeio": formata_valor(demais_creditos_custeio),
                    "despesas_custeio": formata_valor(despesas_custeio),
                    "saldo_custeio": formata_valor(saldo_custeio),
                    "outros_creditos": formata_valor(outros_creditos)
                }

                dados["custeio"] = custeio

                total_saldo_reprogramado_anterior_custeio += saldo_reprogramado_anterior_custeio
                total_repasse_custeio += repasse_custeio
                total_devolucao_custeio += devolucao_custeio
                total_demais_creditos_custeio += demais_creditos_custeio
                total_despesas_custeio += despesas_custeio
                total_saldo_custeio += saldo_custeio
            elif index == 1:
                saldo_reprogramado_anterior_capital = info.get("valores").get(
                    'saldo_reprogramado_periodo_anterior_capital')
                repasse_capital = info.get("valores").get('repasses_no_periodo_capital')
                devolucao_capital = info.get("valores").get('receitas_devolucao_no_periodo_capital')
                demais_creditos_capital = info.get("valores").get('demais_creditos_no_periodo_capital')
                despesas_capital = info.get("valores").get('despesas_no_periodo_capital')
                saldo_capital = info.get("valores").get('saldo_reprogramado_proximo_periodo_capital')
                receitas_rendimento_livre = info.get("valores").get('receitas_rendimento_no_periodo_livre')

                outros_creditos = receitas_rendimento_livre + devolucao_capital + demais_creditos_capital

                capital = {
                    "saldo_reprogramado_anterior_capital": formata_valor(saldo_reprogramado_anterior_capital),
                    "repasse_capital": formata_valor(repasse_capital),
                    "devolucao_capital": formata_valor(devolucao_capital),
                    "demais_creditos_capital": formata_valor(demais_creditos_capital),
                    "despesas_capital": formata_valor(despesas_capital),
                    "saldo_capital": formata_valor(saldo_capital),
                    "outros_creditos": formata_valor(outros_creditos)
                }

                dados["capital"] = capital

                total_saldo_reprogramado_anterior_capital += saldo_reprogramado_anterior_capital
                total_repasse_capital += repasse_capital
                total_devolucao_capital += devolucao_capital
                total_demais_creditos_capital += demais_creditos_capital
                total_despesas_capital += despesas_capital
                total_saldo_capital += saldo_capital
            else:
                saldo_reprogramado_anterior_livre = info.get("valores").get('saldo_reprogramado_periodo_anterior_livre')
                repasse_livre = info.get("valores").get('repasses_no_periodo_livre')
                receita_rendimento_livre = info.get("valores").get('receitas_rendimento_no_periodo_livre')
                devolucao_livre = info.get("valores").get('receitas_devolucao_no_periodo_livre')
                demais_creditos_livre = info.get("valores").get('demais_creditos_no_periodo_livre')
                saldo_livre = info.get("valores").get('saldo_reprogramado_proximo_periodo_livre')

                outros_creditos = receita_rendimento_livre + devolucao_livre + demais_creditos_livre

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
                    "outros_creditos": formata_valor(outros_creditos)
                }

                dados["livre"] = livre

                total_saldo_reprogramado_anterior_livre += saldo_reprogramado_anterior_livre

                total_repasse_livre += repasse_livre

                total_receita_rendimento_livre += receita_rendimento_livre

                total_devolucao_livre += devolucao_livre

                total_demais_creditos_livre += demais_creditos_livre

                total_saldo_livre += saldo_livre

                total_devolucoes_ao_tesouro += devolucoes_ao_tesouro

        lista.append(dados)

    # Calcula totais de outros creditos
    total_outros_creditos_custeio = total_receita_rendimento_livre + \
        total_devolucao_custeio + total_demais_creditos_custeio

    total_outros_creditos_capital = total_receita_rendimento_livre + \
        total_devolucao_capital + total_demais_creditos_capital

    total_outros_creditos_livre = total_receita_rendimento_livre + \
        total_devolucao_livre + total_demais_creditos_livre

    totais = {
        "custeio": {
            "total_saldo_reprogramado_anterior_custeio": formata_valor(total_saldo_reprogramado_anterior_custeio),
            "total_repasse_custeio": formata_valor(total_repasse_custeio),
            "total_devolucao_custeio": formata_valor(total_devolucao_custeio),
            "total_demais_creditos_custeio": formata_valor(total_demais_creditos_custeio),
            "total_despesas_custeio": formata_valor(total_despesas_custeio),
            "total_saldo_custeio": formata_valor(total_saldo_custeio),
            "total_outros_creditos": formata_valor(total_outros_creditos_custeio)
        },
        "capital": {
            "total_saldo_reprogramado_anterior_capital": formata_valor(total_saldo_reprogramado_anterior_capital),
            "total_repasse_capital": formata_valor(total_repasse_capital),
            "total_devolucao_capital": formata_valor(total_devolucao_capital),
            "total_demais_creditos_capital": formata_valor(total_demais_creditos_capital),
            "total_despesas_capital": formata_valor(total_despesas_capital),
            "total_saldo_capital": formata_valor(total_saldo_capital),
            "total_outros_creditos": formata_valor(total_outros_creditos_capital)
        },
        "livre": {
            "total_saldo_reprogramado_anterior_livre": formata_valor(total_saldo_reprogramado_anterior_livre),
            "total_repasse_livre": formata_valor(total_repasse_livre),
            "total_receita_rendimento_livre": formata_valor(total_receita_rendimento_livre),
            "total_devolucao_livre": formata_valor(total_devolucao_livre),
            "total_demais_creditos_livre": formata_valor(total_demais_creditos_livre),
            "total_saldo_livre": formata_valor(total_saldo_livre),
            "total_devolucoes_ao_tesouro": formata_valor(total_devolucoes_ao_tesouro),
            "total_outros_creditos": formata_valor(total_outros_creditos_livre)
        }
    }

    informacoes = {
        "lista": lista,
        "totais": totais
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


def cria_data_geracao_documento(usuario, dre, parcial=False):
    LOGGER.info("Iniciando rodapé...")
    data_geracao = date.today().strftime("%d/%m/%Y")
    tipo_texto = "parcial" if parcial else "final"
    quem_gerou = "" if usuario == "" else f"pelo usuário {usuario}"
    dre = formata_nome_dre(dre)
    texto = f"DRE {dre} - Documento {tipo_texto} gerado {quem_gerou}, via SIG-Escola, em: {data_geracao}"
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

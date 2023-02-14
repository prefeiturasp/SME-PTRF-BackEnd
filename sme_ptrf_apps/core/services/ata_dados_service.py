import logging
from datetime import datetime

from sme_ptrf_apps.core.models import PresenteAta, DevolucaoAoTesouro, Associacao, Periodo
from sme_ptrf_apps.core.services.prestacao_contas_services import informacoes_financeiras_para_atas
from sme_ptrf_apps.core.services.associacoes_service import retorna_repasses_pendentes_periodos_ate_agora
from sme_ptrf_apps.utils.numero_por_extenso import real

LOGGER = logging.getLogger(__name__)


def gerar_dados_ata(prestacao_de_contas=None, ata=None, usuario=None):
    try:
        cabecalho = cria_cabecalho(ata)
        info_financeira_ata = informacoes_financeiras_para_atas(prestacao_de_contas)
        presentes_na_ata = presentes_ata(ata)
        retificacoes = ata.retificacoes
        devolucoes_ao_tesouro = devolucoes_ao_tesouro_ata(ata, prestacao_de_contas)
        repasses_pendentes = get_repasses_pendentes(ata)
        # comentando bloco pagamento antecipado
        # despesas_com_pagamento_antecipado = get_despesas_com_pagamento_antecipado(ata=ata)
        dados_ata = {
            "cabecalho": cabecalho,
            "retificacoes": retificacoes,
            "devolucoes_ao_tesouro": devolucoes_ao_tesouro,
            "info_financeira_ata": info_financeira_ata,
            "dados_da_ata": ata,
            "dados_texto_da_ata": dados_texto_ata(ata, usuario),
            "presentes_na_ata": presentes_na_ata,
            "repasses_pendentes": repasses_pendentes,
            "justificativa_repasses_pendentes": ata.justificativa_repasses_pendentes,
            # "despesas_com_pagamento_antecipado": despesas_com_pagamento_antecipado,
        }
    finally:
        LOGGER.info("Dados da ata gerado com sucesso")

    return dados_ata


def get_despesas_com_pagamento_antecipado(ata):
    periodo = ata.periodo
    associacao = ata.associacao

    from sme_ptrf_apps.core.services.associacoes_service import retorna_despesas_com_pagamento_antecipado_por_periodo

    despesas_com_pagamento_antecipado = retorna_despesas_com_pagamento_antecipado_por_periodo(associacao=associacao, periodo=periodo)

    return despesas_com_pagamento_antecipado


def get_repasses_pendentes(ata):
    associacao = Associacao.by_uuid(ata.associacao.uuid)
    periodo = Periodo.by_uuid(ata.periodo.uuid)

    dados = retorna_repasses_pendentes_periodos_ate_agora(associacao, periodo)

    return dados


def devolucoes_ao_tesouro_ata(ata, prestacao_de_contas):
    lista_de_devolucoes = []

    if ata.tipo_ata == 'RETIFICACAO':
        devolucoes = DevolucaoAoTesouro.objects.filter(prestacao_conta=prestacao_de_contas)

        for devolucao in devolucoes:
            despesa = devolucao.despesa

            devs = {
                "tipo": devolucao.tipo.nome if devolucao.tipo.nome else '',
                "data": formata_data(devolucao.data) if devolucao.data else '',
                "numero_documento": despesa.numero_documento if despesa.numero_documento else '',
                "cpf_cnpj_fornecedor": despesa.cpf_cnpj_fornecedor if despesa.cpf_cnpj_fornecedor else '',
                "valor": devolucao.valor if devolucao.valor else '',
                "motivo": devolucao.motivo if devolucao.motivo else '',
            }

            lista_de_devolucoes.append(devs)

    return lista_de_devolucoes


def presentes_ata(ata):
    from .membro_associacao_service import retorna_membros_do_conselho_fiscal_por_associacao
    presentes_ata_membros = PresenteAta.objects.filter(ata=ata).filter(membro=True).values()
    presentes_ata_nao_membros = PresenteAta.objects.filter(ata=ata).filter(membro=False).filter(
        conselho_fiscal=False).order_by('nome').values()

    presentes_ata_conselho_fiscal = retorna_membros_do_conselho_fiscal_por_associacao(ata.associacao)

    presentes_na_ata = {
        "presentes_ata_membros": presentes_ata_membros,
        "presentes_ata_nao_membros": presentes_ata_nao_membros,
        "presentes_ata_conselho_fiscal": presentes_ata_conselho_fiscal,
    }

    return presentes_na_ata


def dados_texto_ata(ata, usuario):
    periodo = ata.periodo.referencia.split('.')

    if periodo[1] == 'u'.lower():
        periodo_referencia = f"repasse único de {periodo[0]}"
    else:
        periodo_referencia = f"{periodo[1]}° repasse de {periodo[0]}"

    dados_texto_da_ata = {
        "prestacao_conta": ata.prestacao_conta if ata.prestacao_conta else "___",
        "periodo": ata.periodo if ata.periodo else "___",
        "associacao_nome": ata.associacao.nome if ata.associacao.nome else "___",
        "unidade_cod_eol": ata.associacao.unidade.codigo_eol if ata.associacao.unidade.codigo_eol else "___",
        "unidade_tipo": ata.associacao.unidade.tipo_unidade if ata.associacao.unidade.tipo_unidade else "___",
        "unidade_nome": ata.associacao.unidade.nome if ata.associacao.unidade.nome else "___",
        "local_reuniao": ata.local_reuniao if ata.local_reuniao else "___",
        "periodo_referencia": periodo_referencia if periodo_referencia else "___",
        "presidente_reuniao": ata.presidente_reuniao if ata.presidente_reuniao else "___",
        "cargo_presidente_reuniao": ata.cargo_presidente_reuniao if ata.cargo_presidente_reuniao else "___",
        "secretario_reuniao": ata.secretario_reuniao if ata.secretario_reuniao else "___",
        "cargo_secretaria_reuniao": ata.cargo_secretaria_reuniao if ata.cargo_secretaria_reuniao else "___",
        "data_reuniao_por_extenso": data_por_extenso(ata.data_reuniao),
        "comentarios": ata.comentarios,
        "parecer_conselho": ata.parecer_conselho,
        "usuario": usuario,
        "hora_reuniao": ata.hora_reuniao.strftime('%H:%M')
    }

    return dados_texto_da_ata


def data_por_extenso(data):
    if not data:
        return 'Aos ___ dias do mês de ___ de ___'

    mes_ext = {1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril', 5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
               9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'}
    str_data = str(data)
    ano, mes, dia = str_data.split("-")

    if data.day == 1:
        data_extenso = f'No primeiro dia do mês de {mes_ext[int(mes)]} de {real(ano)}'
    else:
        data_extenso = f'Aos {real(dia)} dias do mês de {mes_ext[int(mes)]} de {real(ano)}'

    return data_extenso


def cria_cabecalho(ata):
    """ GERA CABECALHO DOCUMENTO EM PDF ATA """

    cabecalho = {
        "titulo": "Programa de Transferência de Recursos Financeiros - PTRF",
        "subtitulo": "Prestação de Contas",
        "tipo_ata": 'Apresentação' if ata.tipo_ata == 'APRESENTACAO' else 'Retificação',
        "periodo_referencia": ata.periodo.referencia,
        "periodo_data_inicio": formata_data(
            ata.periodo.data_inicio_realizacao_despesas) if ata.periodo.data_inicio_realizacao_despesas else "___",
        "periodo_data_fim": formata_data(
            ata.periodo.data_fim_realizacao_despesas) if ata.periodo.data_fim_realizacao_despesas else "___",
    }

    return cabecalho


def formata_data(data):
    data_formatada = " - "
    if data:
        d = datetime.strptime(str(data), '%Y-%m-%d')
        data_formatada = d.strftime("%d/%m/%Y")

    return f'{data_formatada}'

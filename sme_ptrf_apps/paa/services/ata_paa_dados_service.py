import logging
from datetime import datetime

from sme_ptrf_apps.paa.models import AtaPaa, ParticipanteAtaPaa
from sme_ptrf_apps.paa.services.dados_documento_paa_service import (
    criar_grupos_prioridades,
    criar_atividades_estatutarias
)
from sme_ptrf_apps.utils.numero_por_extenso import real

LOGGER = logging.getLogger(__name__)


def gerar_dados_ata_paa(ata_paa: AtaPaa, usuario=None):
    """
    Gera os dados necessários para a geração do PDF da ata PAA
    """
    try:
        paa = ata_paa.paa
        cabecalho = cria_cabecalho(ata_paa)
        identificacao_associacao = criar_identificacao_associacao_ata(paa)
        presentes_na_ata = presentes_ata_paa(ata_paa)
        prioridades = criar_grupos_prioridades(paa)
        atividades_estatutarias = criar_atividades_estatutarias(paa)
        dados_texto_ata = dados_texto_ata_paa(ata_paa, usuario)

        # Calcular números dos blocos dinamicamente
        numeros_blocos = calcular_numeros_blocos(prioridades, atividades_estatutarias)

        dados_ata = {
            "cabecalho": cabecalho,
            "identificacao_associacao": identificacao_associacao,
            "dados_da_ata": ata_paa,
            "dados_texto_da_ata": dados_texto_ata,
            "presentes_na_ata": presentes_na_ata,
            "prioridades": prioridades,
            "atividades_estatutarias": atividades_estatutarias,
            "numeros_blocos": numeros_blocos,
        }
        LOGGER.info("Dados da ata PAA gerados com sucesso")
        LOGGER.info("Dados da ata PAA %s", dados_ata)
        return dados_ata
    except Exception as e:
        LOGGER.error(f"Erro ao gerar dados da ata PAA: {str(e)}", exc_info=True)
        raise


def calcular_numeros_blocos(prioridades, atividades_estatutarias):
    """
    Calcula os números dos blocos dinamicamente baseado nos blocos que existem.
    Similar à função nome_blocos do relatório de acertos.
    """
    numeros = {}
    numero_bloco = 2  # Começa em 2 porque Bloco 1 e 2 são fixos

    # Encontrar os grupos de prioridades na ordem correta
    grupo_ptrf = None
    grupo_pdde = None
    grupo_recursos_proprios = None

    for grupo in prioridades:
        titulo = grupo.get('titulo', '')
        items = grupo.get('items', [])

        if titulo == "Prioridades PTRF" and items and len(items) > 0:
            grupo_ptrf = grupo
        elif titulo == "Prioridades PDDE" and items and len(items) > 0:
            grupo_pdde = grupo
        elif titulo == "Prioridades Recursos próprios" and items and len(items) > 0:
            grupo_recursos_proprios = grupo

    # Calcular números na ordem correta: PTRF, PDDE, Recursos Próprios
    if grupo_ptrf:
        numero_bloco += 1
        numeros['ptrf'] = numero_bloco

    if grupo_pdde:
        numero_bloco += 1
        numeros['pdde'] = numero_bloco

    if grupo_recursos_proprios:
        numero_bloco += 1
        numeros['recursos_proprios'] = numero_bloco

    # Bloco de Atividades Estatutárias (sempre após os blocos de prioridades)
    if atividades_estatutarias and len(atividades_estatutarias) > 0:
        numero_bloco += 1
        numeros['atividades_estatutarias'] = numero_bloco

    # Bloco de Manifestações (sempre após Atividades Estatutárias)
    numero_bloco += 1
    numeros['manifestacoes'] = numero_bloco

    # Bloco de Lista de Presença (sempre após Manifestações)
    numero_bloco += 1
    numeros['lista_presenca'] = numero_bloco

    return numeros


def presentes_ata_paa(ata_paa: AtaPaa):
    """
    Retorna os presentes na ata PAA organizados por tipo
    """
    presentes_ata_membros_ordenados = ParticipanteAtaPaa.participantes_ordenados_por_cargo(
        ata_paa, True
    )
    # Converter para lista de dicionários incluindo professor_gremio
    presentes_ata_membros_list = []
    for presente in presentes_ata_membros_ordenados:
        presente_dict = {
            'uuid': presente['uuid'],
            'nome': presente['nome'],
            'cargo': presente['cargo'],
            'presente': presente['presente'],
            'professor_gremio': presente.get('professor_gremio', False),
        }
        presentes_ata_membros_list.append(presente_dict)

    presentes_ata_nao_membros = ParticipanteAtaPaa.objects.filter(
        ata_paa=ata_paa, membro=False, conselho_fiscal=False
    ).order_by('nome').values('uuid', 'nome', 'cargo', 'presente', 'professor_gremio')

    presentes_na_ata = {
        "presentes_ata_membros": presentes_ata_membros_list,
        "presentes_ata_nao_membros": list(presentes_ata_nao_membros),
    }

    return presentes_na_ata


def dados_texto_ata_paa(ata_paa: AtaPaa, usuario=None):
    """
    Gera os dados de texto da ata PAA
    """
    paa = ata_paa.paa
    associacao = paa.associacao

    dados_texto_da_ata = {
        "associacao_nome": associacao.nome if associacao.nome else "___",
        "unidade_cod_eol": associacao.unidade.codigo_eol if associacao.unidade.codigo_eol else "___",
        "unidade_tipo": associacao.unidade.tipo_unidade if associacao.unidade.tipo_unidade else "___",
        "unidade_nome": associacao.unidade.nome if associacao.unidade.nome else "___",
        "local_reuniao": ata_paa.local_reuniao if ata_paa.local_reuniao else "___",
        "periodo_referencia": paa.periodo_paa.referencia if paa.periodo_paa.referencia else "___",
        "presidente_reuniao": ata_paa.presidente_da_reuniao.nome if ata_paa.presidente_da_reuniao else "___",
        "cargo_presidente_reuniao": ata_paa.presidente_da_reuniao.cargo if ata_paa.presidente_da_reuniao else "___",
        "secretario_reuniao": ata_paa.secretario_da_reuniao.nome if ata_paa.secretario_da_reuniao else "___",
        "cargo_secretaria_reuniao": ata_paa.secretario_da_reuniao.cargo if ata_paa.secretario_da_reuniao else "___",
        "data_reuniao_por_extenso": data_por_extenso(ata_paa.data_reuniao),
        "data_reuniao": ata_paa.data_reuniao,
        "comentarios": ata_paa.comentarios,
        "parecer_conselho": ata_paa.parecer_conselho,
        "justificativa": ata_paa.justificativa if ata_paa.justificativa else "",
        "usuario": usuario.username if usuario else "",
        "hora_reuniao": ata_paa.hora_reuniao.strftime('%H:%M') if ata_paa.hora_reuniao else "00:00",
        "hora_reuniao_formatada": formatar_hora_ata(ata_paa.hora_reuniao) if ata_paa.hora_reuniao else "00h00",
        "tipo_reuniao": ata_paa.get_tipo_reuniao_display() if ata_paa.tipo_reuniao else "___",
        "convocacao": ata_paa.get_convocacao_display() if ata_paa.convocacao else "___",
    }

    return dados_texto_da_ata


def data_por_extenso(data):
    """
    Converte data para formato por extenso
    """
    if not data:
        return 'Aos ___ dias do mês de ___ de ___'

    mes_ext = {
        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
    }

    ano, mes, dia = str(data).split("-")

    if int(dia) == 1:
        data_extenso = f'No primeiro dia do mês de {mes_ext[int(mes)]} de {real(ano)}'
    else:
        data_extenso = f'Aos {real(dia)} dias do mês de {mes_ext[int(mes)]} de {real(ano)}'

    return data_extenso


def cria_cabecalho(ata_paa: AtaPaa):
    """
    Gera o cabeçalho do documento PDF da ata PAA
    """
    paa = ata_paa.paa
    periodo_paa = paa.periodo_paa

    periodo_inicio = formata_data(periodo_paa.data_inicial) if periodo_paa.data_inicial else "___"
    periodo_fim = formata_data(periodo_paa.data_final) if periodo_paa.data_final else "___"

    cabecalho = {
        "titulo": "Ata de Apresentação do PAA",
        "subtitulo": f"Plano Anual de Atividades - {periodo_paa.referencia}",
        "periodo_referencia": periodo_paa.referencia,
        "periodo_data_inicio": periodo_inicio,
        "periodo_data_fim": periodo_fim,
    }

    return cabecalho


def formata_data(data):
    """
    Formata data para exibição
    """
    if not data:
        return "___"

    if isinstance(data, str):
        try:
            data = datetime.strptime(data, '%Y-%m-%d')
        except ValueError:
            return "___"

    return data.strftime("%d/%m/%Y")


def formatar_hora_ata(hora):
    """
    Formata hora para exibição na ata (formato: 13h00)
    """
    if not hora:
        return "00h00"

    if isinstance(hora, str):
        try:
            hora = datetime.strptime(hora, '%H:%M:%S').time()
        except ValueError:
            try:
                hora = datetime.strptime(hora, '%H:%M').time()
            except ValueError:
                return "00h00"

    return hora.strftime('%Hh%M')


def criar_identificacao_associacao_ata(paa):
    """
    Cria os dados de identificação da associação para a ata PAA
    """
    associacao = paa.associacao

    return {
        "nome_associacao": associacao.nome if associacao.nome else "___",
        "cnpj_associacao": associacao.cnpj if associacao.cnpj else "___",
        "codigo_eol": associacao.unidade.codigo_eol if associacao.unidade and associacao.unidade.codigo_eol else "___",
        "dre": associacao.unidade.formata_nome_dre() if associacao.unidade else "___",
    }

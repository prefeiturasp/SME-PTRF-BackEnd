import logging
from datetime import datetime
from typing import Any, Optional

from sme_ptrf_apps.paa.models import AtaPaa, ParticipanteAtaPaa, PeriodoPaa
from sme_ptrf_apps.paa.services.dados_documento_paa_service import (
    criar_grupos_prioridades,
    criar_atividades_estatutarias
)
from sme_ptrf_apps.utils.numero_por_extenso import real

LOGGER = logging.getLogger(__name__)

_FORMATO_DATA = "%d/%m/%Y"


def _filtrar_itens_atividades_retificadas(items: list[dict]) -> tuple[list[dict], bool]:
    """Retorna apenas os itens marcados como retificados e um flag de presença.

    Args:
        items: Lista de itens que contêm a chave ``retificado``.

    Returns:
        Tupla ``(items_retificados, tem_retificado)`` onde ``items_retificados``
        é a lista filtrada e ``tem_retificado`` indica se há ao menos um item.
    """
    items_retificados = [item for item in items if item.get('retificado')]
    return items_retificados, bool(items_retificados)


def _aplicar_filtro_retificacao_no_grupo(prioridades: list[dict], key: str) -> bool:
    """Filtra in-place os itens do grupo de prioridades identificado por ``key``,
    mantendo apenas os que foram retificados, e recalcula o total do grupo.

    Args:
        prioridades: Lista de grupos retornada por ``criar_grupos_prioridades``.
        key: Identificador estável do grupo (ex.: ``"prioridades_ptrf"``).

    Returns:
        ``True`` se o grupo possui ao menos um item retificado; ``False`` caso
        contrário ou quando o grupo não for encontrado.
    """
    grupo = next((g for g in prioridades if g.get('key') == key), None)
    if grupo is None:
        return False

    items_retificados = [item for item in grupo['items'] if item.get('retificado')]
    grupo['items'] = items_retificados
    grupo['total'] = sum(float(item.get('valor_total', 0)) for item in items_retificados)

    return bool(items_retificados)


def gerar_dados_ata_paa(ata_paa: AtaPaa, usuario=None) -> dict[str, Any]:
    """Gera os dados necessários para a geração do PDF da ata PAA.

    Para atas de retificação, obtém as alterações do ciclo corrente via
    RetificacaoPaaService e computa flags de seção para controlar quais
    blocos serão exibidos no PDF e se a etiqueta de retificação aparece.

    Args:
        ata_paa: Instância de AtaPaa (apresentação ou retificação).
        usuario: Usuário que disparou a geração; usado para auditoria.

    Returns:
        Dicionário com todos os dados necessários para renderizar o template.

    Raises:
        Exception: Qualquer erro durante a montagem dos dados é logado e
            re-lançado para ser tratado na camada de serviço.
    """
    try:
        paa = ata_paa.paa

        # Distingue ata de apresentação (False) de ata de retificação (True).
        # Esse flag controla todo o comportamento diferenciado abaixo.
        is_retificacao = ata_paa.tipo_retificacao

        alteracoes: Optional[dict] = None
        etiqueta_retificacao: Optional[str] = None
        if is_retificacao:
            # Importando aqui para evitar dependência circular entre serviços de retificação.
            from sme_ptrf_apps.paa.services.retificacao_paa_service import RetificacaoPaaService
            from sme_ptrf_apps.paa.services.ciclo_retificacao_service import CicloRetificacaoService

            # Compara o estado atual do PAA com o snapshot da réplica para descobrir
            # quais seções (prioridades, atividades, textos) foram modificadas.
            alteracoes = RetificacaoPaaService(paa=paa, usuario=usuario).identificar_alteracoes()

            # A data exibida na etiqueta é a data de criação do documento PAA retificado
            # do ciclo corrente — não a data de geração da ata. Caso o documento ainda
            # não exista (situação improvável em produção), usa a data atual como fallback.
            # Em caso de regra de negócio alterada, basta utilizar a data do bloco else
            doc_retificacao = CicloRetificacaoService(paa).documento_atual
            if doc_retificacao and doc_retificacao.criado_em:
                data_retificacao = doc_retificacao.criado_em.strftime(_FORMATO_DATA)
            else:
                data_retificacao = datetime.now().strftime(_FORMATO_DATA)
            etiqueta_retificacao = f"Retificado em: {data_retificacao}"

        cabecalho = cria_cabecalho(ata_paa)
        identificacao_associacao = criar_identificacao_associacao_ata(paa)
        presentes_na_ata = presentes_ata_paa(ata_paa)

        # Para retificação, `alteracoes` faz com que cada item carregue o flag
        # `retificado=True/False`; para apresentação, todos ficam como False.
        prioridades = criar_grupos_prioridades(paa, alteracoes=alteracoes)
        atividades_estatutarias = criar_atividades_estatutarias(paa, alteracoes=alteracoes)
        dados_texto_ata = dados_texto_ata_paa(ata_paa, usuario)

        # Flags(booleanas) indicam ao template quais seções devem ser exibidas na ata de retificação.
        # Para ata de apresentação permanecem False e são ignorados pelo template.
        retificado_prioridades_ptrf = False
        retificado_prioridades_pdde = False
        retificado_prioridades_outros = False
        retificado_atividades_estatutarias = False

        if is_retificacao:
            # Filtra cada grupo de prioridades: mantém apenas os itens
            # retificados e recalcula o total do grupo. Retorna True se restou
            # ao menos um item (sinaliza ao template que a seção deve aparecer).
            retificado_prioridades_ptrf = _aplicar_filtro_retificacao_no_grupo(
                prioridades, key='prioridades_ptrf'
            )
            retificado_prioridades_pdde = _aplicar_filtro_retificacao_no_grupo(
                prioridades, key='prioridades_pdde'
            )
            retificado_prioridades_outros = _aplicar_filtro_retificacao_no_grupo(
                prioridades, key='prioridades_outros_recursos'
            )

            # Substitui a lista completa de atividades pela lista filtrada,
            # garantindo que o template exiba somente as atividades retificadas.
            atividades_estatutarias, retificado_atividades_estatutarias = (
                _filtrar_itens_atividades_retificadas(atividades_estatutarias)
            )

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
            "is_retificacao": is_retificacao,
            "etiqueta_retificacao": etiqueta_retificacao,
            "retificado_prioridades_ptrf": retificado_prioridades_ptrf,
            "retificado_prioridades_pdde": retificado_prioridades_pdde,
            "retificado_prioridades_outros": retificado_prioridades_outros,
            "retificado_atividades_estatutarias": retificado_atividades_estatutarias,
        }
        LOGGER.info("Dados da ata PAA gerados com sucesso")
        LOGGER.info("Dados da ata PAA %s", dados_ata)
        return dados_ata
    except Exception as e:
        LOGGER.exception(f"Erro ao gerar dados da ata PAA: {str(e)}", exc_info=True)
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
        "datas_limite_periodo_por_extenso": formatar_datas_periodo(paa.periodo_paa) if paa.periodo_paa else "___",
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

    return data.strftime(_FORMATO_DATA)


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


def formatar_datas_periodo(periodo_paa: PeriodoPaa) -> str:
    """
    Dado data inicia e final de um periodo, retorna por extenso deste modo:
    1º de maio de 2026 a 30 de abril de 2027 por exemplo
    """
    meses = {
        1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
        5: "maio", 6: "junho", 7: "julho", 8: "agosto",
        9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro",
    }

    def formatar(data):
        if not data:
            return ""

        dia = "1º" if data.day == 1 else str(data.day)
        return f"{dia} de {meses[data.month]} de {data.year}"

    return f"{formatar(periodo_paa.data_inicial)} a {formatar(periodo_paa.data_final)}"


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

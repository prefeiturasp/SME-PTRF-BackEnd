import logging
from datetime import datetime
from django.db.models import Sum, Q
from sme_ptrf_apps.paa.utils import numero_decimal
from sme_ptrf_apps.paa.models.atividade_estatutaria import AtividadeEstatutaria
from sme_ptrf_apps.paa.models.prioridade_paa import PrioridadePaa
from sme_ptrf_apps.paa.models.acao_pdde import AcaoPdde
from sme_ptrf_apps.paa.querysets import queryset_prioridades_paa
from sme_ptrf_apps.paa.enums import TipoAplicacaoOpcoesEnum, RecursoOpcoesEnum
from sme_ptrf_apps.paa.choices import StatusChoices

from sme_ptrf_apps.mandatos.services import ServicoCargosDaComposicao
from sme_ptrf_apps.paa.services.outros_recursos_periodo_service import OutroRecursoPeriodoPaaListagemService
from sme_ptrf_apps.core.models import MembroAssociacao
from sme_ptrf_apps.core.models import (
    AcaoAssociacao,
)

from waffle import get_waffle_flag_model

MESES_PT = [
    "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
    "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
]

LOGGER = logging.getLogger(__name__)


def gerar_dados_documento_paa(paa, usuario, previa=False):

    cabecalho = cria_cabecalho(paa.periodo_paa)
    identificacao_associacao = criar_identificacao_associacao(paa)
    data_geracao_documento = cria_data_geracao_documento(usuario, previa)
    grupos_prioridades = criar_grupos_prioridades(paa)
    atividades_estatutarias = criar_atividades_estatutarias(paa)
    recursos_proprios = criar_recursos_proprios(paa)
    receitas_previstas = criar_receitas_previstas(paa)
    receitas_previstas_pdde = criar_receitas_previstas_pdde(paa)
    presidente_diretoria_executiva = cria_presidente_diretoria_executiva(paa.associacao)

    return {
        "cabecalho": cabecalho,
        "identificacao_associacao": identificacao_associacao,
        "data_geracao_documento": data_geracao_documento,
        "texto_introducao": paa.texto_introducao if paa.texto_introducao else "",
        "objetivos": paa.objetivos.all(),
        "grupos_prioridades": grupos_prioridades,
        "receitas_previstas": receitas_previstas,
        "receitas_previstas_pdde": receitas_previstas_pdde,
        "atividades_estatutarias": atividades_estatutarias,
        "recursos_proprios": recursos_proprios,
        "texto_conclusao": paa.texto_conclusao if paa.texto_conclusao else "",
        "presidente_diretoria_executiva": presidente_diretoria_executiva,
        "previa": previa
    }


def criar_receitas_previstas(paa):
    acoes = paa.associacao.acoes.filter(status=AcaoAssociacao.STATUS_ATIVA)

    receitas = []

    for acao_associacao in acoes:

        receita_prevista = paa.receitaprevistapaa_set.filter(acao_associacao=acao_associacao).first()
        prioridades = paa.prioridadepaa_set.filter(acao_associacao=acao_associacao)

        total_despesa_capital = prioridades.filter(
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CAPITAL.name
        ).aggregate(
            total=Sum("valor_total")
        )["total"] or 0

        total_despesa_custeio = prioridades.filter(
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name
        ).aggregate(
            total=Sum("valor_total")
        )["total"] or 0

        saldos = acao_associacao.saldo_atual()

        total_receita_custeio = (
            saldos.get("saldo_atual_custeio", 0) +
            (getattr(receita_prevista, "previsao_valor_custeio", 0) or 0)
        )

        total_receita_capital = (
            saldos.get("saldo_atual_capital", 0) +
            (getattr(receita_prevista, "previsao_valor_capital", 0) or 0)
        )

        total_receita_livre = (
            saldos.get("saldo_atual_livre", 0) +
            (getattr(receita_prevista, "previsao_valor_livre", 0) or 0)
        )

        receitas.append({
            "nome": acao_associacao.acao.nome,
            "total_receita_custeio": total_receita_custeio,
            "total_receita_capital": total_receita_capital,
            "total_receita_livre": total_receita_livre,
            "total_despesa_custeio": total_despesa_custeio,
            "total_despesa_capital": total_despesa_capital,
            "total_despesa_livre": 0,
            "saldo_custeio": total_receita_custeio - total_despesa_custeio,
            "saldo_capital": total_receita_capital - total_despesa_capital,
            "saldo_livre": total_receita_livre,
        })

    total_receitas = sum(
        item["total_receita_custeio"] +
        item["total_receita_capital"] +
        item["total_receita_livre"]
        for item in receitas
    )

    total_despesas = sum(
        item["total_despesa_custeio"] +
        item["total_despesa_capital"] +
        item["total_despesa_livre"]
        for item in receitas
    )

    total_saldo = sum(
        item["saldo_custeio"] +
        item["saldo_capital"] +
        item["saldo_livre"]
        for item in receitas
    )

    return {
        "items": receitas,
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "total_saldo": total_saldo,
    }


def criar_receitas_previstas_pdde(paa):
    acoes = AcaoPdde.objects.filter(status=AcaoAssociacao.STATUS_ATIVA)

    receitas = []

    for acao_pdde in acoes:

        receita_prevista = paa.receitaprevistapdde_set.filter(acao_pdde=acao_pdde).first()
        prioridades = paa.prioridadepaa_set.filter(acao_pdde=acao_pdde)

        total_despesa_capital = prioridades.filter(
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CAPITAL.name
        ).aggregate(
            total=Sum("valor_total")
        )["total"] or 0

        total_despesa_custeio = prioridades.filter(
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name
        ).aggregate(
            total=Sum("valor_total")
        )["total"] or 0

        total_receita_custeio = (
            (getattr(receita_prevista, "previsao_valor_custeio", 0) or 0) +
            (getattr(receita_prevista, "saldo_custeio", 0) or 0)
        )

        total_receita_capital = (
            (getattr(receita_prevista, "previsao_valor_capital", 0) or 0) +
            (getattr(receita_prevista, "saldo_capital", 0) or 0)
        )

        total_receita_livre = (
            (getattr(receita_prevista, "previsao_valor_livre", 0) or 0) +
            (getattr(receita_prevista, "saldo_livre", 0) or 0)
        )

        receitas.append({
            "nome": acao_pdde.nome,
            "total_receita_custeio": total_receita_custeio,
            "total_receita_capital": total_receita_capital,
            "total_receita_livre": total_receita_livre,
            "total_despesa_custeio": total_despesa_custeio,
            "total_despesa_capital": total_despesa_capital,
            "total_despesa_livre": 0,
            "saldo_custeio": total_receita_custeio - total_despesa_custeio,
            "saldo_capital": total_receita_capital - total_despesa_capital,
            "saldo_livre": total_receita_livre,
        })

    total_receitas = sum(
        item["total_receita_custeio"] +
        item["total_receita_capital"] +
        item["total_receita_livre"]
        for item in receitas
    )

    total_despesas = sum(
        item["total_despesa_custeio"] +
        item["total_despesa_capital"] +
        item["total_despesa_livre"]
        for item in receitas
    )

    total_saldo = sum(
        item["saldo_custeio"] +
        item["saldo_capital"] +
        item["saldo_livre"]
        for item in receitas
    )

    return {
        "items": receitas,
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "total_saldo": total_saldo,
    }


def cria_presidente_diretoria_executiva(associacao):
    flags = get_waffle_flag_model()

    LOGGER.info("Verificando se a flag <historico-de-membros> está ativa...")

    if flags.objects.filter(name='historico-de-membros', everyone=True).exists():
        LOGGER.info("A flag está ativa, as informações serão buscadas no Histórico de Membros")
        servico_cargo = ServicoCargosDaComposicao()
        presidente_diretoria_executiva = servico_cargo.get_presidente_diretoria_executiva_composicao_vigente(associacao)

    else:
        presidente_diretoria_executiva = MembroAssociacao.get_presidente_diretoria_executiva(associacao)

    return presidente_diretoria_executiva


def criar_recursos_proprios(paa):
    recursos = []

    for recurso in paa.recursopropriopaa_set.all():
        recursos.append({
            "data_prevista": recurso.data_prevista.strftime("%d/%m/%Y"),
            "fonte_recurso": recurso.fonte_recurso.nome,
            "descricao": recurso.descricao,
            "valor": recurso.valor,
        })

    outros_recursos_periodo = OutroRecursoPeriodoPaaListagemService(
        periodo_paa=paa.periodo_paa,
        unidade=paa.associacao.unidade
    ).serialized_listar_outros_recursos_periodo_receitas_previstas(paa)

    prioridades_recursos_proprios = PrioridadePaa.objects.filter(
        paa=paa, recurso=RecursoOpcoesEnum.RECURSO_PROPRIO.name)

    total_prioridades_recursos_proprios = numero_decimal(prioridades_recursos_proprios.aggregate(
        total=Sum("valor_total")
    )["total"] or 0)

    total_recursos_proprios = paa.get_total_recursos_proprios()
    saldo_recursos_proprios = numero_decimal(
        paa.get_total_recursos_proprios() - total_prioridades_recursos_proprios)

    items_outros_recursos = []

    # Outros Recursos Itens
    for orp in outros_recursos_periodo:

        outro_recurso_objeto = orp.get('outro_recurso_objeto', {})
        recurso_prioridades = PrioridadePaa.objects.filter(
            paa=paa,
            outro_recurso__uuid=outro_recurso_objeto.get('uuid'))

        total_despesa_capital = recurso_prioridades.filter(
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CAPITAL.name
        ).aggregate(
            total=Sum("valor_total")
        )["total"] or 0

        total_despesa_custeio = recurso_prioridades.filter(
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name
        ).aggregate(
            total=Sum("valor_total")
        )["total"] or 0

        total_receita_custeio = 0
        total_receita_capital = 0
        total_receita_livre = 0

        receitas_previstas = orp.get('receitas_previstas', [])

        for receita in receitas_previstas:

            total_receita_custeio += (
                numero_decimal(receita.get("previsao_valor_custeio")) +
                numero_decimal(receita.get("saldo_custeio"))
            )

            total_receita_capital += (
                numero_decimal(receita.get("previsao_valor_capital")) +
                numero_decimal(receita.get("saldo_capital"))
            )

            total_receita_livre += (
                numero_decimal(receita.get("previsao_valor_livre")) +
                numero_decimal(receita.get("saldo_livre"))
            )

        items_outros_recursos.append({
            "nome": outro_recurso_objeto.get('nome'),
            "total_receita_custeio": total_receita_custeio,
            "total_receita_capital": total_receita_capital,
            "total_receita_livre": total_receita_livre,
            "total_despesa_custeio": total_despesa_custeio,
            "total_despesa_capital": total_despesa_capital,
            "total_despesa_livre": 0,
            "saldo_custeio": total_receita_custeio - total_despesa_custeio,
            "saldo_capital": total_receita_capital - total_despesa_capital,
            "saldo_livre": total_receita_livre,
        })

    total_receitas_outros = sum(
        item["total_receita_custeio"] +
        item["total_receita_capital"] +
        item["total_receita_livre"]
        for item in items_outros_recursos
    )

    total_despesas_outros = sum(
        item["total_despesa_custeio"] +
        item["total_despesa_capital"] +
        item["total_despesa_livre"]
        for item in items_outros_recursos
    )

    total_saldo_outros = sum(
        item["saldo_custeio"] +
        item["saldo_capital"] +
        item["saldo_livre"]
        for item in items_outros_recursos
    )

    total_receitas = total_receitas_outros + total_recursos_proprios
    total_despesas = total_despesas_outros + total_prioridades_recursos_proprios
    total_saldo = total_saldo_outros + total_recursos_proprios

    return {
        "items": recursos,
        "total_recursos_proprios": total_recursos_proprios,
        "total_prioridades_recursos_proprios": total_prioridades_recursos_proprios,
        "saldo_recursos_proprios": saldo_recursos_proprios,
        "items_outros_recursos": items_outros_recursos,
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "total_saldo": total_saldo,
    }


def criar_atividades_estatutarias(paa):
    items = []

    atividades = AtividadeEstatutaria.objects.filter(Q(paa__isnull=True) | Q(paa=paa), status=StatusChoices.ATIVO)

    for atividade in atividades:
        atividade_paa = paa.atividadeestatutariapaa_set.filter(atividade_estatutaria=atividade).first()
        items.append({
            "tipo_atividade": atividade.get_tipo_display(),
            "data": atividade_paa.data.strftime("%d/%m/%Y") if atividade_paa else "",
            "atividades_previstas": atividade.nome,
            "mes_ano": (
                f"{MESES_PT[atividade_paa.data.month - 1]}/{atividade_paa.data.year}"
                if atividade_paa
                else MESES_PT[atividade.mes]
            ),
        })

    return items


def criar_grupos_prioridades(paa):

    def ordenar_recursos(prioridades):
        def chave(i):
            eh_proprio = i["recurso"] == "Recurso Próprio"
            return (not eh_proprio, i["recurso"])

        return sorted(prioridades, key=chave)

    def filtrar_prioridade(prioridades, prioridade, recurso):
        if isinstance(recurso, str):
            recurso = [recurso]

        lista_filtrada = [
            i for i in prioridades
            if i["prioridade"] == prioridade and
            i["recurso_tipo"] in recurso
        ]
        # Ordenação exceptional
        if recurso == ["RECURSO_PROPRIO", "OUTRO_RECURSO"]:
            return ordenar_recursos(lista_filtrada)

        return lista_filtrada

    def calcular_total_grupo(items):
        total = 0
        for item in items:
            try:
                total += float(item.get("valor_total", 0))
            except (TypeError, ValueError):
                pass
        return total

    prioridades = queryset_prioridades_paa(paa.prioridadepaa_set.all())

    items = []

    for prioridade in prioridades:
        if prioridade.recurso == "PTRF":
            recurso = prioridade.acao_associacao.acao.nome
        elif prioridade.recurso == "PDDE":
            recurso = prioridade.acao_pdde.nome
        elif prioridade.recurso == 'RECURSO_PROPRIO':
            recurso = "Recurso Próprio"
        elif prioridade.recurso == 'OUTRO_RECURSO':
            recurso = prioridade.outro_recurso.nome
        else:
            recurso = '--'

        items.append({
            "recurso_tipo": prioridade.recurso,
            "recurso": recurso,
            "prioridade": prioridade.prioridade,
            "tipo_aplicacao": prioridade.get_tipo_aplicacao_display(),
            "tipo_despesa_custeio": prioridade.tipo_despesa_custeio.nome if prioridade.tipo_despesa_custeio else "-",
            "especificacao_material": prioridade.especificacao_material.descricao,
            "valor_total": prioridade.valor_total
        })

    grupos = [
        {"titulo": "Prioridades PTRF", "items": filtrar_prioridade(items, True, "PTRF")},
        {"titulo": "Prioridades PDDE", "items": filtrar_prioridade(items, True, "PDDE")},
        {"titulo": "Prioridades Outros Recursos",
            "items": filtrar_prioridade(items, True, ["RECURSO_PROPRIO", "OUTRO_RECURSO"])},
        {"titulo": "Não Prioridades PTRF", "items": filtrar_prioridade(items, False, "PTRF")},
        {"titulo": "Não Prioridades PDDE", "items": filtrar_prioridade(items, False, "PDDE")},
        {"titulo": "Não Prioridades Outros Recursos",
            "items": filtrar_prioridade(items, False, ["RECURSO_PROPRIO", "OUTRO_RECURSO"])},
    ]

    for grupo in grupos:
        grupo["total"] = calcular_total_grupo(grupo["items"])

    return grupos


def criar_identificacao_associacao(paa):
    nome_associacao = paa.associacao.nome
    cnpj_associacao = paa.associacao.cnpj
    codigo_eol_associacao = paa.associacao.unidade.codigo_eol or ""
    nome_dre_associacao = paa.associacao.unidade.formata_nome_dre()

    return {
        "nome_associacao": nome_associacao,
        "cnpj_associacao": cnpj_associacao,
        "codigo_eol_associacao": codigo_eol_associacao,
        "nome_dre_associacao": nome_dre_associacao,
    }


def cria_cabecalho(periodo_paa):
    cabecalho = {
        "mes_ano_inicio": periodo_paa.data_inicial.strftime("%m/%Y"),
        "mes_ano_fim": periodo_paa.data_final.strftime("%m/%Y"),
        "ano": periodo_paa.data_final.strftime("%Y")
    }

    return cabecalho


def cria_data_geracao_documento(usuario, previa=False):
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    tipo_texto = "parcial" if previa else "final"
    quem_gerou = "" if usuario == "" else f"pelo usuário {usuario}, "
    texto = f"Documento {tipo_texto} gerado {quem_gerou}via SIG - Escola, em: {data_geracao}"

    return texto

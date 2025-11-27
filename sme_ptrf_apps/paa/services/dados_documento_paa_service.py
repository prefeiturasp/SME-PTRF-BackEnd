import logging
import locale
from datetime import datetime
from django.db.models import Sum

from sme_ptrf_apps.paa.models.acao_pdde import AcaoPdde
from sme_ptrf_apps.paa.querysets import queryset_prioridades_paa
from sme_ptrf_apps.paa.enums import TipoAplicacaoOpcoesEnum, RecursoOpcoesEnum

from sme_ptrf_apps.mandatos.services import ServicoCargosDaComposicao
from sme_ptrf_apps.core.models import MembroAssociacao
from sme_ptrf_apps.core.models import (
    AcaoAssociacao,
)

from waffle import get_waffle_flag_model

locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
LOGGER = logging.getLogger(__name__)


def gerar_dados_documento_paa(paa, usuario, previa=False):

    cabecalho = cria_cabecalho(paa.periodo_paa, previa)
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
        "texto_introducao": paa.texto_introducao,
        "objetivos": paa.objetivos.all(),
        "grupos_prioridades": grupos_prioridades,
        "receitas_previstas": receitas_previstas,
        "receitas_previstas_pdde": receitas_previstas_pdde,
        "atividades_estatutarias": atividades_estatutarias,
        "recursos_proprios": recursos_proprios,
        "texto_conclusao": paa.texto_conclusao,
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

    prioridades = paa.prioridadepaa_set.filter(recurso=RecursoOpcoesEnum.RECURSO_PROPRIO)

    total_prioridades_recursos_proprios = prioridades.aggregate(
        total=Sum("valor_total")
    )["total"] or 0

    saldo_recursos_proprios = paa.get_total_recursos_proprios() - total_prioridades_recursos_proprios

    return {
        "items": recursos,
        "total_recursos_proprios": paa.get_total_recursos_proprios(),
        "total_prioridades_recursos_proprios": total_prioridades_recursos_proprios,
        "saldo_recursos_proprios": saldo_recursos_proprios,
    }


def criar_atividades_estatutarias(paa):
    atividades = []

    for atividade in paa.atividadeestatutariapaa_set.all():
        atividades.append({
            "tipo_atividade": atividade.atividade_estatutaria.get_tipo_display(),
            "data": atividade.data.strftime("%d/%m/%Y"),
            "atividades_previstas": atividade.atividade_estatutaria.nome,
            "mes_ano": atividade.data.strftime("%B/%Y").upper(),
        })

    return atividades


def criar_grupos_prioridades(paa):
    def filtrar_prioridade(prioridades, prioridade, recurso):
        return [i for i in prioridades if i["prioridade"] == prioridade and i["recurso_tipo"] == recurso]

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
        else:
            recurso = "Recursos Próprios"

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
        {"titulo": "Prioridades Recursos próprios", "items": filtrar_prioridade(items, True, "RECURSO_PROPRIO")},
        {"titulo": "Não Prioridades PTRF", "items": filtrar_prioridade(items, False, "PTRF")},
        {"titulo": "Não Prioridades PDDE", "items": filtrar_prioridade(items, False, "PDDE")},
        {"titulo": "Não Prioridades Recursos próprios",
            "items": filtrar_prioridade(items, False, "RECURSO_PROPRIO")},
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


def cria_cabecalho(periodo_paa, previa):
    cabecalho = {
        "titulo": "Plano Anual de Atividades - PRÉVIA" if previa else "Plano Anual de Atividades - FINAL",
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

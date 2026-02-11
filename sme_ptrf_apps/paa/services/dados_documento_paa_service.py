import logging
from datetime import datetime
from django.db.models import Sum
from sme_ptrf_apps.paa.utils import numero_decimal
from sme_ptrf_apps.paa.models.atividade_estatutaria import AtividadeEstatutaria
from sme_ptrf_apps.paa.models.prioridade_paa import PrioridadePaa
from sme_ptrf_apps.paa.querysets import queryset_prioridades_paa
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum
from sme_ptrf_apps.paa.services.plano_orcamentario_service import PlanoOrcamentarioService

from sme_ptrf_apps.mandatos.services import ServicoCargosDaComposicao
from sme_ptrf_apps.core.models import MembroAssociacao

from waffle import get_waffle_flag_model

MESES_PT = [
    "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
    "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
]

LOGGER = logging.getLogger(__name__)


def _secao_plano_para_documento_receitas(secao):
    """
    Converte uma seção do plano orçamentário (PTRF ou PDDE) para o formato
    esperado pelo documento PAA: items + total_receitas, total_despesas, total_saldo.
    Usa as mesmas regras do PlanoOrcamentarioService (saldo congelado, déficit em livre, etc.).
    """
    if not secao or not secao.get("linhas"):
        return {"items": [], "total_receitas": 0, "total_despesas": 0, "total_saldo": 0}

    linhas = secao["linhas"]
    items = []
    total_receitas = 0
    total_despesas = 0
    total_saldo = 0

    for linha in linhas:
        if linha.get("isTotal"):
            total_receitas = linha["receitas"].get("total", 0)
            total_despesas = linha["despesas"].get("total", 0)
            total_saldo = linha["saldos"].get("total", 0)
            continue
        exibir_custeio = linha.get("exibirCusteio", True)
        exibir_capital = linha.get("exibirCapital", True)
        exibir_livre = linha.get("exibirLivre", True)
        if not (exibir_custeio or exibir_capital or exibir_livre):
            continue
        r = linha["receitas"]
        d = linha["despesas"]
        s = linha["saldos"]
        linhas_visiveis = []
        if exibir_custeio:
            linhas_visiveis.append({
                "label": "Custeio (R$)",
                "receita": r.get("custeio", 0),
                "despesa": d.get("custeio", 0),
                "saldo": s.get("custeio", 0),
            })
        if exibir_capital:
            linhas_visiveis.append({
                "label": "Capital (R$)",
                "receita": r.get("capital", 0),
                "despesa": d.get("capital", 0),
                "saldo": s.get("capital", 0),
            })
        if exibir_livre:
            linhas_visiveis.append({
                "label": "Livre Aplicação (R$)",
                "receita": r.get("livre", 0),
                "despesa": d.get("livre", 0),
                "saldo": s.get("livre", 0),
            })
        zebra_classe = "even" if (len(items) % 2 == 0) else "odd"
        items.append({
            "nome": linha.get("nome", "-"),
            "zebra_classe": zebra_classe,
            "exibirCusteio": exibir_custeio,
            "exibirCapital": exibir_capital,
            "exibirLivre": exibir_livre,
            "linhas": linhas_visiveis,
            "total_receita_custeio": r.get("custeio", 0),
            "total_receita_capital": r.get("capital", 0),
            "total_receita_livre": r.get("livre", 0),
            "total_despesa_custeio": d.get("custeio", 0),
            "total_despesa_capital": d.get("capital", 0),
            "total_despesa_livre": d.get("livre", 0),
            "saldo_custeio": s.get("custeio", 0),
            "saldo_capital": s.get("capital", 0),
            "saldo_livre": s.get("livre", 0),
        })

    return {
        "items": items,
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "total_saldo": total_saldo,
    }


def gerar_dados_documento_paa(paa, usuario, previa=False):
    plano = PlanoOrcamentarioService(paa).construir_plano_orcamentario()
    secoes_por_key = {s["key"]: s for s in plano["secoes"]}

    cabecalho = cria_cabecalho(paa.periodo_paa)
    identificacao_associacao = criar_identificacao_associacao(paa)
    data_geracao_documento = cria_data_geracao_documento(usuario, previa)
    grupos_prioridades = criar_grupos_prioridades(paa)
    atividades_estatutarias = criar_atividades_estatutarias(paa)
    recursos_proprios = criar_recursos_proprios(paa, secoes_por_key.get("outros_recursos"))
    receitas_previstas = _secao_plano_para_documento_receitas(secoes_por_key.get("ptrf"))
    receitas_previstas_pdde = _secao_plano_para_documento_receitas(secoes_por_key.get("pdde"))
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


def criar_recursos_proprios(paa, secao_outros_recursos=None):
    """
    Monta dados de recursos próprios e outros recursos para o documento PAA.
    Quando secao_outros_recursos é informada (vinda do PlanoOrcamentarioService),
    usa as mesmas regras do plano (saldo, déficit em livre, filtros, etc.).
    """
    recursos = []
    for recurso in paa.recursopropriopaa_set.all():
        recursos.append({
            "data_prevista": recurso.data_prevista.strftime("%d/%m/%Y"),
            "fonte_recurso": recurso.fonte_recurso.nome,
            "descricao": recurso.descricao,
            "valor": recurso.valor,
        })

    if secao_outros_recursos and secao_outros_recursos.get("linhas"):
        linhas = secao_outros_recursos["linhas"]
        key_recursos_proprios = RecursoOpcoesEnum.RECURSO_PROPRIO.name
        key_total = "outros-recursos-total"

        total_recursos_proprios = 0
        total_prioridades_recursos_proprios = 0
        saldo_recursos_proprios = 0
        items_outros_recursos = []
        total_receitas = 0
        total_despesas = 0
        total_saldo = 0

        for linha in linhas:
            key_linha = linha.get("key")
            if key_linha == key_recursos_proprios:
                total_recursos_proprios = numero_decimal(linha["receitas"].get("total", 0))
                total_prioridades_recursos_proprios = numero_decimal(linha["despesas"].get("total", 0))
                saldo_recursos_proprios = numero_decimal(linha["saldos"].get("total", 0))
            elif key_linha == key_total:
                total_receitas = numero_decimal(linha["receitas"].get("total", 0))
                total_despesas = numero_decimal(linha["despesas"].get("total", 0))
                total_saldo = numero_decimal(linha["saldos"].get("total", 0))
            else:
                exibir_custeio = linha.get("exibirCusteio", True)
                exibir_capital = linha.get("exibirCapital", True)
                exibir_livre = linha.get("exibirLivre", True)
                if not (exibir_custeio or exibir_capital or exibir_livre):
                    continue
                r, d, s = linha["receitas"], linha["despesas"], linha["saldos"]
                linhas_visiveis = []
                if exibir_custeio:
                    linhas_visiveis.append({
                        "label": "Custeio (R$)",
                        "receita": r.get("custeio", 0),
                        "despesa": d.get("custeio", 0),
                        "saldo": s.get("custeio", 0),
                    })
                if exibir_capital:
                    linhas_visiveis.append({
                        "label": "Capital (R$)",
                        "receita": r.get("capital", 0),
                        "despesa": d.get("capital", 0),
                        "saldo": s.get("capital", 0),
                    })
                if exibir_livre:
                    linhas_visiveis.append({
                        "label": "Livre Aplicação (R$)",
                        "receita": r.get("livre", 0),
                        "despesa": d.get("livre", 0),
                        "saldo": s.get("livre", 0),
                    })
                zebra_classe = "odd" if (len(items_outros_recursos) % 2 == 0) else "even"
                items_outros_recursos.append({
                    "nome": linha.get("nome", "-"),
                    "zebra_classe": zebra_classe,
                    "exibirCusteio": exibir_custeio,
                    "exibirCapital": exibir_capital,
                    "exibirLivre": exibir_livre,
                    "linhas": linhas_visiveis,
                    "total_receita_custeio": r.get("custeio", 0),
                    "total_receita_capital": r.get("capital", 0),
                    "total_receita_livre": r.get("livre", 0),
                    "total_despesa_custeio": d.get("custeio", 0),
                    "total_despesa_capital": d.get("capital", 0),
                    "total_despesa_livre": d.get("livre", 0),
                    "saldo_custeio": s.get("custeio", 0),
                    "saldo_capital": s.get("capital", 0),
                    "saldo_livre": s.get("livre", 0),
                })

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

    # Quando não possuir nenhum outro recurso, monta a seção de recursos próprios
    prioridades_recursos_proprios = PrioridadePaa.objects.filter(
        paa=paa, recurso=RecursoOpcoesEnum.RECURSO_PROPRIO.name
    )
    total_prioridades_recursos_proprios = numero_decimal(
        prioridades_recursos_proprios.aggregate(total=Sum("valor_total"))["total"] or 0
    )
    total_recursos_proprios = numero_decimal(paa.get_total_recursos_proprios())
    saldo_recursos_proprios = total_recursos_proprios - total_prioridades_recursos_proprios

    return {
        "items": recursos,
        "total_recursos_proprios": total_recursos_proprios,
        "total_prioridades_recursos_proprios": total_prioridades_recursos_proprios,
        "saldo_recursos_proprios": saldo_recursos_proprios,
        "items_outros_recursos": [],
        "total_receitas": total_recursos_proprios,
        "total_despesas": total_prioridades_recursos_proprios,
        "total_saldo": saldo_recursos_proprios,
    }


def criar_atividades_estatutarias(paa):
    items = []

    atividades = AtividadeEstatutaria.disponiveis_ordenadas(paa)

    for atividade in atividades:
        atividade_paa = paa.atividadeestatutariapaa_set.filter(atividade_estatutaria=atividade).first()
        items.append({
            "tipo_atividade": atividade.get_tipo_display(),
            "data": atividade_paa.data.strftime("%d/%m/%Y") if atividade_paa else "",
            "atividades_previstas": atividade.nome,
            "mes_ano": (
                f"{MESES_PT[atividade_paa.data.month - 1]}/{atividade_paa.data.year}"
                if atividade_paa
                else MESES_PT[atividade.mes - 1]
            ),
        })

    return items


def criar_grupos_prioridades(paa):

    def ordenar_recursos(prioridades):
        def chave(i):
            eh_proprio = i["recurso"] == "Recursos Próprios"
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

        items.append({
            "recurso_tipo": prioridade.recurso,
            "recurso": prioridade.nome(),
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

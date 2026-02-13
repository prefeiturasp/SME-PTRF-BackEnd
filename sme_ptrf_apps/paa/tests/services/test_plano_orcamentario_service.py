import pytest
from decimal import Decimal

from sme_ptrf_apps.paa.services.plano_orcamentario_service import (
    PlanoOrcamentarioService,
)


def _make_service():
    return PlanoOrcamentarioService(paa=None)


def test_calcular_secao_ptrf_exclui_acoes_com_receita_zerada():
    """
    Garante que _calcular_secao_ptrf:
    - não exibe linha da ação quando capital, custeio e livre aplicação estão zerados;
    - adiciona linha de TOTAL somando apenas as ações com receita.
    """
    service = _make_service()

    uuid1 = "acao-1"
    uuid2 = "acao-2"

    # Ação 1 com valores em custeio e capital
    receitas_ptrf = [
        {
            "uuid": uuid1,
            "acao": {"nome": "Ação 1"},
            "receitas_previstas_paa": [
                {
                    "previsao_valor_custeio": 100,
                    "previsao_valor_capital": 50,
                    "previsao_valor_livre": 0,
                }
            ],
            "saldos": {
                "saldo_atual_custeio": 0,
                "saldo_atual_capital": 0,
                "saldo_atual_livre": 0,
            },
        },
        # Ação 2 totalmente zerada não deve aparecer
        {
            "uuid": uuid2,
            "acao": {"nome": "Ação 2"},
            "receitas_previstas_paa": [
                {
                    "previsao_valor_custeio": 0,
                    "previsao_valor_capital": 0,
                    "previsao_valor_livre": 0,
                }
            ],
            "saldos": {
                "saldo_atual_custeio": 0,
                "saldo_atual_capital": 0,
                "saldo_atual_livre": 0,
            },
        },
    ]

    prioridades_ptrf = {
        uuid1: {
            "custeio": Decimal("10"),
            "capital": Decimal("0"),
            "livre": Decimal("0"),
        },
        # uuid2 sem prioridades
    }

    secao = service._calcular_secao_ptrf(receitas_ptrf, prioridades_ptrf)

    assert secao["key"] == "ptrf"
    # 1 linha de ação (apenas Ação 1) + 1 linha TOTAL
    assert len(secao["linhas"]) == 2

    linha_acao1 = next(linha for linha in secao["linhas"] if linha["key"] == uuid1)
    linha_total = next(linha for linha in secao["linhas"] if linha.get("isTotal"))

    assert linha_acao1["nome"] == "Ação 1"
    # Receita total da ação 1 = 100 (custeio) + 50 (capital)
    assert linha_acao1["receitas"]["total"] == pytest.approx(150.0)

    # Ação 2 não deve aparecer (receita zerada)
    assert not any(linha["key"] == uuid2 for linha in secao["linhas"])

    assert linha_total["isTotal"] is True
    # Total da seção deve ser apenas da ação 1 (150)
    assert linha_total["receitas"]["total"] == pytest.approx(150.0)


def test_calcular_secao_ptrf_retorna_none_quando_todas_acoes_sem_receita():
    """
    Quando todas as ações PTRF têm receita zerada (capital, custeio e livre),
    a seção PTRF não deve ser criada (retorna None).
    """
    service = _make_service()

    receitas_ptrf = [
        {
            "uuid": "acao-1",
            "acao": {"nome": "Ação 1"},
            "receitas_previstas_paa": [
                {
                    "previsao_valor_custeio": 0,
                    "previsao_valor_capital": 0,
                    "previsao_valor_livre": 0,
                }
            ],
            "saldos": {
                "saldo_atual_custeio": 0,
                "saldo_atual_capital": 0,
                "saldo_atual_livre": 0,
            },
        },
    ]

    secao = service._calcular_secao_ptrf(receitas_ptrf, {})

    assert secao is None


def test_calcular_secao_pdde_respeita_flags_aceita():
    """
    Garante que _calcular_secao_pdde:
    - zera e ignora categorias que a ação PDDE não aceita;
    - não inclui ações que só têm valores em categorias não aceitas.
    """
    service = _make_service()

    uuid1 = "acao-pdde-1"
    uuid2 = "acao-pdde-2"

    acoes_pdde = [
        {
            "uuid": uuid1,
            "nome": "PDDE Aceita Capital",
            "aceita_custeio": False,
            "aceita_capital": True,
            "aceita_livre_aplicacao": False,
            "total_valor_custeio": 200,
            "total_valor_capital": 300,
            "total_valor_livre_aplicacao": 400,
        },
        # Ação 2 só tem valor em custeio, mas não aceita custeio -> deve ser ignorada
        {
            "uuid": uuid2,
            "nome": "PDDE Não Aceita Custeio",
            "aceita_custeio": False,
            "aceita_capital": False,
            "aceita_livre_aplicacao": False,
            "total_valor_custeio": 500,
            "total_valor_capital": 0,
            "total_valor_livre_aplicacao": 0,
        },
    ]

    prioridades_pdde = {
        uuid1: {
            "custeio": Decimal("50"),
            "capital": Decimal("0"),
            "livre": Decimal("0"),
        },
        uuid2: {
            "custeio": Decimal("10"),
            "capital": Decimal("0"),
            "livre": Decimal("0"),
        },
    }

    secao = service._calcular_secao_pdde(acoes_pdde, prioridades_pdde)

    assert secao["key"] == "pdde"
    # 1 linha de ação (uuid1) + 1 linha TOTAL
    assert len(secao["linhas"]) == 2

    linha_acao = secao["linhas"][0]
    linha_total = secao["linhas"][1]

    assert linha_acao["key"] == uuid1
    assert linha_acao["nome"] == "PDDE Aceita Capital"

    # Custeio deve ser totalmente ignorado (não aceita_custeio)
    assert linha_acao["exibirCusteio"] is False
    assert linha_acao["receitas"]["custeio"] == 0.0
    assert linha_acao["despesas"]["custeio"] == 0.0

    # Capital deve ser considerado
    assert linha_acao["exibirCapital"] is True
    assert linha_acao["receitas"]["capital"] == pytest.approx(300.0)

    # Livre aplicação não é aceito -> deve ser ignorado
    assert linha_acao["exibirLivre"] is False
    assert linha_acao["receitas"]["livre"] == 0.0

    # Total da seção deve ser igual ao total da única ação considerada
    assert linha_total["isTotal"] is True
    assert linha_total["receitas"]["total"] == pytest.approx(
        linha_acao["receitas"]["total"]
    )


def test_calcular_secao_outros_recursos_recurso_proprio_oculta_custeio_capital():
    """
    Garante que _calcular_secao_outros_recursos:
    - marca recurso próprio para ocultar custeio/capital;
    - calcula linha TOTAL somando os recursos considerados.
    """
    service = _make_service()

    recurso_proprio_key = "RECURSO_PROPRIO"
    outro_recurso_key = "outro-1"

    receitas_outros = [
        {
            "uuid": recurso_proprio_key,
            "nome": "Recursos Próprios",
            "tipo": "RECURSO_PROPRIO",
            "aceita_custeio": False,
            "aceita_capital": False,
            "aceita_livre": True,
            "receitas": {
                "custeio": Decimal("0"),
                "capital": Decimal("0"),
                "livre": Decimal("500"),
                "total": Decimal("500"),
            },
        },
        {
            "uuid": outro_recurso_key,
            "nome": "Outro Recurso",
            "tipo": "OUTRO_RECURSO",
            "aceita_custeio": True,
            "aceita_capital": False,
            "aceita_livre": False,
            "receitas": {
                "custeio": Decimal("100"),
                "capital": Decimal("0"),
                "livre": Decimal("0"),
                "total": Decimal("100"),
            },
        },
    ]

    prioridades = {
        recurso_proprio_key: {
            "custeio": Decimal("0"),
            "capital": Decimal("0"),
            "livre": Decimal("0"),
        },
        outro_recurso_key: {
            "custeio": Decimal("20"),
            "capital": Decimal("0"),
            "livre": Decimal("0"),
        },
    }

    secao = service._calcular_secao_outros_recursos(receitas_outros, prioridades)

    assert secao["key"] == "outros_recursos"
    # 2 linhas de recurso + 1 linha TOTAL
    assert len(secao["linhas"]) == 3

    linha_rp = next(linha for linha in secao["linhas"] if linha["key"] == recurso_proprio_key)
    linha_outro = next(linha for linha in secao["linhas"] if linha["key"] == outro_recurso_key)
    linha_total = next(linha for linha in secao["linhas"] if linha.get("isTotal"))

    # Recurso próprio deve ocultar custeio/capital e exibir apenas livre
    assert linha_rp["ocultarCusteioCapital"] is True
    assert linha_rp["exibirCusteio"] is False
    assert linha_rp["exibirCapital"] is False
    assert linha_rp["exibirLivre"] is True
    assert linha_rp["receitas"]["custeio"] == 0.0
    assert linha_rp["receitas"]["capital"] == 0.0
    assert linha_rp["receitas"]["livre"] == pytest.approx(500.0)

    # Outro recurso não deve ocultar custeio/capital
    assert linha_outro["ocultarCusteioCapital"] is False
    assert linha_outro["exibirCusteio"] is True
    assert linha_outro["receitas"]["custeio"] == pytest.approx(100.0)

    # TOTAL deve somar os valores das linhas
    soma_totais = linha_rp["receitas"]["total"] + linha_outro["receitas"]["total"]
    assert linha_total["isTotal"] is True
    assert linha_total["receitas"]["total"] == pytest.approx(soma_totais)


def test_calcular_secao_outros_recursos_sem_receitas_retorna_none():
    """
    Quando não há receitas de outros recursos, a seção deve ser None.
    """
    service = _make_service()

    secao = service._calcular_secao_outros_recursos([], {})

    assert secao is None


def test_calcular_secao_pdde_sem_acoes_retorna_none():
    """
    Quando não há ações PDDE, a seção PDDE deve ser None.
    """
    service = _make_service()

    secao = service._calcular_secao_pdde([], {})

    assert secao is None


def test_calcular_saldo_debita_negativos_de_livre_aplicacao():
    """
    _calcular_saldo deve:
    - zerar custeio/capital quando ficarem negativos;
    - debitar o déficit do saldo de livre aplicação;
    - manter o total consistente.
    """
    service = _make_service()

    receitas = {
        "custeio": Decimal("100"),
        "capital": Decimal("50"),
        "livre": Decimal("200"),
    }
    despesas = {
        "custeio": Decimal("150"),  # -50 em custeio
        "capital": Decimal("80"),   # -30 em capital
        "livre": Decimal("0"),
    }

    saldo = service._calcular_saldo(receitas, despesas)

    # Custeio e capital não podem ficar negativos
    assert saldo["custeio"] == Decimal("0")
    assert saldo["capital"] == Decimal("0")

    # Livre aplicação deve ser reduzido pelos déficits de custeio (-50) e capital (-30)
    # livre_bruto = 200 - 0 = 200
    # livre_final = 200 - 50 - 30 = 120
    assert saldo["livre"] == Decimal("120")
    assert saldo["total"] == saldo["livre"]


def test_construir_plano_orcamentario_monta_secoes_quando_calculos_retornam_dados():
    """
    Garante que construir_plano_orcamentario:
    - inclui apenas as seções cujo cálculo não retorna None;
    - mantém a ordem PTRF, PDDE, Outros Recursos.
    """
    service = _make_service()

    service._obter_prioridades_agrupadas = lambda: {"PTRF": {}, "PDDE": {}}
    service._obter_prioridades_outros_recursos = lambda: {}
    service._obter_receitas_ptrf = lambda: []
    service._obter_acoes_pdde_totais = lambda: []
    service._obter_receitas_outros_recursos = lambda: []

    service._calcular_secao_ptrf = lambda receitas, prioridades: {
        "key": "ptrf",
        "titulo": "PTRF",
        "linhas": [],
    }
    service._calcular_secao_pdde = lambda acoes, prioridades: {
        "key": "pdde",
        "titulo": "PDDE",
        "linhas": [],
    }
    # Outros recursos não será incluído
    service._calcular_secao_outros_recursos = (
        lambda receitas, prioridades: None
    )

    resultado = service.construir_plano_orcamentario()

    secoes = resultado["secoes"]
    assert [s["key"] for s in secoes] == ["ptrf", "pdde"]


def test_calcular_secao_ptrf_sem_receitas_previstas_nao_estoura_erro():
    """
    Quando a ação PTRF não possui receitas_previstas_paa (lista vazia),
    a seção PTRF deve ser calculada normalmente usando apenas os saldos,
    sem lançar IndexError.
    """
    service = _make_service()

    uuid1 = "acao-sem-receita-prevista"
    receitas_ptrf = [
        {
            "uuid": uuid1,
            "acao": {"nome": "Ação sem receita prevista"},
            "receitas_previstas_paa": [],
            "saldos": {
                "saldo_atual_custeio": 10,
                "saldo_atual_capital": 20,
                "saldo_atual_livre": 30,
            },
        }
    ]

    prioridades_ptrf = {}

    secao = service._calcular_secao_ptrf(receitas_ptrf, prioridades_ptrf)

    assert secao["key"] == "ptrf"
    # 1 linha de ação + 1 linha TOTAL
    assert len(secao["linhas"]) == 2

    linha_acao = next(linha for linha in secao["linhas"] if linha["key"] == uuid1)
    # Como não há previsão, a receita deve ser exatamente a soma dos saldos
    assert linha_acao["receitas"]["total"] == pytest.approx(10 + 20 + 30)

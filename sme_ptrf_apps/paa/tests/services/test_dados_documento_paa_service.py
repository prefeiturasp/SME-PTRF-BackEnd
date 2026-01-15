import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock

from sme_ptrf_apps.paa.services.dados_documento_paa_service import (gerar_dados_documento_paa,
                                                                    criar_grupos_prioridades, criar_recursos_proprios)


@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.cria_presidente_diretoria_executiva", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.criar_receitas_previstas_pdde", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.criar_receitas_previstas", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.criar_recursos_proprios", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.criar_atividades_estatutarias", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.criar_grupos_prioridades", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.cria_data_geracao_documento", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.criar_identificacao_associacao", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.cria_cabecalho", autospec=True)
def test_gerar_dados_documento_paa(
    mock_cabecalho,
    mock_identificacao,
    mock_data,
    mock_grupos,
    mock_atividades,
    mock_recursos,
    mock_receitas,
    mock_receitas_pdde,
    mock_presidente
):
    paa = MagicMock()
    usuario = MagicMock()

    mock_cabecalho.return_value = "CAB"
    mock_identificacao.return_value = "ASSOC"
    mock_data.return_value = "DATA"
    mock_grupos.return_value = "GRUPOS"
    mock_atividades.return_value = "ATIV"
    mock_recursos.return_value = "REC"
    mock_receitas.return_value = "REC_PREV"
    mock_receitas_pdde.return_value = "REC_PDDE"
    mock_presidente.return_value = "PRES"

    paa.objetivos.all.return_value = ["OBJ1", "OBJ2"]
    paa.texto_introducao = "INTRO"
    paa.texto_conclusao = "CONC"

    result = gerar_dados_documento_paa(paa, usuario, previa=True)

    mock_cabecalho.assert_called_once_with(paa.periodo_paa)
    mock_identificacao.assert_called_once_with(paa)
    mock_data.assert_called_once_with(usuario, True)
    mock_grupos.assert_called_once_with(paa)
    mock_atividades.assert_called_once_with(paa)
    mock_recursos.assert_called_once_with(paa)
    mock_receitas.assert_called_once_with(paa)
    mock_receitas_pdde.assert_called_once_with(paa)
    mock_presidente.assert_called_once_with(paa.associacao)

    assert result == {
        "cabecalho": "CAB",
        "identificacao_associacao": "ASSOC",
        "data_geracao_documento": "DATA",
        "texto_introducao": "INTRO",
        "objetivos": ["OBJ1", "OBJ2"],
        "grupos_prioridades": "GRUPOS",
        "receitas_previstas": "REC_PREV",
        "receitas_previstas_pdde": "REC_PDDE",
        "atividades_estatutarias": "ATIV",
        "recursos_proprios": "REC",
        "texto_conclusao": "CONC",
        "presidente_diretoria_executiva": "PRES",
        "previa": True,
    }


@pytest.mark.django_db
def test_criar_grupos_prioridades_junta_recurso_proprio_e_outro(
    paa,
    prioridade_paa_factory,
    outro_recurso_factory
):

    outro_recurso1 = outro_recurso_factory(nome="Alimentação")
    outro_recurso2 = outro_recurso_factory(nome="Transporte")

    prioridade_paa_factory(
        paa=paa,
        prioridade=True,
        recurso="RECURSO_PROPRIO",
        valor_total=100
    )

    prioridade_paa_factory(
        paa=paa,
        prioridade=True,
        recurso="OUTRO_RECURSO",
        outro_recurso=outro_recurso1,
        valor_total=50
    )

    prioridade_paa_factory(
        paa=paa,
        prioridade=True,
        recurso="OUTRO_RECURSO",
        outro_recurso=outro_recurso2,
        valor_total=30
    )

    grupos = criar_grupos_prioridades(paa)

    grupo_outros = next(
        g for g in grupos
        if g["titulo"] == "Prioridades Outros Recursos"
    )

    items = grupo_outros["items"]

    # estão juntos
    assert len(items) == 3

    # recurso próprio primeiro
    assert items[0]["recurso"] == "Recurso Próprio"

    # ordem alfabética dos outros
    assert [i["recurso"] for i in items[1:]] == [
        "Alimentação",
        "Transporte",
    ]

    # total correto
    assert grupo_outros["total"] == 180


@pytest.mark.django_db
@patch(
    "sme_ptrf_apps.paa.services.dados_documento_paa_service.OutroRecursoPeriodoPaaListagemService"
)
def test_criar_recursos_proprios_calcula_totais_corretamente(
    mock_service,
    paa,
    prioridade_paa_factory,
    recurso_proprio_paa_factory,
    outro_recurso_factory,
):
    recurso_proprio_paa_factory(
        paa=paa,
        valor=Decimal("200"),
        descricao="Recurso 1"
    )

    recurso_proprio_paa_factory(
        paa=paa,
        valor=Decimal("300"),
        descricao="Recurso 2"
    )

    prioridade_paa_factory(
        paa=paa,
        recurso="RECURSO_PROPRIO",
        valor_total=Decimal("150"),
        prioridade=True
    )

    prioridade_paa_factory(
        paa=paa,
        recurso="RECURSO_PROPRIO",
        valor_total=Decimal("50"),
        prioridade=True
    )

    # Outro recurso
    outro_recurso = outro_recurso_factory(nome="Prêmio Qualidade")

    prioridade_paa_factory(
        paa=paa,
        recurso="OUTRO_RECURSO",
        outro_recurso=outro_recurso,
        tipo_aplicacao="CUSTEIO",
        valor_total=Decimal("80"),
        prioridade=True
    )

    prioridade_paa_factory(
        paa=paa,
        recurso="OUTRO_RECURSO",
        outro_recurso=outro_recurso,
        tipo_aplicacao="CAPITAL",
        valor_total=Decimal("20"),
        prioridade=True
    )

    mock_service.return_value.serialized_listar_outros_recursos_periodo_receitas_previstas.return_value = [
        {
            "outro_recurso_objeto": {
                "uuid": outro_recurso.uuid,
                "nome": outro_recurso.nome,
            },
            "receitas_previstas": [
                {
                    "previsao_valor_custeio": Decimal("100"),
                    "saldo_custeio": Decimal("10"),
                    "previsao_valor_capital": Decimal("50"),
                    "saldo_capital": Decimal("5"),
                    "previsao_valor_livre": Decimal("0"),
                    "saldo_livre": Decimal("0"),
                }
            ]
        }
    ]

    # Mock do método do PAA
    paa.get_total_recursos_proprios = lambda: Decimal("500")

    resultado = criar_recursos_proprios(paa)

    # Itens de recurso próprio
    assert len(resultado["items"]) == 2

    # Totais de recurso próprio
    assert resultado["total_recursos_proprios"] == Decimal("500")
    assert resultado["total_prioridades_recursos_proprios"] == Decimal("200")
    assert resultado["saldo_recursos_proprios"] == Decimal("300")

    # Outros recursos
    assert len(resultado["items_outros_recursos"]) == 1
    item_outro = resultado["items_outros_recursos"][0]

    assert item_outro["total_despesa_custeio"] == Decimal("80")
    assert item_outro["total_despesa_capital"] == Decimal("20")

    assert item_outro["total_receita_custeio"] == Decimal("110")
    assert item_outro["total_receita_capital"] == Decimal("55")

    # Totais finais
    assert resultado["total_receitas"] == Decimal("665")
    assert resultado["total_despesas"] == Decimal("300")

    assert resultado["total_saldo"] == (
        resultado["total_recursos_proprios"] +
        sum(
            item["saldo_custeio"] +
            item["saldo_capital"] +
            item["saldo_livre"]
            for item in resultado["items_outros_recursos"]
        )
    )

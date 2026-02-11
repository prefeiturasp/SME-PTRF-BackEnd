import pytest
from datetime import date
from model_bakery import baker
from decimal import Decimal
from unittest.mock import patch, MagicMock, Mock

from sme_ptrf_apps.paa.services.dados_documento_paa_service import (
    gerar_dados_documento_paa,
    criar_grupos_prioridades,
    criar_recursos_proprios,
    criar_atividades_estatutarias,
    cria_presidente_diretoria_executiva,
    _secao_plano_para_documento_receitas,
)


@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.cria_presidente_diretoria_executiva", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.criar_recursos_proprios", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.criar_atividades_estatutarias", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.criar_grupos_prioridades", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.cria_data_geracao_documento", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.criar_identificacao_associacao", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.cria_cabecalho", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.PlanoOrcamentarioService", autospec=True)
def test_gerar_dados_documento_paa(
    mock_plano_service,
    mock_cabecalho,
    mock_identificacao,
    mock_data,
    mock_grupos,
    mock_atividades,
    mock_recursos,
    mock_presidente
):
    paa = MagicMock()
    usuario = MagicMock()

    mock_plano_service.return_value.construir_plano_orcamentario.return_value = {"secoes": []}
    mock_cabecalho.return_value = "CAB"
    mock_identificacao.return_value = "ASSOC"
    mock_data.return_value = "DATA"
    mock_grupos.return_value = "GRUPOS"
    mock_atividades.return_value = "ATIV"
    mock_recursos.return_value = "REC"
    mock_presidente.return_value = "PRES"

    paa.objetivos.all.return_value = ["OBJ1", "OBJ2"]
    paa.texto_introducao = "INTRO"
    paa.texto_conclusao = "CONC"

    result = gerar_dados_documento_paa(paa, usuario, previa=True)

    mock_plano_service.return_value.construir_plano_orcamentario.assert_called_once()
    mock_cabecalho.assert_called_once_with(paa.periodo_paa)
    mock_identificacao.assert_called_once_with(paa)
    mock_data.assert_called_once_with(usuario, True)
    mock_grupos.assert_called_once_with(paa)
    mock_atividades.assert_called_once_with(paa)
    mock_recursos.assert_called_once_with(paa, None)
    mock_presidente.assert_called_once_with(paa.associacao)

    assert result["cabecalho"] == "CAB"
    assert result["identificacao_associacao"] == "ASSOC"
    assert result["data_geracao_documento"] == "DATA"
    assert result["texto_introducao"] == "INTRO"
    assert list(result["objetivos"]) == ["OBJ1", "OBJ2"]
    assert result["grupos_prioridades"] == "GRUPOS"
    assert result["receitas_previstas"] == {
        "items": [],
        "total_receitas": 0,
        "total_despesas": 0,
        "total_saldo": 0,
    }
    assert result["receitas_previstas_pdde"] == {
        "items": [],
        "total_receitas": 0,
        "total_despesas": 0,
        "total_saldo": 0,
    }
    assert result["atividades_estatutarias"] == "ATIV"
    assert result["recursos_proprios"] == "REC"
    assert result["texto_conclusao"] == "CONC"
    assert result["presidente_diretoria_executiva"] == "PRES"
    assert result["previa"] is True


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
    assert items[0]["recurso"] == "Recursos Próprios"

    # ordem alfabética dos outros
    assert [i["recurso"] for i in items[1:]] == [
        "Alimentação",
        "Transporte",
    ]

    # total correto
    assert grupo_outros["total"] == 180


@pytest.mark.django_db
def test_criar_recursos_proprios_calcula_totais_corretamente(
    paa,
    prioridade_paa_factory,
    recurso_proprio_paa_factory,
    outro_recurso_factory,
    outro_recurso_periodo_factory,
    receita_prevista_outro_recurso_periodo_factory
):
    recurso_proprio_paa_factory(
        paa=paa,
        associacao=paa.associacao,
        valor=Decimal("200"),
        descricao="Recurso 1"
    )

    recurso_proprio_paa_factory(
        paa=paa,
        associacao=paa.associacao,
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

    outro_recurso_periodo = outro_recurso_periodo_factory(outro_recurso=outro_recurso, periodo_paa=paa.periodo_paa)

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

    receita_prevista_outro_recurso_periodo_factory(
        paa=paa,
        outro_recurso_periodo=outro_recurso_periodo,
        previsao_valor_custeio=110,
        saldo_custeio=50,
        previsao_valor_capital=55,
        saldo_capital=5,
        previsao_valor_livre=0,
        saldo_livre=0
    )

    # Mock do método do PAA
    paa.get_total_recursos_proprios = lambda: Decimal("500")

    from sme_ptrf_apps.paa.services.plano_orcamentario_service import PlanoOrcamentarioService
    plano = PlanoOrcamentarioService(paa).construir_plano_orcamentario()
    secao_outros = next((s for s in plano["secoes"] if s["key"] == "outros_recursos"), None)

    resultado = criar_recursos_proprios(paa, secao_outros)

    # Itens de recurso próprio
    assert len(resultado["items"]) == 2

    # Totais de recurso próprio
    assert resultado["total_recursos_proprios"] == Decimal("500")
    assert resultado["total_prioridades_recursos_proprios"] == Decimal("200")
    assert resultado["saldo_recursos_proprios"] == Decimal("300")

    # Outros recursos
    assert len(resultado["items_outros_recursos"]) == 1
    item_outro = resultado["items_outros_recursos"][0]

    assert item_outro["total_despesa_custeio"] == 80
    assert item_outro["total_despesa_capital"] == 20

    assert item_outro["total_receita_custeio"] == 160
    assert item_outro["total_receita_capital"] == 60

    # Totais finais
    assert resultado["total_receitas"] == Decimal("720")
    assert resultado["total_despesas"] == Decimal("300")

    assert resultado["total_saldo"] == resultado["total_receitas"] - resultado["total_despesas"]


@pytest.fixture
def acao_associacao_ativa(associacao, acao):
    """Fixture para AcaoAssociacao ativa"""
    return baker.make(
        "AcaoAssociacao",
        associacao=associacao,
        acao=acao,
        status="ATIVA",
    )


@pytest.fixture
def acao_associacao_inativa(associacao):
    """Fixture para AcaoAssociacao inativa"""
    acao = baker.make("Acao", nome="Ação Inativa")
    return baker.make(
        "AcaoAssociacao",
        associacao=associacao,
        acao=acao,
        status="INATIVA",
    )


@pytest.mark.django_db
class TestCriaPresidenteDiretoriaExecutiva:
    """Testes para a função cria_presidente_diretoria_executiva"""

    def test_cria_presidente_com_flag_ativa(self, associacao):
        """Testa quando flag historico-de-membros está ativa"""
        # Cria a flag ativa
        baker.make(
            "waffle.Flag",
            name="historico-de-membros",
            everyone=True,
        )

        mock_presidente = Mock()
        mock_presidente.nome = "João Presidente"

        with patch(
            "sme_ptrf_apps.paa.services.dados_documento_paa_service.ServicoCargosDaComposicao"
        ) as mock_servico:
            mock_instance = mock_servico.return_value
            mock_instance.get_presidente_diretoria_executiva_composicao_vigente.return_value = mock_presidente

            resultado = cria_presidente_diretoria_executiva(associacao)

            assert resultado == mock_presidente
            mock_servico.assert_called_once()
            mock_instance.get_presidente_diretoria_executiva_composicao_vigente.assert_called_once_with(
                associacao
            )

    def test_cria_presidente_com_flag_inativa(self, associacao):
        """Testa quando flag historico-de-membros está inativa"""
        mock_presidente = Mock()
        mock_presidente.nome = "Maria Presidente"

        with patch(
            "sme_ptrf_apps.paa.services.dados_documento_paa_service.MembroAssociacao"
        ) as mock_membro:
            mock_membro.get_presidente_diretoria_executiva.return_value = mock_presidente

            resultado = cria_presidente_diretoria_executiva(associacao)

            assert resultado == mock_presidente
            mock_membro.get_presidente_diretoria_executiva.assert_called_once_with(
                associacao
            )


@pytest.fixture
def atividade_estatutaria_tipo_a():
    """Fixture para atividade estatutária tipo A"""
    return baker.make(
        "AtividadeEstatutaria",
        nome="Assembleia Geral Ordinária",
        tipo="TIPO_A",
        mes=3,
    )


@pytest.fixture
def atividade_estatutaria_tipo_b():
    """Fixture para atividade estatutária tipo B"""
    return baker.make(
        "AtividadeEstatutaria",
        nome="Reunião de Diretoria",
        tipo="TIPO_B",
        mes=6,
        ativo=True,
    )


@pytest.fixture
def atividade_estatutaria_inativa():
    """Fixture para atividade estatutária inativa"""
    return baker.make(
        "AtividadeEstatutaria",
        nome="Atividade Desativada",
        tipo="TIPO_A",
        mes=9,
        ativo=False,
    )


@pytest.fixture
def atividade_estatutaria_paa(paa, atividade_estatutaria_tipo_a):
    """Fixture para AtividadeEstatutariaPaa"""
    return baker.make(
        "AtividadeEstatutariaPaa",
        paa=paa,
        atividade_estatutaria=atividade_estatutaria_tipo_a,
        data=date(2024, 3, 15),
    )


@pytest.mark.django_db
class TestCriarAtividadesEstatutarias:
    """Testes para a função criar_atividades_estatutarias"""

    def test_criar_atividades_estatutarias_retorna_lista(self, paa):
        """Testa se retorna uma lista"""
        resultado = criar_atividades_estatutarias(paa)

        assert isinstance(resultado, list)

    def test_criar_atividades_estatutarias_lista_vazia_sem_atividades(self, paa):
        """Testa retorno quando não há atividades disponíveis"""
        resultado = criar_atividades_estatutarias(paa)

        assert resultado == []

    def test_criar_atividades_estatutarias_estrutura_item(
        self,
        paa,
        atividade_estatutaria_tipo_a,
        atividade_estatutaria_paa,
    ):
        """Testa a estrutura de cada item retornado"""
        resultado = criar_atividades_estatutarias(paa)

        assert len(resultado) == 1

        item = resultado[0]
        assert "tipo_atividade" in item
        assert "data" in item
        assert "atividades_previstas" in item
        assert "mes_ano" in item


def test_secao_plano_para_documento_receitas_mapeia_linhas_e_totais():
    """
    Garante que _secao_plano_para_documento_receitas:
    - respeita exibirCusteio/exibirCapital/exibirLivre
    - monta a lista 'linhas' corretamente
    - propaga totais da linha isTotal.
    """
    secao = {
        "linhas": [
            {
                "nome": "Ação 1",
                "exibirCusteio": True,
                "exibirCapital": False,
                "exibirLivre": True,
                "receitas": {"custeio": 10, "capital": 0, "livre": 5, "total": 15},
                "despesas": {"custeio": 3, "capital": 0, "livre": 0, "total": 3},
                "saldos": {"custeio": 7, "capital": 0, "livre": 5, "total": 12},
            },
            {
                "nome": "Ação 2",
                "exibirCusteio": False,
                "exibirCapital": True,
                "exibirLivre": False,
                "receitas": {"custeio": 0, "capital": 20, "livre": 0, "total": 20},
                "despesas": {"custeio": 0, "capital": 4, "livre": 0, "total": 4},
                "saldos": {"custeio": 0, "capital": 16, "livre": 0, "total": 16},
            },
            {
                # linha que não deve aparecer (todas as flags falsas)
                "nome": "Ação ignorada",
                "exibirCusteio": False,
                "exibirCapital": False,
                "exibirLivre": False,
                "receitas": {"custeio": 0, "capital": 0, "livre": 0, "total": 0},
                "despesas": {"custeio": 0, "capital": 0, "livre": 0, "total": 0},
                "saldos": {"custeio": 0, "capital": 0, "livre": 0, "total": 0},
            },
            {
                "isTotal": True,
                "receitas": {"total": 35},
                "despesas": {"total": 7},
                "saldos": {"total": 28},
            },
        ]
    }

    resultado = _secao_plano_para_documento_receitas(secao)

    assert resultado["total_receitas"] == 35
    assert resultado["total_despesas"] == 7
    assert resultado["total_saldo"] == 28

    assert len(resultado["items"]) == 2

    acao1, acao2 = resultado["items"]

    assert acao1["nome"] == "Ação 1"
    labels_acao1 = [linha["label"] for linha in acao1["linhas"]]
    assert labels_acao1 == ["Custeio (R$)", "Livre Aplicação (R$)"]

    assert acao2["nome"] == "Ação 2"
    labels_acao2 = [linha["label"] for linha in acao2["linhas"]]
    assert labels_acao2 == ["Capital (R$)"]


@pytest.mark.django_db
def test_criar_recursos_proprios_sem_outros_recursos_usa_fallback(
    paa,
    prioridade_paa_factory,
    recurso_proprio_paa_factory,
):
    """
    Quando não há seção 'outros_recursos' no plano (nenhum Outro Recurso),
    criar_recursos_proprios deve calcular os totais apenas com Recursos Próprios
    e retornar items_outros_recursos vazio.
    """
    recurso_proprio_paa_factory(
        paa=paa,
        associacao=paa.associacao,
        valor=Decimal("100"),
        descricao="Recurso 1",
    )
    recurso_proprio_paa_factory(
        paa=paa,
        associacao=paa.associacao,
        valor=Decimal("200"),
        descricao="Recurso 2",
    )

    prioridade_paa_factory(
        paa=paa,
        recurso="RECURSO_PROPRIO",
        valor_total=Decimal("120"),
        prioridade=True,
    )

    paa.get_total_recursos_proprios = lambda: Decimal("300")

    resultado = criar_recursos_proprios(paa, secao_outros_recursos=None)

    assert resultado["items_outros_recursos"] == []

    assert resultado["total_recursos_proprios"] == Decimal("300")
    assert resultado["total_prioridades_recursos_proprios"] == Decimal("120")
    assert resultado["saldo_recursos_proprios"] == Decimal("180")

    assert resultado["total_receitas"] == Decimal("300")
    assert resultado["total_despesas"] == Decimal("120")
    assert resultado["total_saldo"] == Decimal("180")

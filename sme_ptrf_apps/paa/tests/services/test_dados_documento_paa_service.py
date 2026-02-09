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
    criar_receitas_previstas,
    criar_receitas_previstas_pdde,
    cria_presidente_diretoria_executiva,
)


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

    assert item_outro["total_receita_custeio"] == Decimal("160")
    assert item_outro["total_receita_capital"] == Decimal("60")

    # Totais finais
    assert resultado["total_receitas"] == Decimal("720")
    assert resultado["total_despesas"] == Decimal("300")

    assert resultado["total_saldo"] == resultado["total_receitas"] - resultado["total_despesas"]


@pytest.fixture
def acao_associacao_ativa(associacao, acao):
    """Fixture para AcaoAssociacao ativa"""
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=acao,
        status='ATIVA'
    )


@pytest.fixture
def acao_associacao_inativa(associacao):
    """Fixture para AcaoAssociacao inativa"""
    acao = baker.make('Acao', nome='Ação Inativa')
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=acao,
        status='INATIVA'
    )


@pytest.fixture
def receita_prevista_paa(paa, acao_associacao_ativa):
    """Fixture para ReceitaPrevistaPaa"""
    return baker.make(
        'ReceitaPrevistaPaa',
        paa=paa,
        acao_associacao=acao_associacao_ativa,
        previsao_valor_custeio=Decimal('1000.00'),
        previsao_valor_capital=Decimal('500.00'),
        previsao_valor_livre=Decimal('200.00')
    )


@pytest.mark.django_db
class TestCriarReceitasPrevistas:
    """Testes para a função criar_receitas_previstas"""

    def test_criar_receitas_previstas_estrutura_retorno(self, paa):
        """Testa se retorna a estrutura esperada"""
        resultado = criar_receitas_previstas(paa)

        assert isinstance(resultado, dict)
        assert 'items' in resultado
        assert 'total_receitas' in resultado
        assert 'total_despesas' in resultado
        assert 'total_saldo' in resultado
        assert isinstance(resultado['items'], list)

    def test_criar_receitas_previstas_sem_acoes_ativas(self, paa):
        """Testa com PAA sem ações ativas"""
        resultado = criar_receitas_previstas(paa)

        assert resultado['items'] == []
        assert resultado['total_receitas'] == 0
        assert resultado['total_despesas'] == 0
        assert resultado['total_saldo'] == 0

    def test_criar_receitas_previstas_ignora_acoes_inativas(
        self,
        paa,
        acao_associacao_inativa
    ):
        """Testa se ignora ações inativas"""
        resultado = criar_receitas_previstas(paa)

        assert len(resultado['items']) == 0

    def test_criar_receitas_previstas_com_uma_acao(
        self,
        paa,
        acao_associacao_ativa,
        receita_prevista_paa
    ):
        """Testa com uma ação ativa"""
        with patch.object(
            type(acao_associacao_ativa),
            'saldo_atual',
            return_value={
                'saldo_atual_custeio': Decimal('300.00'),
                'saldo_atual_capital': Decimal('150.00'),
                'saldo_atual_livre': Decimal('50.00')
            }
        ):
            resultado = criar_receitas_previstas(paa)

            assert len(resultado['items']) == 1

            item = resultado['items'][0]
            assert item['nome'] == acao_associacao_ativa.acao.nome
            assert item['total_receita_custeio'] == Decimal('1300.00')  # 1000 + 300
            assert item['total_receita_capital'] == Decimal('650.00')   # 500 + 150
            assert item['total_receita_livre'] == Decimal('250.00')     # 200 + 50


@pytest.fixture
def acao_pdde_ativa_1():
    """Fixture para AcaoPdde ativa"""
    return baker.make(
        'AcaoPdde',
        nome='PDDE Básico',
        status='ATIVA'
    )


@pytest.fixture
def acao_pdde_inativa():
    """Fixture para AcaoPdde inativa"""
    return baker.make(
        'AcaoPdde',
        nome='PDDE Inativa',
        status='INATIVA'
    )


# @pytest.fixture
# def receita_prevista_pdde(paa, acao_pdde_ativa):
#     """Fixture para ReceitaPrevistaPdde"""
#     return baker.make(
#         'ReceitaPrevistaPdde',
#         paa=paa,
#         acao_pdde=acao_pdde_ativa,
#         previsao_valor_custeio=Decimal('2000.00'),
#         saldo_custeio=Decimal('300.00'),
#         previsao_valor_capital=Decimal('1000.00'),
#         saldo_capital=Decimal('150.00'),
#         previsao_valor_livre=Decimal('500.00'),
#         saldo_livre=Decimal('50.00')
#     )


@pytest.mark.django_db
class TestCriarReceitaPrevistasPdde:
    """Testes para a função criar_receitas_previstas_pdde"""

    def test_criar_receitas_previstas_pdde_estrutura_retorno(self, paa):
        """Testa se retorna a estrutura esperada"""
        resultado = criar_receitas_previstas_pdde(paa)

        assert isinstance(resultado, dict)
        assert 'items' in resultado
        assert 'total_receitas' in resultado
        assert 'total_despesas' in resultado
        assert 'total_saldo' in resultado
        assert isinstance(resultado['items'], list)

    def test_criar_receitas_previstas_pdde_sem_acoes(self, paa):
        """Testa com PAA sem ações PDDE"""
        resultado = criar_receitas_previstas_pdde(paa)

        assert resultado['items'] == []
        assert resultado['total_receitas'] == 0
        assert resultado['total_despesas'] == 0
        assert resultado['total_saldo'] == 0

    def test_criar_receitas_previstas_pdde_ignora_inativas(
        self,
        paa,
        acao_pdde_inativa
    ):
        """Testa se ignora ações PDDE inativas"""
        resultado = criar_receitas_previstas_pdde(paa)

        assert len(resultado['items']) == 0

    def test_criar_receitas_previstas_pdde_com_acao(
        self,
        paa,
        receita_prevista_pdde
    ):
        """Testa com uma ação PDDE ativa"""
        resultado = criar_receitas_previstas_pdde(paa)

        assert len(resultado['items']) == 1, resultado['items']

    def test_criar_receitas_previstas_pdde_sem_receita_prevista(
        self,
        paa,
        acao_pdde_ativa_1
    ):
        """Testa quando não há receita prevista cadastrada"""
        resultado = criar_receitas_previstas_pdde(paa)

        item = resultado['items'][0]
        assert item['total_receita_custeio'] == 0
        assert item['total_receita_capital'] == 0
        assert item['total_receita_livre'] == 0


@pytest.mark.django_db
class TestCriaPresidenteDiretoriaExecutiva:
    """Testes para a função cria_presidente_diretoria_executiva"""

    def test_cria_presidente_com_flag_ativa(self, associacao):
        """Testa quando flag historico-de-membros está ativa"""
        # Cria a flag ativa
        baker.make(
            'waffle.Flag',
            name='historico-de-membros',
            everyone=True
        )

        mock_presidente = Mock()
        mock_presidente.nome = 'João Presidente'

        with patch('sme_ptrf_apps.paa.services.dados_documento_paa_service.ServicoCargosDaComposicao') as mock_servico:
            mock_instance = mock_servico.return_value
            mock_instance.get_presidente_diretoria_executiva_composicao_vigente.return_value = mock_presidente

            resultado = cria_presidente_diretoria_executiva(associacao)

            assert resultado == mock_presidente
            mock_servico.assert_called_once()
            mock_instance.get_presidente_diretoria_executiva_composicao_vigente.assert_called_once_with(associacao)

    def test_cria_presidente_com_flag_inativa(self, associacao):
        """Testa quando flag historico-de-membros está inativa"""
        mock_presidente = Mock()
        mock_presidente.nome = 'Maria Presidente'

        with patch('sme_ptrf_apps.paa.services.dados_documento_paa_service.MembroAssociacao') as mock_membro:
            mock_membro.get_presidente_diretoria_executiva.return_value = mock_presidente

            resultado = cria_presidente_diretoria_executiva(associacao)

            assert resultado == mock_presidente
            mock_membro.get_presidente_diretoria_executiva.assert_called_once_with(associacao)


@pytest.fixture
def atividade_estatutaria_tipo_a():
    """Fixture para atividade estatutária tipo A"""
    return baker.make(
        'AtividadeEstatutaria',
        nome='Assembleia Geral Ordinária',
        tipo='TIPO_A',
        mes=3,
    )


@pytest.fixture
def atividade_estatutaria_tipo_b():
    """Fixture para atividade estatutária tipo B"""
    return baker.make(
        'AtividadeEstatutaria',
        nome='Reunião de Diretoria',
        tipo='TIPO_B',
        mes=6,
        ativo=True
    )


@pytest.fixture
def atividade_estatutaria_inativa():
    """Fixture para atividade estatutária inativa"""
    return baker.make(
        'AtividadeEstatutaria',
        nome='Atividade Desativada',
        tipo='TIPO_A',
        mes=9,
        ativo=False
    )


@pytest.fixture
def atividade_estatutaria_paa(paa, atividade_estatutaria_tipo_a):
    """Fixture para AtividadeEstatutariaPaa"""
    return baker.make(
        'AtividadeEstatutariaPaa',
        paa=paa,
        atividade_estatutaria=atividade_estatutaria_tipo_a,
        data=date(2024, 3, 15)
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
        atividade_estatutaria_paa
    ):
        """Testa a estrutura de cada item retornado"""
        resultado = criar_atividades_estatutarias(paa)

        assert len(resultado) == 1

        item = resultado[0]
        assert 'tipo_atividade' in item
        assert 'data' in item
        assert 'atividades_previstas' in item
        assert 'mes_ano' in item

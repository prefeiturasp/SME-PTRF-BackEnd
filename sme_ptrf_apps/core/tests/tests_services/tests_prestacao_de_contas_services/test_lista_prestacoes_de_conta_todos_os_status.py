import pytest
from model_bakery import baker
from datetime import date, datetime
from ....services.prestacao_contas_services import lista_prestacoes_de_conta_todos_os_status
pytestmark = pytest.mark.django_db


@pytest.fixture
def dre_teste_model_consolidado_dre():
    return baker.make(
        'Unidade',
        codigo_eol='108500',
        tipo_unidade='DRE',
        nome='Dre Teste Model Consolidado Dre',
        sigla='A',
        criado_em=datetime.now(),
    )


@pytest.fixture
def periodo_anterior():
    return baker.make(
        'Periodo',
        referencia='2019.1',
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 8, 31),
    )


@pytest.fixture
def associacao_teste_ata(dre_teste_model_consolidado_dre, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='52.302.275/0001-83',
        unidade=dre_teste_model_consolidado_dre,
        periodo_inicial=periodo_anterior,
        ccm='0.000.00-0',
        email="liniker.oliveira@gmail.com",
        processo_regularidade='123456'
    )


def test_lista_prestacoes_com_filtro_por_devolucao_tesouro(dre_teste_model_consolidado_dre, periodo_anterior):
    # Arrange
    filtro_por_devolucao_tesouro = '1'

    # Act
    prestacoes = lista_prestacoes_de_conta_todos_os_status(
        dre=dre_teste_model_consolidado_dre,
        periodo=periodo_anterior,
        filtro_por_devolucao_tesouro=filtro_por_devolucao_tesouro
    )

    assert not prestacoes
    assert len(prestacoes) == 0

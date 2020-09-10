import pytest
from model_bakery import baker
from rest_framework import status

from ...models import TecnicoDre, Atribuicao

pytestmark = pytest.mark.django_db


def test_delete_tecnico_dre(jwt_authenticated_client, tecnico_jose_dre_ipiranga):
    assert TecnicoDre.objects.filter(uuid=tecnico_jose_dre_ipiranga.uuid).exists()

    response = jwt_authenticated_client.delete(
        f'/api/tecnicos-dre/{tecnico_jose_dre_ipiranga.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not TecnicoDre.objects.filter(uuid=tecnico_jose_dre_ipiranga.uuid).exists()


@pytest.fixture
def tecnico_1(dre):
    return baker.make(
        'TecnicoDre',
        dre=dre,
        nome='Tecnico 1',
        rf='111111',
    )


@pytest.fixture
def tecnico_2(dre):
    return baker.make(
        'TecnicoDre',
        dre=dre,
        nome='Tecnico 2',
        rf='222222',
    )


@pytest.fixture
def unidade_a(dre):
    return baker.make(
        'Unidade',
        nome='Escola A',
        tipo_unidade='EMEI',
        codigo_eol='111111',
        dre=dre,
    )


@pytest.fixture
def unidade_b(dre):
    return baker.make(
        'Unidade',
        nome='Escola B',
        tipo_unidade='EMEI',
        codigo_eol='222222',
        dre=dre,
    )


@pytest.fixture
def atribuicao_unidade_a(tecnico_1, tecnico_2, unidade_a, periodo):
    return baker.make(
        'Atribuicao',
        tecnico=tecnico_1,
        unidade=unidade_a,
        periodo=periodo,
    )


@pytest.fixture
def atribuicao_unidade_b(tecnico_1, tecnico_2, unidade_b, periodo):
    return baker.make(
        'Atribuicao',
        tecnico=tecnico_1,
        unidade=unidade_b,
        periodo=periodo,
    )


def test_delete_tecnico_dre_transferindo_atribuicoes(jwt_authenticated_client, tecnico_1, tecnico_2, unidade_a,
                                                     unidade_b, atribuicao_unidade_a, atribuicao_unidade_b):


    assert Atribuicao.objects.filter(tecnico=tecnico_1).exists(), "Deveria iniciar com atribuições para o técnico 1"
    assert not Atribuicao.objects.filter(tecnico=tecnico_2).exists(), "Não devia iniciar com atribuições para o técnico 2"

    response = jwt_authenticated_client.delete(
        f'/api/tecnicos-dre/{tecnico_1.uuid}/?transferir_para={tecnico_2.uuid}', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Atribuicao.objects.filter(tecnico=tecnico_1).exists(), "Não deveria iniciar haver atribuições para o técnico 1"
    assert Atribuicao.objects.filter(tecnico=tecnico_2).exists(), "Deveria haver atribuições para o técnico 2"

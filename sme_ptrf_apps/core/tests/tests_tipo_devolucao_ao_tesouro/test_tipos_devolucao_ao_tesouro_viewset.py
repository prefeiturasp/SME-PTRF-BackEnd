import pytest
from datetime import date

from model_bakery import baker

from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.tipos_devolucao_ao_tesouro_viewset import TiposDevolucaoAoTesouroViewSet
from ...models import TipoDevolucaoAoTesouro
from sme_ptrf_apps.core.models import PrestacaoConta

pytestmark = pytest.mark.django_db

@pytest.fixture
def tipo_devolucao_ao_tesouro():
    return baker.make('TipoDevolucaoAoTesouro', nome='Teste')

@pytest.fixture
def prestacao_conta_em_analise(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2025, 10, 1),
        status=PrestacaoConta.STATUS_EM_ANALISE
    )


@pytest.fixture
def devolucao_ao_tesouro_com_tipo_devolucao_ao_tesouro(
        prestacao_conta_em_analise,
        tipo_devolucao_ao_tesouro,
        despesa):
    return baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=prestacao_conta_em_analise,
        tipo=tipo_devolucao_ao_tesouro,
        data=date(2025, 7, 1),
        despesa=despesa,
        devolucao_total=True,
        valor=100.00,
        motivo='teste',
    )


def test_view_set(tipo_devolucao_ao_tesouro, usuario_permissao_associacao):
    request = APIRequestFactory().get("")
    detalhe = TiposDevolucaoAoTesouroViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=tipo_devolucao_ao_tesouro.uuid)

    assert response.status_code == status.HTTP_200_OK


def test_filtra_tipo_devolucao_ao_tesouro_por_nome(jwt_authenticated_client, tipo_devolucao_ao_tesouro):
    url = "/api/tipos-devolucao-ao-tesouro/?nome=Teste"
    response = jwt_authenticated_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1, response.data
    assert response.data[0]['nome'] == "Teste"


def test_excluir_tipo_devolucao_ao_tesouro_sem_devolucao(jwt_authenticated_client, tipo_devolucao_ao_tesouro):
    url = f"/api/tipos-devolucao-ao-tesouro/{tipo_devolucao_ao_tesouro.uuid}/"
    response = jwt_authenticated_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_excluir_tipo_devolucao_ao_tesouro_com_devolucao(jwt_authenticated_client,
                                                         devolucao_ao_tesouro_com_tipo_devolucao_ao_tesouro,
                                                         tipo_devolucao_ao_tesouro):

    url = f"/api/tipos-devolucao-ao-tesouro/{tipo_devolucao_ao_tesouro.uuid}/"
    response = jwt_authenticated_client.delete(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'ProtectedError'
    assert response.data['mensagem'] == (
        'Essa operação não pode ser realizada. Há lançamentos '+
                'cadastradas com esse motivo de devolução ao tesouro.'
    )
    assert TipoDevolucaoAoTesouro.objects.filter(uuid=tipo_devolucao_ao_tesouro.uuid).exists()

import pytest
from datetime import datetime
from rest_framework import status

from sme_ptrf_apps.core.models import ProcessoAssociacao

pytestmark = pytest.mark.django_db

def test_delete_processo_associacao(jwt_authenticated_client_a, processo_associacao_123456_2019):
    assert ProcessoAssociacao.objects.filter(uuid=processo_associacao_123456_2019.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/processos-associacao/{processo_associacao_123456_2019.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not ProcessoAssociacao.objects.filter(uuid=processo_associacao_123456_2019.uuid).exists()


def test_delete_processo_associacao_ultimo_processo_e_com_pc_vinculada(jwt_authenticated_client_a, processo_associacao_factory, periodo_factory, prestacao_conta_factory):
    processo_com_pc_vinculada = processo_associacao_factory.create(ano='2023')
    periodo = periodo_factory.create(data_inicio_realizacao_despesas=datetime(2023, 1, 1))
    prestacao_conta_factory.create(periodo=periodo, associacao=processo_com_pc_vinculada.associacao)

    response = jwt_authenticated_client_a.delete(
        f'/api/processos-associacao/{processo_com_pc_vinculada.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {'erro': 'possui_prestacao_de_conta_vinculada', 'mensagem': 'Não é possível excluir o número desse processo SEI, pois este já está vinculado a uma prestação de contas. Caso necessário, é possível editá-lo.'}

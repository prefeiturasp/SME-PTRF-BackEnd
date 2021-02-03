import json

import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import AcaoAssociacao

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_acao_associacao(associacao_charli_bravo_000086, acao_x):
    payload = {
        'associacao': f'{associacao_charli_bravo_000086.uuid}',
        'acao': f'{acao_x.uuid}',
        'status': AcaoAssociacao.STATUS_ATIVA,
    }
    return payload


def test_create_acao_associacao(
    jwt_authenticated_client_a,
    associacao_charli_bravo_000086,
    acao_x,
    payload_acao_associacao
):
    response = jwt_authenticated_client_a.post(
        '/api/acoes-associacoes/', data=json.dumps(payload_acao_associacao), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert AcaoAssociacao.objects.filter(uuid=result['uuid']).exists()


def test_create_acao_associacao_em_lote(
    jwt_authenticated_client_a,
    acao_x,
    associacao_eco_delta_000087,
    associacao_charli_bravo_000086
):
    payload = {
        'acao_uuid': f'{acao_x.uuid}',
        'associacoes_uuids': [f'{associacao_charli_bravo_000086.uuid}', f'{associacao_eco_delta_000087.uuid}'],
    }

    response = jwt_authenticated_client_a.post(
        f'/api/acoes-associacoes/incluir-lote/',
        data=json.dumps(payload),
        content_type='application/json')

    result = json.loads(response.content)

    esperado = {
        'erros': [],
        'mensagem': 'Unidades vinculadas à ação com sucesso.'
    }

    assert response.status_code == status.HTTP_201_CREATED
    assert result == esperado
    assert AcaoAssociacao.objects.exists()


def test_create_acao_associacao_em_lote_uuid_acao_invalido(
    jwt_authenticated_client_a,
    acao_x,
    associacao_eco_delta_000087,
    associacao_charli_bravo_000086,
):
    payload = {
        'acao_uuid': f'{associacao_charli_bravo_000086.uuid}',
        'associacoes_uuids': [f'{associacao_charli_bravo_000086.uuid}', f'{associacao_eco_delta_000087.uuid}'],
    }

    response = jwt_authenticated_client_a.post(
        f'/api/acoes-associacoes/incluir-lote/',
        data=json.dumps(payload),
        content_type='application/json')

    result = json.loads(response.content)

    esperado = {'erro': 'Objeto não encontrado.',
                'mensagem': f'O objeto ação para o uuid {associacao_charli_bravo_000086.uuid} '
                            'não foi encontrado na base.'}

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado
    assert not AcaoAssociacao.objects.exists()


def test_create_acao_associacao_em_lote_uuid_associacao_invalido(
    jwt_authenticated_client_a,
    acao_x,
    associacao_eco_delta_000087,
    associacao_charli_bravo_000086
):
    payload = {
        'acao_uuid': f'{acao_x.uuid}',
        'associacoes_uuids': [f'{acao_x.uuid}', f'{associacao_eco_delta_000087.uuid}'],
    }

    response = jwt_authenticated_client_a.post(
        f'/api/acoes-associacoes/incluir-lote/',
        data=json.dumps(payload),
        content_type='application/json')

    result = json.loads(response.content)

    esperado = {
        'erros': [
            {
                'erro': 'Associação não encontrada',
                'mensagem': 'O objeto associação para o uuid '
                            f'{acao_x.uuid} não foi '
                            'encontrado na base.'
            }
        ],
        'mensagem': 'Alguns vínculos não puderam ser feitos.'
    }

    assert response.status_code == status.HTTP_201_CREATED
    assert result == esperado
    assert AcaoAssociacao.objects.exists()

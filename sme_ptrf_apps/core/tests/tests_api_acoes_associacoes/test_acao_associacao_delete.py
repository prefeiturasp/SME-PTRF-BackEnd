import json

import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import AcaoAssociacao

pytestmark = pytest.mark.django_db


def test_delete_acao_associacao(
    jwt_authenticated_client_a,
    acao_associacao_charli_bravo_000086_x
):
    assert AcaoAssociacao.objects.filter(uuid=acao_associacao_charli_bravo_000086_x.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/acoes-associacoes/{acao_associacao_charli_bravo_000086_x.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not AcaoAssociacao.objects.filter(uuid=acao_associacao_charli_bravo_000086_x.uuid).exists()


def test_delete_acao_associacao_ja_usada(
    jwt_authenticated_client_a,
    acao_associacao_eco_delta_000087_x,
    receita_usando_acao_associacao_eco_delta_x
):

    response = jwt_authenticated_client_a.delete(
        f'/api/acoes-associacoes/{acao_associacao_eco_delta_000087_x.uuid}/', content_type='application/json')

    result = json.loads(response.content)

    esperado = {
        "erro": 'ProtectedError',
        "mensagem": "Essa ação de associação não pode ser excluida porque está sendo usada na aplicação.",
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado


def test_delete_acao_associacao_em_lote_com_usados(
    jwt_authenticated_client_a,
    acao_associacao_charli_bravo_000086_x,
    acao_associacao_eco_delta_000087_x,
    receita_usando_acao_associacao_eco_delta_x
):
    payload = {
        'lista_uuids': [f'{acao_associacao_charli_bravo_000086_x.uuid}', f'{acao_associacao_eco_delta_000087_x.uuid}'],
    }

    response = jwt_authenticated_client_a.post(
        f'/api/acoes-associacoes/excluir-lote/',
        data=json.dumps(payload),
        content_type='application/json')

    result = json.loads(response.content)

    esperado = {
        'erros': [
            {
                'erro': 'ProtectedError',
                'mensagem': f'O vínculo de ação e associação de uuid '
                            f'{acao_associacao_eco_delta_000087_x.uuid} não pode ser '
                            f'excluido porque está sendo usado na aplicação.'
            }
        ],
        'mensagem': 'Alguns vínculos não puderam ser desfeitos por já estarem sendo '
                    'usados na aplicação.'
    }

    # assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_delete_acao_associacao_em_lote_sem_usados(
    jwt_authenticated_client_a,
    acao_associacao_charli_bravo_000086_x,
    acao_associacao_eco_delta_000087_x,
):
    payload = {
        'lista_uuids': [f'{acao_associacao_charli_bravo_000086_x.uuid}', f'{acao_associacao_eco_delta_000087_x.uuid}'],
    }

    response = jwt_authenticated_client_a.post(
        f'/api/acoes-associacoes/excluir-lote/',
        data=json.dumps(payload),
        content_type='application/json')

    result = json.loads(response.content)

    esperado = {
        'erros': [],
        'mensagem': 'Unidades desvinculadas da ação com sucesso.'
    }

    # assert response.status_code == status.HTTP_200_OK
    assert result == esperado

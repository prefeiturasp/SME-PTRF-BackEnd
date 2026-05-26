import json

import pytest
from rest_framework import status

from sme_ptrf_apps.receitas.models import DetalheTipoReceita

pytestmark = pytest.mark.django_db


def test_list_detalhes_tipos_receitas_parametrizacao(
    jwt_authenticated_client_p,
    detalhe_tipo_receita_parametrizacao,
    detalhe_tipo_receita_parametrizacao_02,
):
    response = jwt_authenticated_client_p.get(
        '/api/detalhes-tipos-receitas-parametrizacao/',
        content_type='application/json'
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert content['count'] == 2
    assert {item['nome'] for item in content['results']} == {'Detalhe 01', 'Detalhe 02'}


def test_list_detalhes_tipos_receitas_parametrizacao_por_nome(
    jwt_authenticated_client_p,
    detalhe_tipo_receita_parametrizacao,
    detalhe_tipo_receita_parametrizacao_02,
):
    response = jwt_authenticated_client_p.get(
        '/api/detalhes-tipos-receitas-parametrizacao/?nome=Detalhe 01',
        content_type='application/json'
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert content['count'] == 1
    assert content['results'][0]['nome'] == 'Detalhe 01'


def test_retrieve_detalhe_tipo_receita_parametrizacao(
    jwt_authenticated_client_p,
    detalhe_tipo_receita_parametrizacao,
):
    response = jwt_authenticated_client_p.get(
        f'/api/detalhes-tipos-receitas-parametrizacao/{detalhe_tipo_receita_parametrizacao.uuid}/',
        content_type='application/json'
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert content['id'] == detalhe_tipo_receita_parametrizacao.id
    assert content['nome'] == 'Detalhe 01'
    assert content['tipo_receita'] == str(detalhe_tipo_receita_parametrizacao.tipo_receita.uuid)
    assert content['tipo_receita_nome'] == detalhe_tipo_receita_parametrizacao.tipo_receita.nome
    assert content['can_edit_tipo_receita'] is True


def test_create_detalhe_tipo_receita_parametrizacao(jwt_authenticated_client_p, tipo_receita_com_detalhamento):
    payload = {
        'nome': '  Detalhe    novo  ',
        'tipo_receita': str(tipo_receita_com_detalhamento.uuid),
    }

    response = jwt_authenticated_client_p.post(
        '/api/detalhes-tipos-receitas-parametrizacao/',
        content_type='application/json',
        data=json.dumps(payload)
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED
    assert content['nome'] == 'Detalhe novo'
    assert content['tipo_receita'] == str(tipo_receita_com_detalhamento.uuid)
    assert content['tipo_receita_nome'] == tipo_receita_com_detalhamento.nome
    assert DetalheTipoReceita.objects.filter(uuid=content['uuid'], nome='Detalhe novo').exists()


def test_create_erro_tipo_receita_sem_detalhamento(jwt_authenticated_client_p, tipo_receita):
    payload = {
        'nome': 'Detalhe invalido',
        'tipo_receita': str(tipo_receita.uuid),
    }

    response = jwt_authenticated_client_p.post(
        '/api/detalhes-tipos-receitas-parametrizacao/',
        content_type='application/json',
        data=json.dumps(payload)
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert content == {
        'non_field_errors': 'Não é possível associar um detalhe a um tipo de receita que não permite detalhamento.'
    }


def test_create_erro_detalhe_duplicado(jwt_authenticated_client_p, detalhe_tipo_receita_parametrizacao):
    payload = {
        'nome': 'Detalhe 01',
        'tipo_receita': str(detalhe_tipo_receita_parametrizacao.tipo_receita.uuid),
    }

    response = jwt_authenticated_client_p.post(
        '/api/detalhes-tipos-receitas-parametrizacao/',
        content_type='application/json',
        data=json.dumps(payload)
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert content == {'non_field_errors': 'Este detalhe já existe para esse tipo de receita.'}


def test_patch_detalhe_tipo_receita_parametrizacao(
    jwt_authenticated_client_p,
    detalhe_tipo_receita_parametrizacao,
):
    payload = {
        'nome': 'Detalhe 01 atualizado',
        'tipo_receita': str(detalhe_tipo_receita_parametrizacao.tipo_receita.uuid),
    }

    response = jwt_authenticated_client_p.patch(
        f'/api/detalhes-tipos-receitas-parametrizacao/{detalhe_tipo_receita_parametrizacao.uuid}/',
        content_type='application/json',
        data=json.dumps(payload)
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert content['nome'] == 'Detalhe 01 atualizado'
    assert content['tipo_receita'] == str(detalhe_tipo_receita_parametrizacao.tipo_receita.uuid)


def test_delete_detalhe_tipo_receita_parametrizacao(
    jwt_authenticated_client_p,
    detalhe_tipo_receita_parametrizacao,
):
    response = jwt_authenticated_client_p.delete(
        f'/api/detalhes-tipos-receitas-parametrizacao/{detalhe_tipo_receita_parametrizacao.uuid}/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not DetalheTipoReceita.objects.filter(uuid=detalhe_tipo_receita_parametrizacao.uuid).exists()


def test_delete_erro_com_receitas_associadas(
    jwt_authenticated_client_p,
    detalhe_tipo_receita_parametrizacao_com_receita,
):
    response = jwt_authenticated_client_p.delete(
        f'/api/detalhes-tipos-receitas-parametrizacao/{detalhe_tipo_receita_parametrizacao_com_receita.uuid}/',
        content_type='application/json'
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert content == {
        'mensagem': (
            'Essa operação não pode ser realizada. '
            'Há receitas associadas a esse detalhe de tipo de receita.'
        )
    }

import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def despesa_outra_unidade(despesa_factory, associacao_iniciada_2020_2, tipo_documento, tipo_transacao):
    return despesa_factory(
        associacao=associacao_iniciada_2020_2,
        tipo_documento=tipo_documento,
        tipo_transacao=tipo_transacao,
        valor_total=100,
    )


def test_retrieve_despesa_da_propria_ue(jwt_authenticated_client_d, despesa):
    response = jwt_authenticated_client_d.get(
        f'/api/despesas/{despesa.uuid}/',
        content_type='application/json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['uuid'] == str(despesa.uuid)


def test_retrieve_despesa_de_outra_ue_retorna_404(
    jwt_authenticated_client_d,
    despesa_outra_unidade,
):
    response = jwt_authenticated_client_d.get(
        f'/api/despesas/{despesa_outra_unidade.uuid}/',
        content_type='application/json',
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_despesa_de_outra_ue_retorna_404(
    jwt_authenticated_client_d,
    despesa_outra_unidade,
    payload_despesa_valida,
):
    response = jwt_authenticated_client_d.put(
        f'/api/despesas/{despesa_outra_unidade.uuid}/',
        data=json.dumps(payload_despesa_valida),
        content_type='application/json',
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_destroy_despesa_de_outra_ue_retorna_404(
    jwt_authenticated_client_d,
    despesa_outra_unidade,
):
    response = jwt_authenticated_client_d.delete(
        f'/api/despesas/{despesa_outra_unidade.uuid}/',
        content_type='application/json',
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_nao_inclui_despesa_de_outra_ue(
    jwt_authenticated_client_d,
    associacao,
    despesa,
    despesa_outra_unidade,
):
    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?associacao__uuid={associacao.uuid}',
        content_type='application/json',
    )
    assert response.status_code == status.HTTP_200_OK
    uuids = {item['uuid'] for item in response.json()['results']}
    assert str(despesa.uuid) in uuids
    assert str(despesa_outra_unidade.uuid) not in uuids


def test_list_associacao_de_outra_ue_vem_vazio(
    jwt_authenticated_client_d,
    associacao_iniciada_2020_2,
    despesa_outra_unidade,
):
    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?associacao__uuid={associacao_iniciada_2020_2.uuid}',
        content_type='application/json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['results'] == []


def test_retrieve_visao_dre_acessa_ue_da_dre(
    jwt_authenticated_client_d,
    usuario_permissao_despesa,
    dre,
    despesa,
):
    usuario_permissao_despesa.unidades.clear()
    usuario_permissao_despesa.unidades.add(dre)

    response = jwt_authenticated_client_d.get(
        f'/api/despesas/{despesa.uuid}/',
        content_type='application/json',
    )
    assert response.status_code == status.HTTP_200_OK


def test_retrieve_visao_dre_nao_acessa_ue_de_outra_dre(
    jwt_authenticated_client_d,
    usuario_permissao_despesa,
    dre,
    despesa_factory,
    tipo_documento,
    tipo_transacao,
):
    outra_dre = baker.make(
        'Unidade',
        codigo_eol='888880',
        tipo_unidade='DRE',
        nome='Outra DRE',
    )
    unidade_outra_dre = baker.make(
        'Unidade',
        codigo_eol='666660',
        tipo_unidade='CEU',
        nome='UE de outra DRE',
        dre=outra_dre,
    )
    associacao_outra_dre = baker.make(
        'Associacao',
        unidade=unidade_outra_dre,
        cnpj='11.111.111/0001-11',
        nome='Associação outra DRE',
    )
    despesa_outra_dre = despesa_factory(
        associacao=associacao_outra_dre,
        tipo_documento=tipo_documento,
        tipo_transacao=tipo_transacao,
        valor_total=100,
    )

    usuario_permissao_despesa.unidades.clear()
    usuario_permissao_despesa.unidades.add(dre)

    response = jwt_authenticated_client_d.get(
        f'/api/despesas/{despesa_outra_dre.uuid}/',
        content_type='application/json',
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_retrieve_visao_sme_acessa_ue_sem_vinculo_direto(
    jwt_authenticated_client_d,
    usuario_permissao_despesa,
    despesa_outra_unidade,
):
    visao_sme = baker.make('Visao', nome='SME')
    usuario_permissao_despesa.visoes.add(visao_sme)
    usuario_permissao_despesa.unidades.clear()

    response = jwt_authenticated_client_d.get(
        f'/api/despesas/{despesa_outra_unidade.uuid}/',
        content_type='application/json',
    )
    assert response.status_code == status.HTTP_200_OK


def test_retrieve_suporte_em_duas_ues_respeita_unidade_selecionada(
    jwt_authenticated_client_d,
    usuario_permissao_despesa,
    outra_unidade,
    associacao,
    associacao_iniciada_2020_2,
    despesa,
    despesa_outra_unidade,
):
    usuario_permissao_despesa.unidades.add(outra_unidade)

    response = jwt_authenticated_client_d.get(
        f'/api/despesas/{despesa.uuid}/?associacao__uuid={associacao_iniciada_2020_2.uuid}',
        content_type='application/json',
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_retrieve_suporte_em_duas_ues_acessa_quando_selecionada_e_a_da_despesa(
    jwt_authenticated_client_d,
    usuario_permissao_despesa,
    outra_unidade,
    associacao,
    despesa,
):
    usuario_permissao_despesa.unidades.add(outra_unidade)

    response = jwt_authenticated_client_d.get(
        f'/api/despesas/{despesa.uuid}/?associacao__uuid={associacao.uuid}',
        content_type='application/json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['uuid'] == str(despesa.uuid)

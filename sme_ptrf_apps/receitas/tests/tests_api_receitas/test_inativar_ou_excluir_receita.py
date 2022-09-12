import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_delete_receita_deve_excluir_nao_eh_estorno_nao_eh_repasse_nao_tem_pc(
    jwt_authenticated_client_p,
    associacao,
    receita_deve_exluir,
):

    receita_uuid = f"{receita_deve_exluir.uuid}"

    response = jwt_authenticated_client_p.delete(
        f'/api/receitas/{receita_uuid}/?associacao__uuid={associacao.uuid}',
        content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_receita_deve_inativar_tem_pc(
    jwt_authenticated_client_p,
    associacao,
    receita_deve_inativar,
    periodo_inativar_receita,
    prestacao_conta_devolvida_inativar_receita,
):

    receita_uuid = f"{receita_deve_inativar.uuid}"

    response = jwt_authenticated_client_p.delete(
        f'/api/receitas/{receita_uuid}/?associacao__uuid={associacao.uuid}',
        content_type='application/json')

    esperado = {
        'sucesso': 'receita_inativada_com_sucesso',
        'mensagem': 'Receita inativada com sucesso'
    }

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_delete_receita_nao_deve_excluir_e_estorno(
    jwt_authenticated_client_p,
    associacao,
    receita_nao_deve_exluir_estorno,
):

    receita_uuid = f"{receita_nao_deve_exluir_estorno.uuid}"

    response = jwt_authenticated_client_p.delete(
        f'/api/receitas/{receita_uuid}/?associacao__uuid={associacao.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    esperado = {
        'erro': 'receita_do_tipo_estorno',
        'mensagem': 'Não é possivel excluir uma receita do tipo estorno. Deve ser feito a partir da despesa.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado


def test_delete_receita_deve_excluir_e_repasse_sem_pc(
    jwt_authenticated_client_p,
    associacao,
    receita_deve_exluir_e_repasse,
):

    receita_uuid = f"{receita_deve_exluir_e_repasse.uuid}"

    response = jwt_authenticated_client_p.delete(
        f'/api/receitas/{receita_uuid}/?associacao__uuid={associacao.uuid}',
        content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_receita_deve_inativar_e_repasse_com_pc(
    jwt_authenticated_client_p,
    associacao,
    receita_deve_inativar_e_repasse,
    periodo_inativar_receita,
    prestacao_conta_devolvida_inativar_receita,
):

    receita_uuid = f"{receita_deve_inativar_e_repasse.uuid}"

    response = jwt_authenticated_client_p.delete(
        f'/api/receitas/{receita_uuid}/?associacao__uuid={associacao.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    esperado = {
        'sucesso': 'receita_inativada_com_sucesso',
        'mensagem': 'Receita inativada com sucesso'
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado

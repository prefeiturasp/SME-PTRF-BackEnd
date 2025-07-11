import json
import pytest
from freezegun import freeze_time
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_get_lista_adquiridos_e_produzidos(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1, bem_produzido_item_1, rateio_capital_1, rateio_custeio_1):

    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/?associacao_uuid={associacao_1.uuid}')
    content = json.loads(response.content)

    assert len(content["results"]) == 2
    assert response.status_code == status.HTTP_200_OK


@freeze_time('2025-01-01')
def test_get_lista_adquiridos_e_produzidos_com_filtro_acao_e_conta(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1, despesa_factory, rateio_despesa_factory, conta_associacao_factory, acao_associacao_factory):
    conta_associacao = conta_associacao_factory(associacao=associacao_1)
    acao_associacao = acao_associacao_factory(associacao=associacao_1)
    despesa_2025_1 = despesa_factory(associacao=associacao_1, data_documento='2025-01-01', nome_fornecedor='teste')
    _ = rateio_despesa_factory(
        associacao=associacao_1, despesa=despesa_2025_1, aplicacao_recurso="CAPITAL", conta_associacao=conta_associacao, acao_associacao=acao_associacao)
    _ = rateio_despesa_factory(
        associacao=associacao_1, despesa=despesa_2025_1, aplicacao_recurso="CAPITAL")

    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'acao_associacao_uuid={acao_associacao.uuid}&'
        f'conta_associacao_uuid={conta_associacao.uuid}'
    )
    content = json.loads(response.content)

    assert len(content["results"]) == 1
    assert response.status_code == status.HTTP_200_OK


@freeze_time('2025-01-01')
def test_get_lista_adquiridos_e_produzidos_com_filtro_fornecedor(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1, despesa_factory, rateio_despesa_factory):
    despesa_2025_1 = despesa_factory(associacao=associacao_1, data_documento='2025-01-01', nome_fornecedor='teste')
    _ = rateio_despesa_factory(
        associacao=associacao_1, despesa=despesa_2025_1, aplicacao_recurso="CAPITAL")
    _ = rateio_despesa_factory(
        associacao=associacao_1, despesa=despesa_2025_1, aplicacao_recurso="CAPITAL")

    print(despesa_2025_1.nome_fornecedor)
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'fornecedor=teste'
    )
    content = json.loads(response.content)

    assert len(content["results"]) == 2
    assert response.status_code == status.HTTP_200_OK


@freeze_time('2025-01-01')
def test_get_lista_adquiridos_e_produzidos_com_filtro_especificacao(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1, bem_produzido_1, despesa_factory, bem_produzido_item_factory, rateio_despesa_factory, especificacao_material_servico_1):
    _ = bem_produzido_item_factory(bem_produzido=bem_produzido_1, especificacao_do_bem=especificacao_material_servico_1)
    _ = bem_produzido_item_factory(bem_produzido=bem_produzido_1, especificacao_do_bem=especificacao_material_servico_1)
    _ = bem_produzido_item_factory(bem_produzido=bem_produzido_1, especificacao_do_bem=especificacao_material_servico_1)

    despesa_2025_1 = despesa_factory(associacao=associacao_1, data_documento='2025-01-01')
    _ = rateio_despesa_factory(
        associacao=associacao_1, despesa=despesa_2025_1, aplicacao_recurso="CAPITAL", especificacao_material_servico=especificacao_material_servico_1)
    _ = rateio_despesa_factory(
        associacao=associacao_1, despesa=despesa_2025_1, aplicacao_recurso="CAPITAL")

    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'especificacao_bem=especificacao do bem'
    )
    content = json.loads(response.content)

    assert len(content["results"]) == 4
    assert response.status_code == status.HTTP_200_OK


@freeze_time('2025-01-01')
def test_get_lista_adquiridos_e_produzidos_com_filtro_periodo(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1, bem_produzido_1, despesa_factory, bem_produzido_item_factory, rateio_despesa_factory, periodo_2025_1, periodo_2024_1):
    _ = bem_produzido_item_factory(bem_produzido=bem_produzido_1)
    _ = bem_produzido_item_factory(bem_produzido=bem_produzido_1)
    _ = bem_produzido_item_factory(bem_produzido=bem_produzido_1)

    despesa_2025_1 = despesa_factory(associacao=associacao_1, data_documento='2025-01-01')
    despesa_2024_1 = despesa_factory(associacao=associacao_1, data_documento='2024-01-01')
    _ = rateio_despesa_factory(
        associacao=associacao_1, despesa=despesa_2025_1, aplicacao_recurso="CAPITAL")
    _ = rateio_despesa_factory(
        associacao=associacao_1, despesa=despesa_2025_1, aplicacao_recurso="CAPITAL")
    _ = rateio_despesa_factory(
        associacao=associacao_1, despesa=despesa_2024_1, aplicacao_recurso="CAPITAL")

    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'periodos_uuid={periodo_2025_1.uuid}'
    )
    content = json.loads(response.content)

    assert len(content["results"]) == 5
    assert response.status_code == status.HTTP_200_OK

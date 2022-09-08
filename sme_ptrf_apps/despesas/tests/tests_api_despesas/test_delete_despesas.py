import pytest
from rest_framework import status

from ...models import Despesa, RateioDespesa


pytestmark = pytest.mark.django_db


def test_api_delete_despesas_sem_pc(
    jwt_authenticated_client_d,
    tapi_despesa,
    tapi_rateio_despesa_capital,
    tapi_periodo_2019_2,
):
    assert Despesa.objects.filter(uuid=tapi_despesa.uuid).exists()
    assert RateioDespesa.objects.filter(uuid=tapi_rateio_despesa_capital.uuid).exists()

    response = jwt_authenticated_client_d.delete(f'/api/despesas/{tapi_despesa.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Despesa.objects.filter(uuid=tapi_despesa.uuid).exists()
    assert not RateioDespesa.objects.filter(uuid=tapi_rateio_despesa_capital.uuid).exists()


def test_api_delete_despesas_com_pc(
    jwt_authenticated_client_d,
    tapi_despesa,
    tapi_periodo_2019_2,
    tapi_rateio_despesa_capital,
    tapi_prestacao_conta_da_despesa
):
    assert Despesa.objects.filter(uuid=tapi_despesa.uuid).exists()
    assert RateioDespesa.objects.filter(uuid=tapi_rateio_despesa_capital.uuid).exists()

    response = jwt_authenticated_client_d.delete(f'/api/despesas/{tapi_despesa.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    assert Despesa.objects.filter(uuid=tapi_despesa.uuid).exists()
    assert Despesa.by_uuid(tapi_despesa.uuid).status == 'INATIVO', "Despesa deveria estar inativa."

    assert RateioDespesa.objects.filter(uuid=tapi_rateio_despesa_capital.uuid).exists()
    assert RateioDespesa.by_uuid(tapi_rateio_despesa_capital.uuid).status == 'INATIVO', "Rateio deveria estar inativo."


def test_api_delete_despesas_com_imposto_sem_pc(
    jwt_authenticated_client_d,
    tapi_despesa_com_imposto,
    tapi_rateio_despesa_com_imposto,
    tapi_despesa_imposto,
    tapi_rateio_despesa_imposto,
    tapi_periodo_2019_2,
):
    assert Despesa.objects.filter(uuid=tapi_despesa_com_imposto.uuid).exists()
    assert RateioDespesa.objects.filter(uuid=tapi_rateio_despesa_com_imposto.uuid).exists()

    assert Despesa.objects.filter(uuid=tapi_despesa_imposto.uuid).exists()
    assert RateioDespesa.objects.filter(uuid=tapi_rateio_despesa_imposto.uuid).exists()

    response = jwt_authenticated_client_d.delete(f'/api/despesas/{tapi_despesa_com_imposto.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Despesa.objects.filter(uuid=tapi_despesa_imposto.uuid).exists()
    assert not RateioDespesa.objects.filter(uuid=tapi_rateio_despesa_imposto.uuid).exists()


def test_api_delete_despesas_com_imposto_com_pc(
    jwt_authenticated_client_d,
    tapi_despesa_com_imposto,
    tapi_rateio_despesa_com_imposto,
    tapi_despesa_imposto,
    tapi_rateio_despesa_imposto,
    tapi_periodo_2019_2,
    tapi_prestacao_conta_da_despesa,
):
    assert Despesa.objects.filter(uuid=tapi_despesa_com_imposto.uuid).exists()
    assert RateioDespesa.objects.filter(uuid=tapi_rateio_despesa_com_imposto.uuid).exists()

    assert Despesa.objects.filter(uuid=tapi_despesa_imposto.uuid).exists()
    assert RateioDespesa.objects.filter(uuid=tapi_rateio_despesa_imposto.uuid).exists()

    response = jwt_authenticated_client_d.delete(f'/api/despesas/{tapi_despesa_com_imposto.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    assert Despesa.objects.filter(uuid=tapi_despesa_com_imposto.uuid).exists()
    assert Despesa.by_uuid(tapi_despesa_com_imposto.uuid).status == 'INATIVO', "Despesa principal deveria estar inativa."

    assert RateioDespesa.objects.filter(uuid=tapi_rateio_despesa_com_imposto.uuid).exists()
    assert RateioDespesa.by_uuid(tapi_rateio_despesa_com_imposto.uuid).status == 'INATIVO', "Rateio da despesa principal deveria estar inativo."

    assert Despesa.objects.filter(uuid=tapi_despesa_imposto.uuid).exists()
    assert Despesa.by_uuid(tapi_despesa_imposto.uuid).status == 'INATIVO', "Despesa imposto deveria estar inativa."

    assert RateioDespesa.objects.filter(uuid=tapi_rateio_despesa_imposto.uuid).exists()
    assert RateioDespesa.by_uuid(tapi_rateio_despesa_imposto.uuid).status == 'INATIVO', "Rateio da despesa imposto deveria estar inativo."

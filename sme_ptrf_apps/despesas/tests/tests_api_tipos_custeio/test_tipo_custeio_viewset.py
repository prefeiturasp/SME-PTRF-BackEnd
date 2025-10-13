import pytest
import json
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_tipos_custeio_vincular_com_sucesso(jwt_authenticated_client_sme, tipo_custeio_factory, unidade_factory):
    tipo_custeio = tipo_custeio_factory()
    unidade = unidade_factory()

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/vincular-unidades/'

    payload = {
        "unidade_uuids": [
            f"{unidade.uuid}"
        ]
    }

    response = jwt_authenticated_client_sme.post(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK


def test_api_tipos_custeio_vincular_com_erro(jwt_authenticated_client_sme, tipo_custeio_factory, unidade_factory, despesa_factory, rateio_despesa_factory):
    tipo_custeio = tipo_custeio_factory()
    unidade = unidade_factory()
    despesa = despesa_factory.create()
    rateio_despesa_factory.create(
        despesa=despesa,
        tipo_custeio=tipo_custeio
    )

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/vincular-unidades/'

    payload = {
        "unidade_uuids": [
            f"{unidade.uuid}"
        ]
    }

    response = jwt_authenticated_client_sme.post(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'mensagem': 'Não é possível vincular o tipo de custeio, pois existem unidades com rateios já criados para este tipo que não foram selecionadas.'}


def test_api_tipos_custeio_desvincular_com_sucesso(jwt_authenticated_client_sme, tipo_custeio_factory, unidade_factory):
    tipo_custeio = tipo_custeio_factory()
    unidade = unidade_factory()

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/desvincular-unidades/'

    payload = {
        "unidade_uuids": [
            f"{unidade.uuid}"
        ]
    }

    response = jwt_authenticated_client_sme.post(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK


def test_api_tipos_custeio_desvincular_com_erro(jwt_authenticated_client_sme, tipo_custeio_factory, despesa_factory, rateio_despesa_factory):
    tipo_custeio = tipo_custeio_factory()
    despesa = despesa_factory()
    rateio = rateio_despesa_factory(
        despesa=despesa,
        tipo_custeio=tipo_custeio
    )

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/desvincular-unidades/'

    payload = {
        "unidade_uuids": [
            f"{rateio.despesa.associacao.unidade.uuid}"
        ]
    }

    response = jwt_authenticated_client_sme.post(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'mensagem': 'A operação de desvinculação não pode ser realizada. Algumas unidades possuem rateios cadastrados que exigem que permaneçam vinculadas a este tipo de custeio.'}

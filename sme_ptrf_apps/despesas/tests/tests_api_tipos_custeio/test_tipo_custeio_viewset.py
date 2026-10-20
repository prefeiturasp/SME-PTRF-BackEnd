import pytest
import json
from unittest.mock import patch
from rest_framework import status
from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_COMPLETO
from sme_ptrf_apps.despesas.services.tipo_custeio_vinculo_unidade_service import (
    TipoCusteioVinculoUnidadeService,
    UnidadeNaoEncontradaException,
)

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


def test_api_tipos_custeio_vincular_com_erro(jwt_authenticated_client_sme, tipo_custeio_factory):
    tipo_custeio = tipo_custeio_factory()

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/vincular-unidades/'

    payload = {
        "unidade_uuids": [
            "123"
        ]
    }

    response = jwt_authenticated_client_sme.post(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'mensagem': 'Erro ao vincular'}


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


def test_api_tipos_custeio_desvincular_com_erro(
        jwt_authenticated_client_sme, tipo_custeio_factory, despesa_factory, rateio_despesa_factory):
    tipo_custeio = tipo_custeio_factory()
    despesa = despesa_factory(status=STATUS_COMPLETO)

    rateio = rateio_despesa_factory(
        despesa=despesa,
        tipo_custeio=tipo_custeio,
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
        'mensagem': "Não é possível desvincular pois a(s) unidade(s) possuem lançamentos deste tipo."}


def test_api_tipos_custeio_vincular_sem_unidades_retorna_400(jwt_authenticated_client_sme, tipo_custeio_factory):
    tipo_custeio = tipo_custeio_factory()

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/vincular-unidades/'
    payload = {"unidade_uuids": []}

    response = jwt_authenticated_client_sme.post(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'mensagem': 'Nenhuma unidade foi identificada para desvínculo.'}


def test_api_tipos_custeio_vincular_unidade_nao_encontrada_retorna_404(
        jwt_authenticated_client_sme, tipo_custeio_factory, unidade_factory):
    tipo_custeio = tipo_custeio_factory()
    unidade = unidade_factory()

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/vincular-unidades/'
    payload = {"unidade_uuids": [f"{unidade.uuid}"]}

    with patch.object(
            TipoCusteioVinculoUnidadeService, 'vincular_unidades',
            side_effect=UnidadeNaoEncontradaException('Unidade não encontrada.')):
        response = jwt_authenticated_client_sme.post(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'mensagem': 'Unidade não encontrada.'}


def test_api_tipos_custeio_desvincular_sem_unidade_informada_retorna_400(
        jwt_authenticated_client_sme, tipo_custeio_factory):
    tipo_custeio = tipo_custeio_factory()

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/desvincular-unidades/'
    payload = {"unidade_uuids": []}

    response = jwt_authenticated_client_sme.post(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'erro': 'Nenhuma unidade informada.'}


def test_api_tipos_custeio_desvincular_unidade_nao_encontrada_retorna_404(
        jwt_authenticated_client_sme, tipo_custeio_factory, unidade_factory):
    tipo_custeio = tipo_custeio_factory()
    unidade = unidade_factory()

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/desvincular-unidades/'
    payload = {"unidade_uuids": [f"{unidade.uuid}"]}

    with patch.object(
            TipoCusteioVinculoUnidadeService, 'desvincular_unidades',
            side_effect=UnidadeNaoEncontradaException('Unidade não encontrada.')):
        response = jwt_authenticated_client_sme.post(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'mensagem': 'Unidade não encontrada.'}


def test_api_tipos_custeio_desvincular_com_uuid_invalido_retorna_erro_generico(
        jwt_authenticated_client_sme, tipo_custeio_factory):
    tipo_custeio = tipo_custeio_factory()

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/desvincular-unidades/'
    payload = {"unidade_uuids": ["123"]}

    response = jwt_authenticated_client_sme.post(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'mensagem': 'Erro ao desvincular'}


def test_api_tipos_custeio_destroy_protegido_por_despesas_vinculadas_retorna_400(
        jwt_authenticated_client_d, tipo_custeio_factory, rateio_despesa_factory):
    tipo_custeio = tipo_custeio_factory()
    rateio_despesa_factory(tipo_custeio=tipo_custeio)

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/'
    response = jwt_authenticated_client_d.delete(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'erro': 'ProtectedError',
        'mensagem': 'Esse tipo não pode ser excluído pois existem despesas cadastradas com esse tipo.'
    }


def test_api_tipos_custeio_vincular_todas_unidades_com_sucesso(
        jwt_authenticated_client_sme, tipo_custeio_factory, unidade_factory):
    tipo_custeio = tipo_custeio_factory()
    tipo_custeio.unidades.add(unidade_factory())

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/vincular-todas-unidades/'
    response = jwt_authenticated_client_sme.post(url, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['sucesso'] is True
    tipo_custeio.refresh_from_db()
    assert tipo_custeio.unidades.count() == 0


def test_api_tipos_custeio_vincular_todas_unidades_com_erro(jwt_authenticated_client_sme, tipo_custeio_factory):
    tipo_custeio = tipo_custeio_factory()
    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/vincular-todas-unidades/'

    with patch.object(TipoCusteioVinculoUnidadeService, 'vincular_todas_unidades', side_effect=Exception('boom')):
        response = jwt_authenticated_client_sme.post(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'mensagem': 'Erro ao vincular todas as unidades.'}


def test_api_tipos_custeio_desvincular_todas_unidades_com_sucesso(
        jwt_authenticated_client_sme, tipo_custeio_factory):
    tipo_custeio = tipo_custeio_factory()

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/desvincular-todas-unidades/'
    response = jwt_authenticated_client_sme.post(url, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['sucesso'] is True


def test_api_tipos_custeio_desvincular_todas_unidades_com_erro(jwt_authenticated_client_sme, tipo_custeio_factory):
    tipo_custeio = tipo_custeio_factory()
    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/desvincular-todas-unidades/'

    with patch.object(
            TipoCusteioVinculoUnidadeService, 'desvincular_todas_unidades', side_effect=Exception('boom')):
        response = jwt_authenticated_client_sme.post(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'mensagem': 'Erro ao desvincular todas as unidades.'}


def test_api_tipos_custeio_unidades_vinculadas_lista_as_unidades_do_tipo_custeio(
        jwt_authenticated_client_sme, tipo_custeio_factory, unidade_factory):
    tipo_custeio = tipo_custeio_factory()
    unidade_vinculada = unidade_factory()
    unidade_nao_vinculada = unidade_factory()
    tipo_custeio.unidades.add(unidade_vinculada)

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/unidades-vinculadas/'
    response = jwt_authenticated_client_sme.get(url, content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids_retornados = {item['uuid'] for item in result['results']}
    assert uuids_retornados == {str(unidade_vinculada.uuid)}
    assert str(unidade_nao_vinculada.uuid) not in uuids_retornados


def test_api_tipos_custeio_unidades_vinculadas_filtra_por_dre(
        jwt_authenticated_client_sme, tipo_custeio_factory, unidade_factory, dre_factory):
    dre_alvo = dre_factory()
    outra_dre = dre_factory()
    tipo_custeio = tipo_custeio_factory()
    unidade_da_dre_alvo = unidade_factory(dre=dre_alvo)
    unidade_de_outra_dre = unidade_factory(dre=outra_dre)
    tipo_custeio.unidades.add(unidade_da_dre_alvo, unidade_de_outra_dre)

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/unidades-vinculadas/?dre={dre_alvo.uuid}'
    response = jwt_authenticated_client_sme.get(url, content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert {item['uuid'] for item in result['results']} == {str(unidade_da_dre_alvo.uuid)}


def test_api_tipos_custeio_unidades_vinculadas_filtra_por_tipo_unidade(
        jwt_authenticated_client_sme, tipo_custeio_factory, unidade_factory):
    tipo_custeio = tipo_custeio_factory()
    unidade_emef = unidade_factory(tipo_unidade='EMEF')
    unidade_ceu = unidade_factory(tipo_unidade='CEU')
    tipo_custeio.unidades.add(unidade_emef, unidade_ceu)

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/unidades-vinculadas/?tipo_unidade=EMEF'
    response = jwt_authenticated_client_sme.get(url, content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert {item['uuid'] for item in result['results']} == {str(unidade_emef.uuid)}


def test_api_tipos_custeio_unidades_vinculadas_filtra_por_nome_ou_codigo(
        jwt_authenticated_client_sme, tipo_custeio_factory, unidade_factory):
    tipo_custeio = tipo_custeio_factory()
    unidade_buscada = unidade_factory(nome='Escola Municipal Buscada')
    outra_unidade = unidade_factory(nome='Outra Escola')
    tipo_custeio.unidades.add(unidade_buscada, outra_unidade)

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/unidades-vinculadas/?nome_ou_codigo=Buscada'
    response = jwt_authenticated_client_sme.get(url, content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert {item['uuid'] for item in result['results']} == {str(unidade_buscada.uuid)}


def test_api_tipos_custeio_unidades_nao_vinculadas_lista_as_unidades_nao_vinculadas(
        jwt_authenticated_client_sme, tipo_custeio_factory, unidade_factory):
    tipo_custeio = tipo_custeio_factory()
    unidade_vinculada = unidade_factory()
    unidade_nao_vinculada = unidade_factory()
    tipo_custeio.unidades.add(unidade_vinculada)

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/unidades-nao-vinculadas/'
    response = jwt_authenticated_client_sme.get(url, content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids_retornados = {item['uuid'] for item in result['results']}
    assert str(unidade_nao_vinculada.uuid) in uuids_retornados
    assert str(unidade_vinculada.uuid) not in uuids_retornados


def test_api_tipos_custeio_unidades_nao_vinculadas_filtra_por_dre(
        jwt_authenticated_client_sme, tipo_custeio_factory, unidade_factory, dre_factory):
    tipo_custeio = tipo_custeio_factory()
    dre_alvo = dre_factory()
    unidade_da_dre_alvo = unidade_factory(dre=dre_alvo)
    unidade_de_outra_dre = unidade_factory()

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/unidades-nao-vinculadas/?dre={dre_alvo.uuid}'
    response = jwt_authenticated_client_sme.get(url, content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids_retornados = {item['uuid'] for item in result['results']}
    assert str(unidade_da_dre_alvo.uuid) in uuids_retornados
    assert str(unidade_de_outra_dre.uuid) not in uuids_retornados


def test_api_tipos_custeio_unidades_nao_vinculadas_filtra_por_tipo_unidade(
        jwt_authenticated_client_sme, tipo_custeio_factory, unidade_factory):
    tipo_custeio = tipo_custeio_factory()
    unidade_emef = unidade_factory(tipo_unidade='EMEF')
    unidade_ceu = unidade_factory(tipo_unidade='CEU')

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/unidades-nao-vinculadas/?tipo_unidade=EMEF'
    response = jwt_authenticated_client_sme.get(url, content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids_retornados = {item['uuid'] for item in result['results']}
    assert str(unidade_emef.uuid) in uuids_retornados
    assert str(unidade_ceu.uuid) not in uuids_retornados


def test_api_tipos_custeio_unidades_nao_vinculadas_filtra_por_nome_ou_codigo(
        jwt_authenticated_client_sme, tipo_custeio_factory, unidade_factory):
    tipo_custeio = tipo_custeio_factory()
    unidade_buscada = unidade_factory(nome='Escola Municipal Buscada')
    outra_unidade = unidade_factory(nome='Outra Escola')

    url = f'/api/tipos-custeio/{tipo_custeio.uuid}/unidades-nao-vinculadas/?nome_ou_codigo=Buscada'
    response = jwt_authenticated_client_sme.get(url, content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    uuids_retornados = {item['uuid'] for item in result['results']}
    assert str(unidade_buscada.uuid) in uuids_retornados
    assert str(outra_unidade.uuid) not in uuids_retornados

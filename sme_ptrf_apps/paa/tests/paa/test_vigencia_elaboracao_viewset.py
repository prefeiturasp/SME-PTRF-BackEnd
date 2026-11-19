from datetime import date

import pytest
from freezegun import freeze_time
from rest_framework import status

pytestmark = pytest.mark.django_db

URL = '/api/paa/vigencia-elaboracao/'


@pytest.fixture
def periodos(periodo_paa_factory):
    vigente = periodo_paa_factory.create(
        referencia='2026', data_inicial=date(2026, 5, 1), data_final=date(2027, 4, 30))
    proxima = periodo_paa_factory.create(
        referencia='2027', data_inicial=date(2027, 8, 1), data_final=date(2027, 12, 31))
    return vigente, proxima


@freeze_time('2026-10-28')
def test_retorna_vigencia_paginada(
        jwt_authenticated_client_sme, flag_paa, flag_paa_proxima_vigencia, parametro_paa_factory,
        associacao, periodos):
    parametro_paa_factory.create(mes_elaboracao_paa=10)

    response = jwt_authenticated_client_sme.get(URL, {'associacao_uuid': associacao.uuid})

    assert response.status_code == status.HTTP_200_OK
    corpo = response.json()
    assert corpo['hoje'] == '2026-10-28'
    assert corpo['mes_elaboracao_paa'] == 10
    assert corpo['proxima_vigencia_habilitada'] is True
    assert corpo['periodos_sobrepostos'] is False
    assert (
        corpo['periodos']['count'],
        corpo['periodos']['page_size'],
        corpo['periodos']['total_pages']) == (2, 20, 1)
    assert [(p['referencia'], p['vigencia'], p['paa']) for p in corpo['periodos']['results']] == [
        ('2026', 'VIGENTE', None), ('2027', 'PROXIMA_VIGENCIA', None)]


@freeze_time('2026-10-28')
def test_flag_desligada_devolve_proxima_vigencia_desabilitada(
        jwt_authenticated_client_sme, flag_paa, parametro_paa_factory, associacao, periodos):
    parametro_paa_factory.create(mes_elaboracao_paa=10)

    corpo = jwt_authenticated_client_sme.get(URL, {'associacao_uuid': associacao.uuid}).json()

    assert corpo['proxima_vigencia_habilitada'] is False


@freeze_time('2026-10-28')
def test_pagina_os_periodos_em_20_itens(
        jwt_authenticated_client_sme, flag_paa, parametro_paa_factory, paa_factory, periodo_paa_factory,
        associacao):
    parametro_paa_factory.create(mes_elaboracao_paa=10)
    for ano in range(1990, 2015):
        periodo = periodo_paa_factory.create(
            referencia=str(ano), data_inicial=date(ano, 1, 1), data_final=date(ano, 12, 31))
        paa_factory.create(periodo_paa=periodo, associacao=associacao)

    pagina_1 = jwt_authenticated_client_sme.get(URL, {'associacao_uuid': associacao.uuid}).json()['periodos']
    pagina_2 = jwt_authenticated_client_sme.get(
        URL, {'associacao_uuid': associacao.uuid, 'page': 2}).json()['periodos']
    tamanho_maior = jwt_authenticated_client_sme.get(
        URL, {'associacao_uuid': associacao.uuid, 'page_size': 50}).json()['periodos']

    assert (pagina_1['count'], pagina_1['total_pages'], len(pagina_1['results'])) == (25, 2, 20)
    assert len(pagina_2['results']) == 5
    assert len(tamanho_maior['results']) == 20


def test_uuid_malformado_responde_400(jwt_authenticated_client_sme, flag_paa):
    response = jwt_authenticated_client_sme.get(URL, {'associacao_uuid': 'invalido'})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'associacao_uuid' in response.json()


def test_associacao_inexistente_e_de_outra_unidade_respondem_o_mesmo_404(
        jwt_authenticated_client_dre, flag_paa, associacao_factory, unidade_factory):
    de_outra_unidade = associacao_factory.create(unidade=unidade_factory.create(tipo_unidade='CEU'))

    inexistente = jwt_authenticated_client_dre.get(
        URL, {'associacao_uuid': '00000000-0000-0000-0000-000000000000'})
    inacessivel = jwt_authenticated_client_dre.get(URL, {'associacao_uuid': de_outra_unidade.uuid})

    assert inexistente.status_code == inacessivel.status_code == status.HTTP_404_NOT_FOUND
    assert inexistente.json() == inacessivel.json()


def test_sem_autenticacao_responde_401(client, flag_paa, associacao):
    response = client.get(URL, {'associacao_uuid': associacao.uuid})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_sem_permissao_de_ue_responde_403(jwt_authenticated_client, flag_paa, associacao):
    response = jwt_authenticated_client.get(URL, {'associacao_uuid': associacao.uuid})

    assert response.status_code == status.HTTP_403_FORBIDDEN

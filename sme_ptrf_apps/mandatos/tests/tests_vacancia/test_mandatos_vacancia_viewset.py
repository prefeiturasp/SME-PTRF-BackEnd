from datetime import date

import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from waffle.testutils import override_flag

from sme_ptrf_apps.mandatos.api.views import MandatosVacanciaViewSet
from sme_ptrf_apps.mandatos.models import Composicao
from sme_ptrf_apps.mandatos.fixtures.factories.mandato_factory import MandatoFactory

pytestmark = pytest.mark.django_db

FLAG = 'historico-de-membros-v2'


@pytest.fixture
def mandato_2026():
    return MandatoFactory(data_inicial=date(2026, 1, 1), data_final=date(2026, 12, 31))


@pytest.fixture
def associacao_teste(associacao_factory):
    return associacao_factory.create()


@override_flag(FLAG, active=True)
def test_mandato_vigente_retorna_mandato_sem_composicoes(mandato_2026, usuario_permissao_sme):
    """ A resposta da v2 não deve trazer o campo `composicoes` (conceito exclusivo da v1). """
    request = APIRequestFactory().get('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'get': 'mandato_vigente'})

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['uuid'] == str(mandato_2026.uuid)
    assert 'composicoes' not in response.data


@override_flag(FLAG, active=True)
def test_mandato_vigente_sem_mandato_retorna_uuid_none(usuario_permissao_sme):
    request = APIRequestFactory().get('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'get': 'mandato_vigente'})

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {'uuid': None}


@override_flag(FLAG, active=True)
def test_mandato_vigente_nao_cria_composicao_v1_como_efeito_colateral(
        mandato_2026, associacao_teste, usuario_permissao_sme):
    """ Regressão: a action da v1 cria uma Composicao (v1) implicitamente ao consultar o
    mandato vigente. A action da v2 não pode ter esse efeito colateral. """
    request = APIRequestFactory().get('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'get': 'mandato_vigente'})

    view(request)

    assert not Composicao.objects.filter(mandato=mandato_2026, associacao=associacao_teste).exists()


@override_flag(FLAG, active=False)
def test_mandato_vigente_bloqueado_com_flag_v2_desligada(mandato_2026, usuario_permissao_sme):
    """ Sem a flag historico-de-membros-v2 ativa, WaffleFlagMixin levanta Http404
    ('Inactive waffle') antes de chegar na action. """
    from django.http import Http404

    request = APIRequestFactory().get('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'get': 'mandato_vigente'})

    with pytest.raises(Http404):
        view(request)


@override_flag(FLAG, active=True)
def test_mandatos_anteriores_retorna_apenas_mandatos_com_data_final_anterior_ao_vigente(
        mandato_2026, usuario_permissao_sme):
    mandato_2024 = MandatoFactory(data_inicial=date(2024, 1, 1), data_final=date(2024, 12, 31))

    request = APIRequestFactory().get('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'get': 'mandatos_anteriores'})

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in response.data]
    assert uuids == [str(mandato_2024.uuid)]


@override_flag(FLAG, active=True)
def test_mandatos_anteriores_ordenado_do_mais_recente_para_o_mais_antigo(mandato_2026, usuario_permissao_sme):
    mandato_2023 = MandatoFactory(data_inicial=date(2023, 1, 1), data_final=date(2023, 12, 31))
    mandato_2024 = MandatoFactory(data_inicial=date(2024, 1, 1), data_final=date(2024, 12, 31))

    request = APIRequestFactory().get('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'get': 'mandatos_anteriores'})

    response = view(request)

    uuids = [item['uuid'] for item in response.data]
    assert uuids == [str(mandato_2024.uuid), str(mandato_2023.uuid)]


@override_flag(FLAG, active=True)
def test_mandatos_anteriores_nao_inclui_o_proprio_vigente(mandato_2026, usuario_permissao_sme):
    request = APIRequestFactory().get('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'get': 'mandatos_anteriores'})

    response = view(request)

    uuids = [item['uuid'] for item in response.data]
    assert str(mandato_2026.uuid) not in uuids


@override_flag(FLAG, active=True)
def test_mandatos_anteriores_sem_mandato_vigente_retorna_todos(usuario_permissao_sme):
    """ Mesmo comportamento da v1 (`MandatosViewSet.mandatos_anteriores`): sem mandato vigente,
    o filtro não é aplicado e todos os mandatos cadastrados voltam na resposta. """
    mandato_2024 = MandatoFactory(data_inicial=date(2024, 1, 1), data_final=date(2024, 12, 31))

    request = APIRequestFactory().get('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'get': 'mandatos_anteriores'})

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in response.data]
    assert uuids == [str(mandato_2024.uuid)]


@override_flag(FLAG, active=False)
def test_mandatos_anteriores_bloqueado_com_flag_v2_desligada(mandato_2026, usuario_permissao_sme):
    from django.http import Http404

    request = APIRequestFactory().get('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'get': 'mandatos_anteriores'})

    with pytest.raises(Http404):
        view(request)

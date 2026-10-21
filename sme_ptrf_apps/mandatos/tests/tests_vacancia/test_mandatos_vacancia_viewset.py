from datetime import date

import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from waffle.testutils import override_flag

from sme_ptrf_apps.mandatos.api.views import MandatosVacanciaViewSet
from sme_ptrf_apps.mandatos.models import Composicao, Mandato
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


# CRUD (list/create/retrieve/update/destroy) e mandato-mais-recente

@override_flag(FLAG, active=True)
def test_list_retorna_mandatos_cadastrados(mandato_2026, usuario_permissao_sme):
    request = APIRequestFactory().get('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'get': 'list'})

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    uuids = [item['uuid'] for item in response.data['results']]
    assert str(mandato_2026.uuid) in uuids


@override_flag(FLAG, active=True)
def test_list_filtra_por_referencia(mandato_2026, usuario_permissao_sme):
    outro = MandatoFactory(
        referencia_mandato='2027 a 2029', data_inicial=date(2027, 1, 1), data_final=date(2029, 12, 31)
    )

    request = APIRequestFactory().get('', {'referencia': outro.referencia_mandato})
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'get': 'list'})

    response = view(request)

    uuids = [item['uuid'] for item in response.data['results']]
    assert uuids == [str(outro.uuid)]


@override_flag(FLAG, active=True)
def test_retrieve_retorna_mandato(mandato_2026, usuario_permissao_sme):
    request = APIRequestFactory().get('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'get': 'retrieve'})

    response = view(request, uuid=mandato_2026.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['uuid'] == str(mandato_2026.uuid)


@override_flag(FLAG, active=True)
def test_create_cria_mandato(usuario_permissao_sme):
    payload = {
        'referencia_mandato': '2027 a 2029',
        'data_inicial': '2027-01-01',
        'data_final': '2029-12-31',
    }
    request = APIRequestFactory().post('', payload, format='json')
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'post': 'create'})

    response = view(request)

    assert response.status_code == status.HTTP_201_CREATED
    assert Mandato.objects.filter(referencia_mandato='2027 a 2029').exists()


@override_flag(FLAG, active=True)
def test_create_bloqueia_datas_sobrepostas_a_outro_mandato(mandato_2026, jwt_authenticated_client_sme):
    """ Usa o client de teste completo (não a chamada direta na view): uma exceção de validação
    levantada fora do ciclo normal de request do Django deixa a transação do teste quebrada,
    já que o projeto roda com `ATOMIC_REQUESTS=True` (mesmo padrão de `test_mandato_create.py`, v1). """
    import json

    payload = {
        'referencia_mandato': '2026 duplicado',
        'data_inicial': '2026-06-01',
        'data_final': '2026-12-31',
    }

    response = jwt_authenticated_client_sme.post(
        '/api/mandatos-vacancia/', data=json.dumps(payload), content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@override_flag(FLAG, active=True)
def test_update_edita_referencia_do_mandato(mandato_2026, usuario_permissao_sme):
    payload = {
        'referencia_mandato': 'referencia atualizada',
        'data_inicial': mandato_2026.data_inicial.isoformat(),
        'data_final': mandato_2026.data_final.isoformat(),
    }
    request = APIRequestFactory().patch('', payload, format='json')
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'patch': 'partial_update'})

    response = view(request, uuid=mandato_2026.uuid)

    assert response.status_code == status.HTTP_200_OK
    mandato_2026.refresh_from_db()
    assert mandato_2026.referencia_mandato == 'referencia atualizada'


@override_flag(FLAG, active=True)
def test_mandato_mais_recente_retorna_o_mandato_com_data_inicial_mais_recente(usuario_permissao_sme):
    MandatoFactory(data_inicial=date(2020, 1, 1), data_final=date(2022, 12, 31))
    mais_recente = MandatoFactory(data_inicial=date(2023, 1, 1), data_final=date(2025, 12, 31))

    request = APIRequestFactory().get('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'get': 'mandato_mais_recente'})

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['uuid'] == str(mais_recente.uuid)


@override_flag(FLAG, active=True)
def test_mandato_mais_recente_sem_mandato_retorna_lista_vazia(usuario_permissao_sme):
    request = APIRequestFactory().get('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'get': 'mandato_mais_recente'})

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@override_flag(FLAG, active=True)
def test_destroy_exclui_o_mandato_mais_recente_sem_cargos(mandato_2026, usuario_permissao_sme):
    request = APIRequestFactory().delete('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'delete': 'destroy'})

    response = view(request, uuid=mandato_2026.uuid)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Mandato.objects.filter(uuid=mandato_2026.uuid).exists()


@override_flag(FLAG, active=True)
def test_destroy_bloqueado_quando_nao_e_o_mandato_mais_recente(usuario_permissao_sme):
    mais_antigo = MandatoFactory(data_inicial=date(2020, 1, 1), data_final=date(2022, 12, 31))
    MandatoFactory(data_inicial=date(2023, 1, 1), data_final=date(2025, 12, 31))

    request = APIRequestFactory().delete('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'delete': 'destroy'})

    response = view(request, uuid=mais_antigo.uuid)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Mandato.objects.filter(uuid=mais_antigo.uuid).exists()


@override_flag(FLAG, active=True)
def test_destroy_bloqueado_quando_ha_cargo_ocupado_vinculado(mandato_2026, associacao_teste, usuario_permissao_sme):
    from sme_ptrf_apps.mandatos.fixtures.factories.ocupante_cargo_factory import OcupanteCargoFactory
    from sme_ptrf_apps.mandatos.models import CargoComposicaoVacancia, ComposicaoVacancia

    composicao = ComposicaoVacancia.objects.create(associacao=associacao_teste, mandato=mandato_2026)
    CargoComposicaoVacancia.objects.create(
        composicao=composicao,
        ocupante_do_cargo=OcupanteCargoFactory(nome='Ocupante Teste'),
        cargo_associacao='VOGAL_1',
        data_inicio_no_cargo=mandato_2026.data_inicial,
        data_fim_no_cargo=mandato_2026.data_final,
    )

    request = APIRequestFactory().delete('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'delete': 'destroy'})

    response = view(request, uuid=mandato_2026.uuid)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Mandato.objects.filter(uuid=mandato_2026.uuid).exists()


@override_flag(FLAG, active=True)
def test_destroy_permite_quando_ha_so_cargo_vago_vinculado(mandato_2026, associacao_teste, usuario_permissao_sme):
    """ Cargo vago (sem ocupante) não deve bloquear a exclusão do mandato. """
    from sme_ptrf_apps.mandatos.models import CargoComposicaoVacancia, ComposicaoVacancia

    composicao = ComposicaoVacancia.objects.create(associacao=associacao_teste, mandato=mandato_2026)
    CargoComposicaoVacancia.objects.create(
        composicao=composicao,
        ocupante_do_cargo=None,
        cargo_associacao='VOGAL_1',
        data_inicio_no_cargo=mandato_2026.data_inicial,
        data_fim_no_cargo=mandato_2026.data_final,
    )

    request = APIRequestFactory().delete('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = MandatosVacanciaViewSet.as_view({'delete': 'destroy'})

    response = view(request, uuid=mandato_2026.uuid)

    assert response.status_code == status.HTTP_204_NO_CONTENT

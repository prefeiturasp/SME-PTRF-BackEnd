from datetime import date
from uuid import uuid4

import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from waffle.testutils import override_flag

from sme_ptrf_apps.mandatos.api.views import CargosComposicoesVacanciaViewSet
from sme_ptrf_apps.mandatos.models import ComposicaoVacancia, CargoComposicaoVacancia
from sme_ptrf_apps.mandatos.choices import CargoComposicaoVacanciaChoices as Cargo
from sme_ptrf_apps.mandatos.services import ServicoHistoricoCargoComposicao
from sme_ptrf_apps.mandatos.fixtures.factories.mandato_factory import MandatoFactory
from sme_ptrf_apps.mandatos.fixtures.factories.ocupante_cargo_factory import OcupanteCargoFactory

pytestmark = pytest.mark.django_db

FLAG = 'historico-de-membros-v2'


@pytest.fixture
def mandato_2026():
    return MandatoFactory(data_inicial=date(2026, 1, 1), data_final=date(2026, 12, 31))


@pytest.fixture
def associacao_teste(associacao_factory):
    return associacao_factory.create()


@pytest.fixture
def composicao_vacancia(mandato_2026, associacao_teste):
    return ServicoHistoricoCargoComposicao.get_or_create_composicao_vacancia(
        associacao=associacao_teste, mandato=mandato_2026
    )


@pytest.fixture
def cargo_ocupado(composicao_vacancia):
    return ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia,
        ocupante_do_cargo=OcupanteCargoFactory(),
        cargo_associacao=Cargo.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )


def _payload_ocupante(**kwargs):
    payload = {
        'nome': 'Fulano de Tal',
        'codigo_identificacao': '654321',
        'cpf_responsavel': '99988877766',
        'representacao': 'SERVIDOR',
    }
    payload.update(kwargs)
    return payload


@override_flag(FLAG, active=True)
def test_retrieve_retorna_cargo_composicao_vacancia(cargo_ocupado, usuario_permissao_sme):
    """GET /{uuid}/ retorna o registro serializado."""
    request = APIRequestFactory().get('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'get': 'retrieve'})

    response = view(request, uuid=cargo_ocupado.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == cargo_ocupado.id


@override_flag(FLAG, active=True)
def test_list_retorna_registros_paginados(cargo_ocupado, usuario_permissao_sme):
    """GET / lista os registros existentes, paginado (CustomPagination)."""
    request = APIRequestFactory().get('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'get': 'list'})

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] >= 1


def test_retrieve_bloqueado_com_flag_v2_desligada(cargo_ocupado, usuario_permissao_sme):
    """Sem a flag historico-de-membros-v2 ativa, WaffleFlagMixin levanta Http404
    ('Inactive waffle') antes de chegar na action."""
    from django.http import Http404

    request = APIRequestFactory().get('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'get': 'retrieve'})

    with pytest.raises(Http404):
        view(request, uuid=cargo_ocupado.uuid)


@override_flag(FLAG, active=True)
def test_create_registra_entrada_via_service(composicao_vacancia, usuario_permissao_sme):
    """POST / cria o OcupanteCargo e o CargoComposicaoVacancia via registrar_entrada."""
    payload = {
        'composicao': str(composicao_vacancia.uuid),
        'cargo_associacao': Cargo.CARGO_ASSOCIACAO_TESOUREIRO,
        'data_inicio_no_cargo': '2026-01-01',
        'ocupante_do_cargo': _payload_ocupante(),
    }
    request = APIRequestFactory().post('', payload, format='json')
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'post': 'create'})

    response = view(request)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['ocupante_do_cargo']['nome'] == 'Fulano de Tal'


@override_flag(FLAG, active=True)
def test_composicao_vigente_cria_composicao_se_nao_existir(mandato_2026, associacao_teste, usuario_permissao_sme):
    """GET composicao-vigente faz get_or_create — primeira chamada cria a composição."""
    assert not ComposicaoVacancia.objects.filter(associacao=associacao_teste, mandato=mandato_2026).exists()

    request = APIRequestFactory().get('', {
        'associacao_uuid': str(associacao_teste.uuid),
        'mandato_uuid': str(mandato_2026.uuid),
    })
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'get': 'composicao_vigente'})

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['uuid']
    assert ComposicaoVacancia.objects.filter(associacao=associacao_teste, mandato=mandato_2026).exists()


@override_flag(FLAG, active=True)
def test_composicao_vigente_e_idempotente_em_chamadas_repetidas(composicao_vacancia, usuario_permissao_sme):
    """Chamar de novo não cria uma segunda ComposicaoVacancia pra mesma associacao+mandato."""
    request = APIRequestFactory().get('', {
        'associacao_uuid': str(composicao_vacancia.associacao.uuid),
        'mandato_uuid': str(composicao_vacancia.mandato.uuid),
    })
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'get': 'composicao_vigente'})

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['uuid'] == str(composicao_vacancia.uuid)


@override_flag(FLAG, active=True)
def test_registrar_saida_encerra_o_cargo(cargo_ocupado, usuario_permissao_sme):
    """POST {uuid}/registrar-saida/ aplica D-1 e retorna o registro atualizado."""
    request = APIRequestFactory().post('', {'data_saida': '2026-02-01'}, format='json')
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'post': 'registrar_saida'})

    response = view(request, uuid=cargo_ocupado.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['data_fim_no_cargo'] == '2026-01-31'

    cargo_ocupado.refresh_from_db()
    assert cargo_ocupado.data_fim_no_cargo == date(2026, 1, 31)


def test_registrar_saida_sem_data_no_body_retorna_400(cargo_ocupado, usuario_permissao_sme, flag_factory):
    """Sem data_saida no body, o RegistrarSaidaSerializer barra a requisição."""
    flag_factory.create(name=FLAG, everyone=True)

    request = APIRequestFactory().post('', {}, format='json')
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'post': 'registrar_saida'})

    response = view(request, uuid=cargo_ocupado.uuid)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@override_flag(FLAG, active=True)
def test_composicao_por_data_por_composicao_uuid(cargo_ocupado, composicao_vacancia, usuario_permissao_sme):
    """GET composicao-por-data com composicao_uuid retorna o snapshot da data."""
    request = APIRequestFactory().get('', {
        'composicao_uuid': str(composicao_vacancia.uuid),
        'data': '2026-06-15',
    })
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'get': 'composicao_por_data'})

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    ocupante_presidente = response.data[Cargo.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA]['ocupante_do_cargo']
    assert ocupante_presidente['id'] == cargo_ocupado.ocupante_do_cargo.id


@override_flag(FLAG, active=True)
def test_composicao_por_data_por_associacao_uuid_e_data(cargo_ocupado, composicao_vacancia, usuario_permissao_sme):
    """Mesma consulta funciona sem composicao_uuid, usando associacao_uuid + data (fallback)."""
    request = APIRequestFactory().get('', {
        'associacao_uuid': str(composicao_vacancia.associacao.uuid),
        'data': '2026-06-15',
    })
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'get': 'composicao_por_data'})

    response = view(request)

    assert response.status_code == status.HTTP_200_OK


@override_flag(FLAG, active=True)
def test_composicao_por_data_retorna_404_quando_nao_encontra(usuario_permissao_sme):
    """Nenhum critério bate com composição nenhuma ->404, não erro 500."""
    request = APIRequestFactory().get('', {'composicao_uuid': '00000000-0000-0000-0000-000000000000'})
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'get': 'composicao_por_data'})

    response = view(request)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@override_flag(FLAG, active=True)
def test_datas_de_alteracao_retorna_marcos_em_ordem(cargo_ocupado, composicao_vacancia, usuario_permissao_sme):
    """GET datas-de-alteracao retorna as datas de mudança da composição, ordenadas."""
    ServicoHistoricoCargoComposicao.registrar_saida(cargo_ocupado, data_saida=date(2026, 2, 1))

    request = APIRequestFactory().get('', {'composicao_uuid': str(composicao_vacancia.uuid)})
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'get': 'datas_de_alteracoes_na_composicao'})

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == ['2026-01-01', '2026-02-01']


def test_registrar_saida_em_registro_ja_encerrado_retorna_400_nao_500(
        cargo_ocupado, usuario_permissao_sme, flag_factory):
    """ o service levanta CargoComposicaoVacanciaValidationError sem o try/except na action isso vazaria como 500."""
    flag_factory.create(name=FLAG, everyone=True)

    request_1 = APIRequestFactory().post('', {'data_saida': '2026-02-01'}, format='json')
    force_authenticate(request_1, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'post': 'registrar_saida'})
    response_1 = view(request_1, uuid=cargo_ocupado.uuid)
    assert response_1.status_code == status.HTTP_200_OK

    # tentar de novo no mesmo registro (já encerrado) — ValidatorSaidaOcupanteVigente barra
    request_2 = APIRequestFactory().post('', {'data_saida': '2026-03-01'}, format='json')
    force_authenticate(request_2, user=usuario_permissao_sme)
    response_2 = view(request_2, uuid=cargo_ocupado.uuid)

    assert response_2.status_code == status.HTTP_400_BAD_REQUEST


@override_flag(FLAG, active=True)
def test_cancelar_saida_reverte_o_registro_para_vigente(cargo_ocupado, usuario_permissao_sme):
    """PATCH {uuid}/cancelar-saida/ volta o registro pra vigente e apaga a vacância aberta."""
    request_saida = APIRequestFactory().post('', {'data_saida': '2026-06-01'}, format='json')
    force_authenticate(request_saida, user=usuario_permissao_sme)
    view_saida = CargosComposicoesVacanciaViewSet.as_view({'post': 'registrar_saida'})
    view_saida(request_saida, uuid=cargo_ocupado.uuid)

    cargo_ocupado.refresh_from_db()
    assert cargo_ocupado.data_fim_no_cargo == date(2026, 5, 31)

    request_cancelar = APIRequestFactory().patch('')
    force_authenticate(request_cancelar, user=usuario_permissao_sme)
    view_cancelar = CargosComposicoesVacanciaViewSet.as_view({'patch': 'cancelar_saida'})

    response = view_cancelar(request_cancelar, uuid=cargo_ocupado.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['data_fim_no_cargo'] == '2026-12-31'

    cargo_ocupado.refresh_from_db()
    assert cargo_ocupado.data_fim_no_cargo == cargo_ocupado.composicao.mandato.data_final


def test_cancelar_saida_bloqueado_retorna_400(cargo_ocupado, usuario_permissao_sme, flag_factory):
    """Cancelar a saída de um registro ainda vigente (nunca saiu) deve dar 400,
    não 500 — mesma regra de tradução de exceção do registrar-saida. flag_factory
    pelo mesmo motivo do teste acima (evitar o .delete() do @override_flag numa
    conexão marcada pra rollback)."""
    flag_factory.create(name=FLAG, everyone=True)

    request = APIRequestFactory().patch('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'patch': 'cancelar_saida'})

    response = view(request, uuid=cargo_ocupado.uuid)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@override_flag(FLAG, active=True)
def test_cancelar_entrada_remove_o_registro_e_retorna_204(cargo_ocupado, usuario_permissao_sme):
    """PATCH {uuid}/cancelar-entrada/ apaga o registro vigente e não devolve corpo."""
    uuid_cargo = cargo_ocupado.uuid

    request = APIRequestFactory().patch('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'patch': 'cancelar_entrada'})

    response = view(request, uuid=uuid_cargo)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not CargoComposicaoVacancia.objects.filter(uuid=uuid_cargo).exists()


def test_cancelar_entrada_bloqueado_retorna_400(cargo_ocupado, usuario_permissao_sme, flag_factory):
    """Cancelar a entrada de um registro que já saiu deve dar 400, não 500 — mesma
    tradução de exceção das demais actions de saída/cancelamento. flag_factory pelo
    mesmo motivo documentado nos testes acima (evitar .delete() numa conexão em rollback)."""
    flag_factory.create(name=FLAG, everyone=True)

    request_saida = APIRequestFactory().post('', {'data_saida': '2026-06-01'}, format='json')
    force_authenticate(request_saida, user=usuario_permissao_sme)
    view_saida = CargosComposicoesVacanciaViewSet.as_view({'post': 'registrar_saida'})
    view_saida(request_saida, uuid=cargo_ocupado.uuid)

    request = APIRequestFactory().patch('')
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'patch': 'cancelar_entrada'})

    response = view(request, uuid=cargo_ocupado.uuid)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@override_flag(FLAG, active=True)
def test_corrigir_data_saida_atualiza_para_nova_data(cargo_ocupado, usuario_permissao_sme):
    """PATCH {uuid}/corrigir-saida/ reverte e registra de novo com a data corrigida."""
    request_saida = APIRequestFactory().post('', {'data_saida': '2026-06-01'}, format='json')
    force_authenticate(request_saida, user=usuario_permissao_sme)
    view_saida = CargosComposicoesVacanciaViewSet.as_view({'post': 'registrar_saida'})
    view_saida(request_saida, uuid=cargo_ocupado.uuid)

    request_corrigir = APIRequestFactory().patch('', {'data_saida': '2026-07-01'}, format='json')
    force_authenticate(request_corrigir, user=usuario_permissao_sme)
    view_corrigir = CargosComposicoesVacanciaViewSet.as_view({'patch': 'corrigir_data_saida'})

    response = view_corrigir(request_corrigir, uuid=cargo_ocupado.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['data_fim_no_cargo'] == '2026-06-30'  # D-1 da nova data

    cargo_ocupado.refresh_from_db()
    assert cargo_ocupado.data_fim_no_cargo == date(2026, 6, 30)


def test_corrigir_data_saida_bloqueado_se_nunca_saiu_retorna_400(cargo_ocupado, usuario_permissao_sme, flag_factory):
    """Não há saída pra corrigir num registro ainda vigente — mesma exceção de
    cancelar_saida propaga daqui. flag_factory por causa do try/except+ATOMIC_REQUESTS
    (mesmo motivo documentado nos testes de registrar-saida/cancelar-saida acima)."""
    flag_factory.create(name=FLAG, everyone=True)

    request = APIRequestFactory().patch('', {'data_saida': '2026-07-01'}, format='json')
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'patch': 'corrigir_data_saida'})

    response = view(request, uuid=cargo_ocupado.uuid)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@override_flag(FLAG, active=True)
def test_timeline_retorna_historico_ordenado_do_cargo(cargo_ocupado, composicao_vacancia, usuario_permissao_sme):
    """GET /timeline/ retorna todos os registros (ocupados e vagos) do cargo, em ordem."""
    ServicoHistoricoCargoComposicao.registrar_saida(cargo_ocupado, data_saida=date(2026, 6, 1))

    request = APIRequestFactory().get('', {
        'composicao_uuid': str(composicao_vacancia.uuid),
        'cargo_associacao_uuid': Cargo.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
    })
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'get': 'timeline'})

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2  # ocupante Pedro + vago
    assert response.data[0]['data_inicio_no_cargo'] == '2026-01-01'
    assert response.data[1]['vago'] is True


def test_timeline_composicao_uuid_inexistente_retorna_404(usuario_permissao_sme, flag_factory):
    """Http404 é tratado pelo próprio DRF — vira Response(404) normal, não propaga
    pra fora de view(). flag_factory pelo mesmo motivo de ATOMIC_REQUESTS de sempre."""
    flag_factory.create(name=FLAG, everyone=True)

    request = APIRequestFactory().get('', {
        'composicao_uuid': '00000000-0000-0000-0000-000000000000',
        'cargo_associacao': Cargo.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
    })
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'get': 'timeline'})

    response = view(request)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_timeline_composicao_uuid_mal_formado_retorna_404_nao_500(usuario_permissao_sme, flag_factory):
    """composicao_uuid que não é um UUID válido: ValidationError do ORM, convertida
    pelo helper em Http404 (404 normal) em vez de 500."""
    flag_factory.create(name=FLAG, everyone=True)

    request = APIRequestFactory().get('', {
        'composicao_uuid': 'isso-nao-e-um-uuid',
        'cargo_associacao': Cargo.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
    })
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'get': 'timeline'})

    response = view(request)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@override_flag(FLAG, active=True)
def test_cargos_da_composicao_retorna_formato_v1_diretoria_e_conselho(
        cargo_ocupado, composicao_vacancia, usuario_permissao_sme):
    """GET /cargos-da-composicao/?composicao_uuid=&data= retorna {diretoria_executiva,
    conselho_fiscal}, formato compatível com o que a v1 já produz."""
    request = APIRequestFactory().get('', {
        'composicao_uuid': str(composicao_vacancia.uuid),
        'data': '2026-06-01',
    })
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'get': 'cargos_da_composicao'})

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['diretoria_executiva']) == 9
    assert len(response.data['conselho_fiscal']) == 5
    presidente = response.data['diretoria_executiva'][0]
    assert presidente['ocupante_do_cargo']['nome'] == cargo_ocupado.ocupante_do_cargo.nome
    assert presidente['ocupante_editavel'] is False


def test_cargos_da_composicao_uuid_inexistente_retorna_404(usuario_permissao_sme, flag_factory):
    """composicao_uuid que não existe: 404, não 500 (usa o helper _get_composicao_vacancia_ou_404)."""
    flag_factory.create(name=FLAG, everyone=True)

    request = APIRequestFactory().get('', {
        'composicao_uuid': str(uuid4()),
    })
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'get': 'cargos_da_composicao'})

    response = view(request)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@override_flag(FLAG, active=True)
def test_editar_ocupante_atualiza_dados_via_patch(cargo_ocupado, usuario_permissao_sme):
    """PATCH {uuid}/ edita dados do ocupante do registro."""
    request = APIRequestFactory().patch('', {
        'ocupante_do_cargo': _payload_ocupante(nome='Nome Editado'),
    }, format='json')
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'patch': 'partial_update'})

    response = view(request, uuid=cargo_ocupado.uuid)

    assert response.status_code == status.HTTP_200_OK

    cargo_ocupado.ocupante_do_cargo.refresh_from_db()
    assert cargo_ocupado.ocupante_do_cargo.nome == 'Nome Editado'


def test_editar_ocupante_bloqueado_em_cargo_vago_retorna_400(composicao_vacancia, usuario_permissao_sme, flag_factory):
    """PATCH {uuid}/ num registro vago retorna 400, não 500."""
    flag_factory.create(name=FLAG, everyone=True)

    registro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia,
        ocupante_do_cargo=OcupanteCargoFactory(),
        cargo_associacao=Cargo.CARGO_ASSOCIACAO_TESOUREIRO,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro, data_saida=date(2026, 3, 1))
    vago = CargoComposicaoVacancia.objects.get(
        composicao=composicao_vacancia,
        cargo_associacao=Cargo.CARGO_ASSOCIACAO_TESOUREIRO,
        ocupante_do_cargo__isnull=True,
    )

    request = APIRequestFactory().patch('', {
        'ocupante_do_cargo': _payload_ocupante(),
    }, format='json')
    force_authenticate(request, user=usuario_permissao_sme)
    view = CargosComposicoesVacanciaViewSet.as_view({'patch': 'partial_update'})

    response = view(request, uuid=vago.uuid)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

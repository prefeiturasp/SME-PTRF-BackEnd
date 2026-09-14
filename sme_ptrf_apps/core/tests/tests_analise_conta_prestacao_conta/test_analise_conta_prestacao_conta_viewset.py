from unittest.mock import patch
from uuid import uuid4

import pytest

from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from ...api.views.analise_conta_prestacao_conta_viewset import AnaliseContaPrestacaoContaViewSet
from ...models import AnaliseContaPrestacaoConta

pytestmark = pytest.mark.django_db


def test_view_set(analise_conta_prestacao_conta_2020_1_solicitar_envio_do_comprovante_do_saldo_da_conta, usuario_permissao_associacao):
    request = APIRequestFactory().get("")
    detalhe = AnaliseContaPrestacaoContaViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=analise_conta_prestacao_conta_2020_1_solicitar_envio_do_comprovante_do_saldo_da_conta.uuid)

    assert response.status_code == status.HTTP_200_OK


# get_ajustes_saldo_conta
def _get_ajustes(usuario, **query_params):
    querystring = '&'.join(f'{chave}={valor}' for chave, valor in query_params.items())
    request = APIRequestFactory().get(f'/?{querystring}')
    force_authenticate(request, user=usuario)
    view = AnaliseContaPrestacaoContaViewSet.as_view({'get': 'get_ajustes_saldo_conta'})
    return view(request)


def test_get_ajustes_saldo_conta_sem_prestacao_conta(usuario_permissao_associacao):
    response = _get_ajustes(usuario_permissao_associacao)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'parametros_requeridos'


def test_get_ajustes_saldo_conta_prestacao_conta_nao_encontrada(usuario_permissao_associacao):
    response = _get_ajustes(usuario_permissao_associacao, prestacao_conta=uuid4())

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'Objeto não encontrado.'


def test_get_ajustes_saldo_conta_sem_conta_associacao(usuario_permissao_associacao, prestacao_conta):
    response = _get_ajustes(usuario_permissao_associacao, prestacao_conta=prestacao_conta.uuid)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'parametros_requeridos'


def test_get_ajustes_saldo_conta_conta_associacao_nao_encontrada(usuario_permissao_associacao, prestacao_conta):
    response = _get_ajustes(
        usuario_permissao_associacao, prestacao_conta=prestacao_conta.uuid, conta_associacao=uuid4())

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'Objeto não encontrado.'


def test_get_ajustes_saldo_conta_sucesso(
    usuario_permissao_associacao, analise_conta_prestacao_conta_factory, prestacao_conta_factory,
    conta_associacao_factory, analise_prestacao_conta_factory
):
    pc = prestacao_conta_factory()
    conta_associacao = conta_associacao_factory()
    analise_prestacao_conta = analise_prestacao_conta_factory(prestacao_conta=pc)
    analise_conta = analise_conta_prestacao_conta_factory(
        prestacao_conta=pc, conta_associacao=conta_associacao, analise_prestacao_conta=analise_prestacao_conta)

    response = _get_ajustes(
        usuario_permissao_associacao,
        prestacao_conta=pc.uuid,
        conta_associacao=conta_associacao.uuid,
        analise_prestacao_conta=analise_prestacao_conta.uuid,
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['uuid'] == str(analise_conta.uuid)


# salvar_ajustes_saldo_conta
def _salvar_ajustes(usuario, dados):
    request = APIRequestFactory().post('', data=dados, format='json')
    force_authenticate(request, user=usuario)
    view = AnaliseContaPrestacaoContaViewSet.as_view({'post': 'salvar_ajustes_saldo_conta'})
    return view(request)


def test_salvar_ajustes_saldo_conta_dados_vazios(usuario_permissao_associacao):
    response = _salvar_ajustes(usuario_permissao_associacao, {})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'Dados da Análise Vazio'


def test_salvar_ajustes_saldo_conta_analise_prestacao_conta_nao_encontrada(
    usuario_permissao_associacao, prestacao_conta_factory, conta_associacao_factory
):
    pc = prestacao_conta_factory()
    conta_associacao = conta_associacao_factory()

    dados = {
        'analise_prestacao_conta': str(uuid4()),
        'conta_associacao': str(conta_associacao.uuid),
        'prestacao_conta': str(pc.uuid),
        'data_extrato': '2025-09-26',
        'saldo_extrato': '442149.03',
    }
    response = _salvar_ajustes(usuario_permissao_associacao, dados)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'Objeto não encontrado.'


def test_salvar_ajustes_saldo_conta_prestacao_conta_nao_encontrada(
    usuario_permissao_associacao, analise_prestacao_conta_factory, conta_associacao_factory
):
    analise_prestacao_conta = analise_prestacao_conta_factory()
    conta_associacao = conta_associacao_factory()

    dados = {
        'analise_prestacao_conta': str(analise_prestacao_conta.uuid),
        'conta_associacao': str(conta_associacao.uuid),
        'prestacao_conta': str(uuid4()),
        'data_extrato': '2025-09-26',
        'saldo_extrato': '442149.03',
    }
    response = _salvar_ajustes(usuario_permissao_associacao, dados)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'Objeto não encontrado.'


def test_salvar_ajustes_saldo_conta_conta_associacao_nao_encontrada(
    usuario_permissao_associacao, analise_prestacao_conta_factory, prestacao_conta_factory
):
    pc = prestacao_conta_factory()
    analise_prestacao_conta = analise_prestacao_conta_factory(prestacao_conta=pc)

    dados = {
        'analise_prestacao_conta': str(analise_prestacao_conta.uuid),
        'conta_associacao': str(uuid4()),
        'prestacao_conta': str(pc.uuid),
        'data_extrato': '2025-09-26',
        'saldo_extrato': '442149.03',
    }
    response = _salvar_ajustes(usuario_permissao_associacao, dados)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'Objeto não encontrado.'


def test_salvar_ajustes_saldo_conta_erro_ao_salvar(
    usuario_permissao_associacao, analise_prestacao_conta_factory, prestacao_conta_factory, conta_associacao_factory
):
    pc = prestacao_conta_factory()
    conta_associacao = conta_associacao_factory()
    analise_prestacao_conta = analise_prestacao_conta_factory(prestacao_conta=pc)

    dados = {
        'analise_prestacao_conta': str(analise_prestacao_conta.uuid),
        'conta_associacao': str(conta_associacao.uuid),
        'prestacao_conta': str(pc.uuid),
        'data_extrato': '2025-09-26',
        'saldo_extrato': '442149.03',
    }

    with patch.object(AnaliseContaPrestacaoConta.objects, 'update_or_create', side_effect=Exception('falha no banco')):
        response = _salvar_ajustes(usuario_permissao_associacao, dados)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'Erro ao salvar Analise de Ajustes de saldo'
    assert 'falha no banco' in response.data['mensagem']


def test_salvar_ajustes_saldo_conta_sucesso(
    usuario_permissao_associacao, analise_prestacao_conta_factory, prestacao_conta_factory, conta_associacao_factory
):
    pc = prestacao_conta_factory()
    conta_associacao = conta_associacao_factory()
    analise_prestacao_conta = analise_prestacao_conta_factory(prestacao_conta=pc)

    dados = {
        'analise_prestacao_conta': str(analise_prestacao_conta.uuid),
        'conta_associacao': str(conta_associacao.uuid),
        'prestacao_conta': str(pc.uuid),
        'data_extrato': '2025-09-26',
        'saldo_extrato': '442149.03',
        'solicitar_envio_do_comprovante_do_saldo_da_conta': True,
        'solicitar_correcao_da_data_do_saldo_da_conta': True,
        'observacao_solicitar_envio_do_comprovante_do_saldo_da_conta': 'observação teste',
        'solicitar_correcao_de_justificativa_de_conciliacao': True,
    }

    response = _salvar_ajustes(usuario_permissao_associacao, dados)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['mensagem'] == 'Analise de ajustes de saldo por conta salva com sucesso'

    analise_conta = AnaliseContaPrestacaoConta.objects.get(
        analise_prestacao_conta=analise_prestacao_conta,
        conta_associacao=conta_associacao,
        prestacao_conta=pc,
    )
    assert str(analise_conta.saldo_extrato) == '442149.03'
    assert analise_conta.solicitar_envio_do_comprovante_do_saldo_da_conta is True
    assert analise_conta.observacao_solicitar_envio_do_comprovante_do_saldo_da_conta == 'observação teste'

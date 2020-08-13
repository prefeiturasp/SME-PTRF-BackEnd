import json

import pytest
from model_bakery import baker
from rest_framework import status

from ....dre.models import VerificacaoRegularidadeAssociacao

pytestmark = pytest.mark.django_db


@pytest.fixture
def grupo_verificacao_regularidade_documentos():
    return baker.make('dre.GrupoVerificacaoRegularidade', titulo='Documentos')


@pytest.fixture
def lista_verificacao_regularidade_documentos_associacao(grupo_verificacao_regularidade_documentos):
    return baker.make(
        'dre.ListaVerificacaoRegularidade',
        titulo='Documentos da Associação',
        grupo=grupo_verificacao_regularidade_documentos
    )


@pytest.fixture
def item_verificacao_regularidade_documentos_associacao_cnpj(lista_verificacao_regularidade_documentos_associacao):
    return baker.make(
        'dre.ItemVerificacaoRegularidade',
        descricao='CNPJ',
        lista=lista_verificacao_regularidade_documentos_associacao
    )


@pytest.fixture
def item_verificacao_regularidade_documentos_associacao_rais(lista_verificacao_regularidade_documentos_associacao):
    return baker.make(
        'dre.ItemVerificacaoRegularidade',
        descricao='RAIS',
        lista=lista_verificacao_regularidade_documentos_associacao
    )


@pytest.fixture
def verificacao_regularidade_associacao_documento_cnpj(grupo_verificacao_regularidade_documentos,
                                                       lista_verificacao_regularidade_documentos_associacao,
                                                       item_verificacao_regularidade_documentos_associacao_cnpj,
                                                       associacao):
    return baker.make(
        'dre.VerificacaoRegularidadeAssociacao',
        associacao=associacao,
        grupo_verificacao=grupo_verificacao_regularidade_documentos,
        lista_verificacao=lista_verificacao_regularidade_documentos_associacao,
        item_verificacao=item_verificacao_regularidade_documentos_associacao_cnpj,
        regular=True
    )


@pytest.fixture
def verificacao_regularidade_associacao_documento_rais(grupo_verificacao_regularidade_documentos,
                                                       lista_verificacao_regularidade_documentos_associacao,
                                                       item_verificacao_regularidade_documentos_associacao_rais,
                                                       associacao):
    return baker.make(
        'dre.VerificacaoRegularidadeAssociacao',
        associacao=associacao,
        grupo_verificacao=grupo_verificacao_regularidade_documentos,
        lista_verificacao=lista_verificacao_regularidade_documentos_associacao,
        item_verificacao=item_verificacao_regularidade_documentos_associacao_rais,
        regular=True
    )


def test_marca_item_verificacao_quando_sem_verificacao_ja_feita(client, associacao,
                                                                grupo_verificacao_regularidade_documentos,
                                                                lista_verificacao_regularidade_documentos_associacao,
                                                                item_verificacao_regularidade_documentos_associacao_cnpj,
                                                                ):
    response = client.get(
        f'/api/associacoes/{associacao.uuid}/marca-item-verificacao/?item={item_verificacao_regularidade_documentos_associacao_cnpj.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'item_verificacao': f'{item_verificacao_regularidade_documentos_associacao_cnpj.uuid}',
        'mensagem': 'Item de verificação marcado.'
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado

    verificacao = VerificacaoRegularidadeAssociacao.objects.get(associacao=associacao,
                                                                item_verificacao=item_verificacao_regularidade_documentos_associacao_cnpj)
    assert verificacao.regular


def test_marca_item_verificacao_quando_com_verificacao_ja_feita(client, associacao,
                                                                grupo_verificacao_regularidade_documentos,
                                                                lista_verificacao_regularidade_documentos_associacao,
                                                                item_verificacao_regularidade_documentos_associacao_cnpj,
                                                                verificacao_regularidade_associacao_documento_cnpj
                                                                ):
    response = client.get(
        f'/api/associacoes/{associacao.uuid}/marca-item-verificacao/?item={item_verificacao_regularidade_documentos_associacao_cnpj.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'item_verificacao': f'{item_verificacao_regularidade_documentos_associacao_cnpj.uuid}',
        'mensagem': 'Item de verificação marcado.'
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado

    verificacao = VerificacaoRegularidadeAssociacao.objects.get(associacao=associacao,
                                                                item_verificacao=item_verificacao_regularidade_documentos_associacao_cnpj)
    assert verificacao.regular, 'Deve continuar existindo a verificação.'

    verificacoes = VerificacaoRegularidadeAssociacao.objects.filter(associacao=associacao,
                                                                    item_verificacao=item_verificacao_regularidade_documentos_associacao_cnpj)
    assert verificacoes.count() == 1, 'Deve continuar havendo apenas uma verificação.'


def test_desmarca_item_verificacao_quando_com_verificacao_ja_feita(client, associacao,
                                                                   grupo_verificacao_regularidade_documentos,
                                                                   lista_verificacao_regularidade_documentos_associacao,
                                                                   item_verificacao_regularidade_documentos_associacao_cnpj,
                                                                   verificacao_regularidade_associacao_documento_cnpj
                                                                   ):
    response = client.get(
        f'/api/associacoes/{associacao.uuid}/desmarca-item-verificacao/?item={item_verificacao_regularidade_documentos_associacao_cnpj.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'item_verificacao': f'{item_verificacao_regularidade_documentos_associacao_cnpj.uuid}',
        'mensagem': 'Item de verificação desmarcado.'
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado

    verificacoes = VerificacaoRegularidadeAssociacao.objects.filter(associacao=associacao,
                                                                    item_verificacao=item_verificacao_regularidade_documentos_associacao_cnpj)
    assert verificacoes.count() == 0, 'A verificação deveria ter sido removida.'


def test_marca_lista_verificacao_quando_sem_verificacao_ja_feita(client, associacao,
                                                                 grupo_verificacao_regularidade_documentos,
                                                                 lista_verificacao_regularidade_documentos_associacao,
                                                                 item_verificacao_regularidade_documentos_associacao_cnpj,
                                                                 item_verificacao_regularidade_documentos_associacao_rais
                                                                 ):
    response = client.get(
        f'/api/associacoes/{associacao.uuid}/marca-lista-verificacao/?lista={lista_verificacao_regularidade_documentos_associacao.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'lista_verificacao': f'{lista_verificacao_regularidade_documentos_associacao.uuid}',
        'mensagem': 'Itens da lista de verificação marcados.'
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado

    verificacao = VerificacaoRegularidadeAssociacao.objects.filter(associacao=associacao,
                                                                   lista_verificacao=lista_verificacao_regularidade_documentos_associacao)
    assert verificacao.count() == 2, 'Deveriam haver dois itens de verificação criados.'


def test_desmarca_lista_verificacao(client, associacao,
                                    grupo_verificacao_regularidade_documentos,
                                    lista_verificacao_regularidade_documentos_associacao,
                                    item_verificacao_regularidade_documentos_associacao_cnpj,
                                    item_verificacao_regularidade_documentos_associacao_rais,
                                    verificacao_regularidade_associacao_documento_cnpj,
                                    verificacao_regularidade_associacao_documento_rais
                                    ):
    response = client.get(
        f'/api/associacoes/{associacao.uuid}/desmarca-lista-verificacao/?lista={lista_verificacao_regularidade_documentos_associacao.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'lista_verificacao': f'{lista_verificacao_regularidade_documentos_associacao.uuid}',
        'mensagem': 'Itens da lista de verificação desmarcados.'
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado

    verificacao = VerificacaoRegularidadeAssociacao.objects.filter(associacao=associacao,
                                                                   lista_verificacao=lista_verificacao_regularidade_documentos_associacao)
    assert verificacao.count() == 0, 'Não deveria haver nenhum itens de verificação.'


def test_atualiza_itens_verificacao(client, associacao,
                                    grupo_verificacao_regularidade_documentos,
                                    lista_verificacao_regularidade_documentos_associacao,
                                    item_verificacao_regularidade_documentos_associacao_cnpj,
                                    item_verificacao_regularidade_documentos_associacao_rais,
                                    verificacao_regularidade_associacao_documento_cnpj,
                                    verificacao_regularidade_associacao_documento_rais
                                    ):
    payload = [
        {
            "uuid": f'{item_verificacao_regularidade_documentos_associacao_cnpj.uuid}',
            "regular": False
        },
        {
            "uuid": f'{item_verificacao_regularidade_documentos_associacao_rais.uuid}',
            "regular": True
        }
    ]
    response = client.post(
        f'/api/associacoes/{associacao.uuid}/atualiza-itens-verificacao/', data=json.dumps(payload),
        content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'mensagem': 'Itens de verificação atualizados.'
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado

    verificacao1 = VerificacaoRegularidadeAssociacao.objects.filter(associacao=associacao,
                                                                   item_verificacao=item_verificacao_regularidade_documentos_associacao_cnpj)
    assert verificacao1.count() == 0, 'Esse item não deveria existir'

    verificacao2 = VerificacaoRegularidadeAssociacao.objects.filter(associacao=associacao,
                                                                   item_verificacao=item_verificacao_regularidade_documentos_associacao_rais)
    assert verificacao2.count() == 1, 'Esse item deveria existir'

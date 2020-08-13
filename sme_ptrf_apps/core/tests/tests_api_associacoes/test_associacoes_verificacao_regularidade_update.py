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

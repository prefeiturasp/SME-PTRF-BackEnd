import json

import pytest
from freezegun import freeze_time
from model_bakery import baker
from rest_framework import status
from sme_ptrf_apps.core.services import formata_data

pytestmark = pytest.mark.django_db


@pytest.fixture
def categoria():
    return baker.make('Categoria', nome='Prestações de conta')


@pytest.fixture
def categoria1():
    return baker.make('Categoria', nome='Categoria 1')


@pytest.fixture
def tipo_notificacao():
    return baker.make('TipoNotificacao', nome='Informação')


@pytest.fixture
def tipo_notificacao1():
    return baker.make('TipoNotificacao', nome='Alerta')


@pytest.fixture
def remetente():
    return baker.make('Remetente', nome='SME')


@pytest.fixture
def remetente1():
    return baker.make('Remetente', nome='AMCom')


@pytest.fixture
def notificacao(tipo_notificacao, remetente, categoria, usuario_permissao_associacao):
    return baker.make(
        'Notificacao',
        tipo=tipo_notificacao,
        categoria=categoria,
        remetente=remetente,
        titulo="Documentos Faltantes",
        descricao="Documentos Faltantes na prestação de contas",
        usuario=usuario_permissao_associacao
    )


@pytest.fixture
def notificacao2(tipo_notificacao1, remetente1, categoria1, usuario_permissao_associacao):
    return baker.make(
        'Notificacao',
        tipo=tipo_notificacao1,
        categoria=categoria1,
        remetente=remetente1,
        lido=True,
        titulo="Documentos Faltantes 2",
        descricao="Documentos Faltantes na prestação de contas 2",
        usuario=usuario_permissao_associacao
    )


def test_quantidade_de_nao_lidos(jwt_authenticated_client_a, notificacao):
    response = jwt_authenticated_client_a.get(
        f'/api/notificacoes/quantidade-nao-lidos/', content_type='application/json')
    result = json.loads(response.content)
    assert result['quantidade_nao_lidos'] == 1


def test_lista_notificacoes(jwt_authenticated_client_a, notificacao):
    response = jwt_authenticated_client_a.get(
        f'/api/notificacoes/', content_type='application/json')
    result = json.loads(response.content)
    esperado = {
            'count': 1,
            'links': {'next': None,
                      'previous': None},
            'page': 1,
            'page_size': 10,
            'results': [
                {
                    'data': formata_data(notificacao.criado_em.date()),
                    'infos': [
                        {
                            'uuid': str(notificacao.uuid),
                            'titulo': notificacao.titulo,
                            'descricao': notificacao.descricao,
                            'lido': notificacao.lido,
                            'hora': notificacao.hora.strftime("%H:%M"),
                            'tipo': notificacao.tipo.nome,
                            'remetente': notificacao.remetente.nome,
                            'categoria': notificacao.categoria.nome
                        }
                    ]
                }
            ]
        }

    assert result == esperado


def test_filtro_lido(jwt_authenticated_client_a, notificacao, notificacao2):
    response = jwt_authenticated_client_a.get(
        f'/api/notificacoes/?lido=True', content_type='application/json')
    result = json.loads(response.content)
    esperado = {
            'count': 1,
            'links': {'next': None,
                      'previous': None},
            'page': 1,
            'page_size': 10,
            'results': [
                {
                    'data': formata_data(notificacao2.criado_em.date()),
                    'infos': [
                        {
                            'uuid': str(notificacao2.uuid),
                            'titulo': notificacao2.titulo,
                            'descricao': notificacao2.descricao,
                            'lido': notificacao2.lido,
                            'hora': notificacao2.hora.strftime("%H:%M"),
                            'tipo': notificacao2.tipo.nome,
                            'remetente': notificacao2.remetente.nome,
                            'categoria': notificacao2.categoria.nome
                        }
                    ]
                }
            ]
    
    }

    assert result == esperado


def test_filtro_tipo(jwt_authenticated_client_a, notificacao, notificacao2):
    response = jwt_authenticated_client_a.get(
        f'/api/notificacoes/?tipo={notificacao2.tipo.id}', content_type='application/json')
    result = json.loads(response.content)
    esperado = {
            'count': 1,
            'links': {'next': None,
                      'previous': None},
            'page': 1,
            'page_size': 10,
            'results': [
                {
                    'data': formata_data(notificacao2.criado_em.date()),
                    'infos': [
                        {
                            'uuid': str(notificacao2.uuid),
                            'titulo': notificacao2.titulo,
                            'descricao': notificacao2.descricao,
                            'lido': notificacao2.lido,
                            'hora': notificacao2.hora.strftime("%H:%M"),
                            'tipo': notificacao2.tipo.nome,
                            'remetente': notificacao2.remetente.nome,
                            'categoria': notificacao2.categoria.nome
                        }
                    ]
                }
            ]
    }


    assert result == esperado

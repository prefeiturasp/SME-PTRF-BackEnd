import json

import pytest
from freezegun import freeze_time
from model_bakery import baker
from rest_framework import status
from sme_ptrf_apps.core.services import formata_data
from sme_ptrf_apps.core.choices import MembroEnum, RepresentacaoCargo
from sme_ptrf_apps.core.models import Notificacao

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


@pytest.fixture
def usuario_presidente(unidade):
    from django.contrib.auth import get_user_model
    senha = 'Sgp8888'
    login = '7218888'
    email = 'sme88@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.save()
    return user


@pytest.fixture
def usuario_vice_presidente(unidade):
    from django.contrib.auth import get_user_model
    senha = 'Sgp9999'
    login = '7219999'
    email = 'sme99@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.save()
    return user


@pytest.fixture
def membro_associacao_presidente_associacao(associacao, usuario_presidente):
    return baker.make(
        'MembroAssociacao',
        nome='Arthur Nobrega Silva',
        associacao=associacao,
        cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.value,
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.SERVIDOR.value,
        codigo_identificacao='567411',
        email='ollyverottoboni@gmail.com',
        usuario=usuario_presidente
    )


@pytest.fixture
def membro_associacao_vice_presidente_associacao(associacao, usuario_vice_presidente):
    return baker.make(
        'MembroAssociacao',
        nome='Arthur Nobrega Junior',
        associacao=associacao,
        cargo_associacao=MembroEnum.VICE_PRESIDENTE_DIRETORIA_EXECUTIVA.value,
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.SERVIDOR.value,
        codigo_identificacao='967499',
        email='ollyverottoboni@gmail.com',
        usuario=usuario_vice_presidente
    )


@pytest.fixture
def comentario_analise_prestacao(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'ComentarioAnalisePrestacao',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        ordem=1,
        comentario='Teste',
    )


@pytest.fixture
def categoria_prestacao_conta():
    return baker.make('Categoria', nome='Comentário na prestação de contas')


@pytest.fixture
def tipo_notificacao_aviso():
    return baker.make('TipoNotificacao', nome='Aviso')


@pytest.fixture
def remetente_dre():
    return baker.make('Remetente', nome='DRE')


def test_notificar(jwt_authenticated_client_a, 
    membro_associacao_presidente_associacao, 
    membro_associacao_vice_presidente_associacao, 
    associacao,
    periodo_2020_1,
    comentario_analise_prestacao,
    categoria_prestacao_conta,
    remetente_dre,
    tipo_notificacao_aviso):

    assert Notificacao.objects.count() == 0

    payload = {
        'associacao': str(associacao.uuid),
        'periodo': str(periodo_2020_1.uuid),
        'comentarios': [
            str(comentario_analise_prestacao.uuid),
        ]
    }

    response = jwt_authenticated_client_a.post(
        f'/api/notificacoes/notificar/', data=json.dumps(payload), content_type='application/json')

    result = json.loads(response.content)
    assert result == {"mensagem": "Processo de notificação enviado com sucesso."}
    assert Notificacao.objects.count() == 2
    assert Notificacao.objects.filter(usuario=membro_associacao_presidente_associacao.usuario).first()
    assert Notificacao.objects.filter(usuario=membro_associacao_vice_presidente_associacao.usuario).first()

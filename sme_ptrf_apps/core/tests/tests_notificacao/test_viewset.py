import datetime
import json
import uuid
from unittest.mock import patch

import pytest

from model_bakery import baker

from sme_ptrf_apps.core.services.notificacao_services import formata_data
from sme_ptrf_apps.core.choices import MembroEnum, RepresentacaoCargo
from sme_ptrf_apps.core.models import Notificacao, Recurso
from django.contrib.auth.models import Permission
from sme_ptrf_apps.users.models import Grupo

pytestmark = pytest.mark.django_db


@pytest.fixture
def notificacao(usuario_permissao_associacao):
    return baker.make(
        'Notificacao',
        tipo=Notificacao.TIPO_NOTIFICACAO_INFORMACAO,
        categoria=Notificacao.CATEGORIA_NOTIFICACAO_COMENTARIO_PC,
        remetente=Notificacao.REMETENTE_NOTIFICACAO_DRE,
        titulo="Documentos Faltantes",
        descricao="Documentos Faltantes na prestação de contas",
        usuario=usuario_permissao_associacao
    )


@pytest.fixture
def notificacao2(usuario_permissao_associacao):
    return baker.make(
        'Notificacao',
        tipo=Notificacao.TIPO_NOTIFICACAO_URGENTE,
        categoria=Notificacao.CATEGORIA_NOTIFICACAO_ELABORACAO_PC,
        remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
        lido=True,
        titulo="Documentos Faltantes 2",
        descricao="Documentos Faltantes na prestação de contas 2",
        usuario=usuario_permissao_associacao
    )


def test_quantidade_de_nao_lidos(jwt_authenticated_client_a, notificacao):
    response = jwt_authenticated_client_a.get(
        '/api/notificacoes/quantidade-nao-lidos/', content_type='application/json')
    result = json.loads(response.content)
    assert result['quantidade_nao_lidos'] == 1


def test_lista_notificacoes(jwt_authenticated_client_a, notificacao):
    response = jwt_authenticated_client_a.get(
        '/api/notificacoes/', content_type='application/json')
    result = json.loads(response.content)
    esperado = {
        'count': 1,
        'links': {'next': None, 'previous': None},
        'page': 1,
        'page_size': 10,
        'results': [
            {
                'data': formata_data(notificacao.criado_em.date()),
                'infos': [
                    {
                        'uuid': str(notificacao.uuid),
                        'unidade': None,
                        'titulo': notificacao.titulo,
                        'descricao': notificacao.descricao,
                        'lido': notificacao.lido,
                        'periodo': None,
                        'hora': notificacao.hora.strftime("%H:%M"),
                        'tipo': Notificacao.TIPO_NOTIFICACAO_NOMES[notificacao.tipo],
                        'remetente': Notificacao.REMETENTE_NOTIFICACAO_NOMES[notificacao.remetente],
                        'categoria': Notificacao.CATEGORIA_NOTIFICACAO_NOMES[notificacao.categoria],
                        'recurso': notificacao.recurso
                    }
                ]
            }
        ]
    }

    assert result == esperado


def test_filtro_lido(jwt_authenticated_client_a, notificacao, notificacao2):
    response = jwt_authenticated_client_a.get(
        '/api/notificacoes/?lido=True', content_type='application/json')
    result = json.loads(response.content)
    esperado = {
        'count': 1,
        'links': {'next': None, 'previous': None},
        'page': 1,
        'page_size': 10,
        'results': [
            {
                'data': formata_data(notificacao2.criado_em.date()),
                'infos': [
                    {
                        'uuid': str(notificacao2.uuid),
                        'unidade': None,
                        'titulo': notificacao2.titulo,
                        'descricao': notificacao2.descricao,
                        'lido': notificacao2.lido,
                        'periodo': None,
                        'hora': notificacao2.hora.strftime("%H:%M"),
                        'tipo': Notificacao.TIPO_NOTIFICACAO_NOMES[notificacao2.tipo],
                        'remetente': Notificacao.REMETENTE_NOTIFICACAO_NOMES[notificacao2.remetente],
                        'categoria': Notificacao.CATEGORIA_NOTIFICACAO_NOMES[notificacao2.categoria],
                        'recurso': notificacao2.recurso
                    }
                ]
            }
        ]
    }

    assert result == esperado


def test_filtro_tipo(jwt_authenticated_client_a, notificacao, notificacao2):
    response = jwt_authenticated_client_a.get(
        f'/api/notificacoes/?tipo={notificacao2.tipo}', content_type='application/json')
    result = json.loads(response.content)
    esperado = {
        'count': 1,
        'links': {'next': None, 'previous': None},
        'page': 1,
        'page_size': 10,
        'results': [
            {
                'data': formata_data(notificacao2.criado_em.date()),
                'infos': [
                    {
                        'uuid': str(notificacao2.uuid),
                        'unidade': None,
                        'titulo': notificacao2.titulo,
                        'descricao': notificacao2.descricao,
                        'lido': notificacao2.lido,
                        'periodo': None,
                        'hora': notificacao2.hora.strftime("%H:%M"),
                        'tipo': Notificacao.TIPO_NOTIFICACAO_NOMES[notificacao2.tipo],
                        'remetente': Notificacao.REMETENTE_NOTIFICACAO_NOMES[notificacao2.remetente],
                        'categoria': Notificacao.CATEGORIA_NOTIFICACAO_NOMES[notificacao2.categoria],
                        'recurso': notificacao2.recurso
                    }
                ]
            }
        ]
    }

    assert result == esperado


@pytest.fixture
def permissao_notificar():
    return Permission.objects.filter(codename='recebe_notificacao_comentario_em_pc').first()


@pytest.fixture
def grupo_com_permissao_notificar(permissao_notificar):
    g = Grupo.objects.create(name="grupo1")
    g.permissions.add(permissao_notificar)
    g.descricao = "Descrição grupo 1"
    g.save()
    return g


@pytest.fixture
def usuario_presidente(unidade, grupo_com_permissao_notificar):
    from django.contrib.auth import get_user_model
    senha = 'Sgp8888'
    login = '7218888'
    email = 'sme88@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_com_permissao_notificar)
    user.save()
    return user


@pytest.fixture
def usuario_vice_presidente(unidade, grupo_com_permissao_notificar):
    from django.contrib.auth import get_user_model
    senha = 'Sgp9999'
    login = '7219999'
    email = 'sme99@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_com_permissao_notificar)
    user.save()
    return user


@pytest.fixture
def usuario_apenas_com_permissao(grupo_com_permissao_notificar):
    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '6605656'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.groups.add(grupo_com_permissao_notificar)
    user.save()
    return user


@pytest.fixture
def membro_associacao_presidente_associacao(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Arthur Nobrega Silva',
        associacao=associacao,
        cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.name,
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.SERVIDOR.value,
        codigo_identificacao='7219999',
        email='ollyverottoboni@gmail.com',
    )


@pytest.fixture
def membro_associacao_vice_presidente_associacao(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Arthur Nobrega Junior',
        associacao=associacao,
        cargo_associacao=MembroEnum.VICE_PRESIDENTE_DIRETORIA_EXECUTIVA.name,
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.SERVIDOR.value,
        codigo_identificacao='7210418',
        email='ollyverottoboni@gmail.com',
    )


@pytest.fixture
def comentario_analise_prestacao(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'ComentarioAnalisePrestacao',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        ordem=1,
        comentario='Teste',
    )


def test_notificar(jwt_authenticated_client_a,
                   associacao,
                   periodo_2020_1,
                   comentario_analise_prestacao,
                   usuario_presidente,
                   usuario_vice_presidente,
                   usuario_apenas_com_permissao):
    assert Notificacao.objects.count() == 0

    payload = {
        'associacao': str(associacao.uuid),
        'periodo': str(periodo_2020_1.uuid),
        'comentarios': [
            str(comentario_analise_prestacao.uuid),
        ],
        'enviar_email': False
    }

    response = jwt_authenticated_client_a.post(
        '/api/notificacoes/notificar/', data=json.dumps(payload), content_type='application/json')

    result = json.loads(response.content)
    assert result == {"mensagem": "Processo de notificação enviado com sucesso."}
    assert Notificacao.objects.count() == 2
    assert Notificacao.objects.filter(
        usuario__username=usuario_presidente.username).first()
    assert Notificacao.objects.filter(
        usuario__username=usuario_vice_presidente.username).first()
    assert not Notificacao.objects.filter(
        usuario__username=usuario_apenas_com_permissao.username).first()


def test_notificar_dados_incompletos(jwt_authenticated_client_a):
    payload = {'associacao': '', 'periodo': '', 'comentarios': []}

    response = jwt_authenticated_client_a.post(
        '/api/notificacoes/notificar/', data=json.dumps(payload), content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == 400
    assert result['erro'] == 'Dados incompletos'


def test_notificar_exception(
    jwt_authenticated_client_a,
    associacao,
    periodo_2020_1,
    comentario_analise_prestacao,
):
    payload = {
        'associacao': str(associacao.uuid),
        'periodo': str(periodo_2020_1.uuid),
        'comentarios': [str(comentario_analise_prestacao.uuid)],
    }

    path = 'sme_ptrf_apps.core.api.views.notificacao_viewset.notificar_comentario_pc'
    with patch(path) as mock_notificar:
        mock_notificar.side_effect = Exception('erro inesperado')

        response = jwt_authenticated_client_a.post(
            '/api/notificacoes/notificar/', data=json.dumps(payload), content_type='application/json')
        result = json.loads(response.content)

    assert response.status_code == 400
    assert result['erro'] == 'Problema no processo de notificar usuário'


def test_filtro_remetente(jwt_authenticated_client_a, notificacao, notificacao2):
    response = jwt_authenticated_client_a.get(
        f'/api/notificacoes/?remetente={notificacao2.remetente}', content_type='application/json')
    result = json.loads(response.content)

    assert result['count'] == 1
    assert result['results'][0]['infos'][0]['uuid'] == str(notificacao2.uuid)


def test_filtro_categoria(jwt_authenticated_client_a, notificacao, notificacao2):
    response = jwt_authenticated_client_a.get(
        f'/api/notificacoes/?categoria={notificacao2.categoria}', content_type='application/json')
    result = json.loads(response.content)

    assert result['count'] == 1
    assert result['results'][0]['infos'][0]['uuid'] == str(notificacao2.uuid)


@pytest.fixture
def recurso_ptrf():
    return baker.make(
        'Recurso',
        nome_exibicao='PTRF',
        cor=Recurso.CorChoices.AZUL,
    )


def test_filtro_recurso(jwt_authenticated_client_a, usuario_permissao_associacao, notificacao, recurso_ptrf):
    notificacao.recurso = recurso_ptrf
    notificacao.save()

    response = jwt_authenticated_client_a.get(
        f'/api/notificacoes/?recurso={recurso_ptrf.uuid}', content_type='application/json')
    result = json.loads(response.content)

    assert result['count'] == 1
    assert result['results'][0]['infos'][0]['uuid'] == str(notificacao.uuid)


def test_filtro_data_inicio_fim(jwt_authenticated_client_a, notificacao, notificacao2):
    hoje = notificacao.criado_em.date()
    amanha = (hoje + datetime.timedelta(days=1)).isoformat()

    response = jwt_authenticated_client_a.get(
        f'/api/notificacoes/?data_inicio={hoje.isoformat()}&data_fim={amanha}', content_type='application/json')
    result = json.loads(response.content)

    assert result['count'] == 2


def test_lista_notificacoes_sem_paginacao(jwt_authenticated_client_a, notificacao):
    path = 'sme_ptrf_apps.core.api.views.notificacao_viewset.NotificacaoViewSet.paginate_queryset'
    with patch(path, return_value=None):
        response = jwt_authenticated_client_a.get('/api/notificacoes/', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == 200
    assert result == [
        {
            'data': formata_data(notificacao.criado_em.date()),
            'infos': [
                {
                    'uuid': str(notificacao.uuid),
                    'unidade': None,
                    'titulo': notificacao.titulo,
                    'descricao': notificacao.descricao,
                    'lido': notificacao.lido,
                    'periodo': None,
                    'hora': notificacao.hora.strftime("%H:%M"),
                    'tipo': Notificacao.TIPO_NOTIFICACAO_NOMES[notificacao.tipo],
                    'remetente': Notificacao.REMETENTE_NOTIFICACAO_NOMES[notificacao.remetente],
                    'categoria': Notificacao.CATEGORIA_NOTIFICACAO_NOMES[notificacao.categoria],
                    'recurso': notificacao.recurso
                }
            ]
        }
    ]


def test_erro_concluir_pc(jwt_authenticated_client_a, usuario_permissao_associacao):
    notificacao_erro = baker.make(
        'Notificacao',
        tipo=Notificacao.TIPO_NOTIFICACAO_URGENTE,
        categoria=Notificacao.CATEGORIA_NOTIFICACAO_ERRO_AO_CONCLUIR_PC,
        remetente=Notificacao.REMETENTE_NOTIFICACAO_SISTEMA,
        titulo="Erro ao concluir",
        descricao="Erro ao concluir a prestação de contas",
        usuario=usuario_permissao_associacao
    )

    response = jwt_authenticated_client_a.get(
        '/api/notificacoes/erro-concluir-pc/', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == 200
    assert len(result) == 1
    assert result[0]['uuid'] == str(notificacao_erro.uuid)


def test_tabelas(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(
        '/api/notificacoes/tabelas/', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == 200
    assert result == {
        'tipos_notificacao': Notificacao.tipos_to_json(),
        'remetentes': Notificacao.remetentes_to_json(),
        'categorias': Notificacao.categorias_to_json()
    }


def test_marcar_como_lido(jwt_authenticated_client_a, notificacao):
    assert notificacao.lido is False

    payload = {'uuid': str(notificacao.uuid), 'lido': True}

    response = jwt_authenticated_client_a.put(
        '/api/notificacoes/marcar-lido/', data=json.dumps(payload), content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == 200
    assert result == {'mensagem': 'Notificação atualizada com sucesso'}

    notificacao.refresh_from_db()
    assert notificacao.lido is True


def test_marcar_como_lido_notificacao_nao_encontrada(jwt_authenticated_client_a):
    payload = {'uuid': str(uuid.uuid4()), 'lido': True}

    response = jwt_authenticated_client_a.put(
        '/api/notificacoes/marcar-lido/', data=json.dumps(payload), content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == 200
    assert result == {'mensagem': 'Notificação atualizada com sucesso'}


def test_marcar_como_lido_dados_incompletos(jwt_authenticated_client_a):
    payload = {'uuid': '', 'lido': True}

    response = jwt_authenticated_client_a.put(
        '/api/notificacoes/marcar-lido/', data=json.dumps(payload), content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == 200
    assert result == {'mensagem': 'Notificação atualizada com sucesso'}


def test_notificar_comentarios_de_analise_consolidado_dre_dados_incompletos(jwt_authenticated_client_a):
    payload = {'dre': '', 'periodo': '', 'comentarios': []}

    response = jwt_authenticated_client_a.post(
        '/api/notificacoes/notificar-comentarios-de-analise-consolidado-dre/',
        data=json.dumps(payload), content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == 400
    assert result['erro'] == 'Dados incompletos'


def test_notificar_comentarios_de_analise_consolidado_dre_dre_nao_encontrada(
    jwt_authenticated_client_a, periodo_2020_1,
):
    payload = {
        'dre': str(uuid.uuid4()),
        'periodo': str(periodo_2020_1.uuid),
        'comentarios': [str(uuid.uuid4())],
    }

    response = jwt_authenticated_client_a.post(
        '/api/notificacoes/notificar-comentarios-de-analise-consolidado-dre/',
        data=json.dumps(payload), content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == 400
    assert result['erro'] == 'objeto_nao_encontrado'


def test_notificar_comentarios_de_analise_consolidado_dre_periodo_nao_encontrado(
    jwt_authenticated_client_a, dre,
):
    payload = {
        'dre': str(dre.uuid),
        'periodo': str(uuid.uuid4()),
        'comentarios': [str(uuid.uuid4())],
    }

    response = jwt_authenticated_client_a.post(
        '/api/notificacoes/notificar-comentarios-de-analise-consolidado-dre/',
        data=json.dumps(payload), content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == 400
    assert result['erro'] == 'objeto_nao_encontrado'


def test_notificar_comentarios_de_analise_consolidado_dre(
    jwt_authenticated_client_a, dre, periodo_2020_1,
):
    payload = {
        'dre': str(dre.uuid),
        'periodo': str(periodo_2020_1.uuid),
        'comentarios': [str(uuid.uuid4())],
    }

    path = (
        'sme_ptrf_apps.dre.services.notificacao_service'
        '.class_notificacao_comentario_de_analise_consolidado_dre'
        '.NotificacaoComentarioDeAnaliseConsolidadoDre'
    )
    with patch(path) as mock_notificacao_class:
        mock_notificacao_class.return_value.notificar.return_value = True

        response = jwt_authenticated_client_a.post(
            '/api/notificacoes/notificar-comentarios-de-analise-consolidado-dre/',
            data=json.dumps(payload), content_type='application/json')
        result = json.loads(response.content)

    assert response.status_code == 200
    assert result == {'mensagem': 'Processo de notificação finalizado.', 'enviada': True}


def test_notificar_comentarios_de_analise_consolidado_dre_exception(
    jwt_authenticated_client_a, dre, periodo_2020_1,
):
    payload = {
        'dre': str(dre.uuid),
        'periodo': str(periodo_2020_1.uuid),
        'comentarios': [str(uuid.uuid4())],
    }

    path = (
        'sme_ptrf_apps.dre.services.notificacao_service'
        '.class_notificacao_comentario_de_analise_consolidado_dre'
        '.NotificacaoComentarioDeAnaliseConsolidadoDre'
    )
    with patch(path) as mock_notificacao_class:
        mock_notificacao_class.return_value.notificar.side_effect = Exception('erro inesperado')

        response = jwt_authenticated_client_a.post(
            '/api/notificacoes/notificar-comentarios-de-analise-consolidado-dre/',
            data=json.dumps(payload), content_type='application/json')
        result = json.loads(response.content)

    assert response.status_code == 400
    assert result['erro'] == 'Problema no processo de notificar usuário'


@pytest.fixture
def prestacao_conta_reprovada_nao_apresentacao(associacao, periodo_2020_1):
    return baker.make(
        'PrestacaoContaReprovadaNaoApresentacao',
        associacao=associacao,
        periodo=periodo_2020_1,
    )


def test_notificar_prestacao_conta_reprovada_nao_apresentacao_dados_incompletos(jwt_authenticated_client_a):
    payload = {'prestacao_conta_reprovada_nao_apresentacao': ''}

    response = jwt_authenticated_client_a.post(
        '/api/notificacoes/notificar-prestacao-conta-reprovada-nao-apresentacao/',
        data=json.dumps(payload), content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == 400
    assert result['erro'] == 'Dados incompletos'


def test_notificar_prestacao_conta_reprovada_nao_apresentacao_nao_encontrada(jwt_authenticated_client_a):
    payload = {'prestacao_conta_reprovada_nao_apresentacao': str(uuid.uuid4())}

    response = jwt_authenticated_client_a.post(
        '/api/notificacoes/notificar-prestacao-conta-reprovada-nao-apresentacao/',
        data=json.dumps(payload), content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == 400
    assert result['erro'] == 'objeto_nao_encontrado'


def test_notificar_prestacao_conta_reprovada_nao_apresentacao(
    jwt_authenticated_client_a, prestacao_conta_reprovada_nao_apresentacao,
):
    payload = {
        'prestacao_conta_reprovada_nao_apresentacao': str(prestacao_conta_reprovada_nao_apresentacao.uuid),
    }

    path = (
        'sme_ptrf_apps.core.services.notificacao_services'
        '.notificacao_prestacao_de_contas_reprovada_nao_apresentacao'
        '.notificar_prestacao_de_contas_reprovada_nao_apresentacao'
    )
    with patch(path) as mock_notificar:
        mock_notificar.return_value = None

        response = jwt_authenticated_client_a.post(
            '/api/notificacoes/notificar-prestacao-conta-reprovada-nao-apresentacao/',
            data=json.dumps(payload), content_type='application/json')
        result = json.loads(response.content)

    assert response.status_code == 200
    assert result == {'mensagem': 'Processo de notificação enviado com sucesso.'}
    mock_notificar.assert_called_once_with(prestacao_conta_reprovada_nao_apresentacao)


def test_notificar_prestacao_conta_reprovada_nao_apresentacao_exception(
    jwt_authenticated_client_a, prestacao_conta_reprovada_nao_apresentacao,
):
    payload = {
        'prestacao_conta_reprovada_nao_apresentacao': str(prestacao_conta_reprovada_nao_apresentacao.uuid),
    }

    path = (
        'sme_ptrf_apps.core.services.notificacao_services'
        '.notificacao_prestacao_de_contas_reprovada_nao_apresentacao'
        '.notificar_prestacao_de_contas_reprovada_nao_apresentacao'
    )
    with patch(path) as mock_notificar:
        mock_notificar.side_effect = Exception('erro inesperado')

        response = jwt_authenticated_client_a.post(
            '/api/notificacoes/notificar-prestacao-conta-reprovada-nao-apresentacao/',
            data=json.dumps(payload), content_type='application/json')
        result = json.loads(response.content)

    assert response.status_code == 400
    assert result['erro'] == 'Problema no processo de notificar usuário'

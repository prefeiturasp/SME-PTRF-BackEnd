import json

import pytest
from django.contrib.auth.models import Permission
from model_bakery import baker
from sme_ptrf_apps.users.models import Grupo
from django.contrib.contenttypes.models import ContentType
from rest_framework.status import (
    HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
)

pytestmark = pytest.mark.django_db


def test_repasses_pendentes(
        jwt_authenticated_client_p,
        periodo,
        repasse,
        acao,
        acao_associacao,
        associacao,
        tipo_conta,
        conta_associacao):

    response = jwt_authenticated_client_p.get(
        f'/api/repasses/pendentes/?associacao={associacao.uuid}', content_type='application/json')
    result = json.loads(response.content)

    uuids_esperado = [f'{repasse.uuid}']

    result_uuids = []
    for item in result:
        result_uuids.append(item['uuid'])

    assert result_uuids == uuids_esperado


def test_repasses_pendentes_livre_aplicacao(
        jwt_authenticated_client_p,
        periodo_2020_1,
        repasse_2020_1_livre_aplicacao_pendente,
        acao,
        acao_associacao,
        associacao,
        tipo_conta,
        conta_associacao):

    response = jwt_authenticated_client_p.get(
        f'/api/repasses/pendentes/?associacao={associacao.uuid}', content_type='application/json')
    result = json.loads(response.content)

    uuids_esperado = [f'{repasse_2020_1_livre_aplicacao_pendente.uuid}']

    result_uuids = []
    for item in result:
        result_uuids.append(item['uuid'])

    assert result_uuids == uuids_esperado


@pytest.fixture
def grupo_sem_permissao_criar_receita():
    content_type = ContentType.objects.filter(model='receita').first()
    g = Grupo.objects.create(name="receita")
    g.permissions.add(
        Permission.objects.create(codename='algo_receita', name='Can Algo', content_type=content_type)
    )
    return g


@pytest.fixture
def usuario_sem_permissao(unidade, grupo_sem_permissao_criar_receita):
    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_sem_permissao_criar_receita)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_sem_permissao(client, usuario_sem_permissao):
    from unittest.mock import patch

    from rest_framework.test import APIClient
    api_client = APIClient()
    with patch('sme_ptrf_apps.users.api.views.login.AutenticacaoService.autentica') as mock_post:
        data = {
            "nome": "LUCIA HELENA",
            "cpf": "62085077072",
            "email": "luh@gmail.com",
            "login": "7210418"
        }
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = data
        resp = api_client.post('/api/login', {'login': usuario_sem_permissao.username,
                                              'senha': usuario_sem_permissao.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client


def test_repasses_pendentes_sem_permissao(
        jwt_authenticated_client_sem_permissao,
        periodo,
        repasse,
        acao,
        acao_associacao,
        associacao,
        tipo_conta,
        conta_associacao):

    response = jwt_authenticated_client_sem_permissao.get(
        f'/api/repasses/pendentes/?acao-associacao={acao_associacao.uuid}&data=02/09/2019',
        content_type='application/json')

    assert response.status_code == HTTP_403_FORBIDDEN


def test_tabelas_retorna_periodos_ordenados(jwt_authenticated_client_p, periodo_factory):
    periodo_factory(referencia="2024.6")
    periodo_factory(referencia="2023.2")
    periodo_factory(referencia="2025.1")

    response = jwt_authenticated_client_p.get('/api/repasses/tabelas/', content_type='application/json')

    assert response.status_code == HTTP_200_OK

    result = json.loads(response.content)

    periodos_retorno = [p['referencia'] for p in result['periodos']]

    assert periodos_retorno == ["2025.1", "2024.6", "2023.2"]


def test_list_repasses_retorna_200(jwt_authenticated_client_p, repasse):
    response = jwt_authenticated_client_p.get('/api/repasses/', content_type='application/json')
    assert response.status_code == HTTP_200_OK


def test_list_repasses_filtro_search_por_eol(jwt_authenticated_client_p, repasse, associacao):
    eol = associacao.unidade.codigo_eol
    response = jwt_authenticated_client_p.get(
        f'/api/repasses/?search={eol}', content_type='application/json'
    )
    assert response.status_code == HTTP_200_OK
    result = json.loads(response.content)
    uuids = [item['uuid'] for item in result['results']]
    assert str(repasse.uuid) in uuids


def test_list_repasses_filtro_periodo(jwt_authenticated_client_p, repasse, periodo):
    response = jwt_authenticated_client_p.get(
        f'/api/repasses/?periodo={periodo.uuid}', content_type='application/json'
    )
    assert response.status_code == HTTP_200_OK
    result = json.loads(response.content)
    uuids = [item['uuid'] for item in result['results']]
    assert str(repasse.uuid) in uuids


def test_list_repasses_filtro_conta(jwt_authenticated_client_p, repasse, conta_associacao, tipo_conta):
    response = jwt_authenticated_client_p.get(
        f'/api/repasses/?conta={tipo_conta.uuid}', content_type='application/json'
    )
    assert response.status_code == HTTP_200_OK
    result = json.loads(response.content)
    uuids = [item['uuid'] for item in result['results']]
    assert str(repasse.uuid) in uuids


def test_list_repasses_filtro_acao(jwt_authenticated_client_p, repasse, acao_associacao, acao):
    response = jwt_authenticated_client_p.get(
        f'/api/repasses/?acao={acao.uuid}', content_type='application/json'
    )
    assert response.status_code == HTTP_200_OK
    result = json.loads(response.content)
    uuids = [item['uuid'] for item in result['results']]
    assert str(repasse.uuid) in uuids


def test_list_repasses_filtro_status_pendente(jwt_authenticated_client_p, repasse):
    response = jwt_authenticated_client_p.get(
        '/api/repasses/?status=PENDENTE', content_type='application/json'
    )
    assert response.status_code == HTTP_200_OK
    result = json.loads(response.content)
    uuids = [item['uuid'] for item in result['results']]
    assert str(repasse.uuid) in uuids


def test_list_repasses_filtro_status_exclui_pendentes(jwt_authenticated_client_p, repasse, repasse_realizado):
    response = jwt_authenticated_client_p.get(
        '/api/repasses/?status=REALIZADO', content_type='application/json'
    )
    assert response.status_code == HTTP_200_OK
    result = json.loads(response.content)
    uuids = [item['uuid'] for item in result['results']]
    assert str(repasse.uuid) not in uuids
    assert str(repasse_realizado.uuid) in uuids


def test_destroy_repasse_realizado_retorna_400(jwt_authenticated_client_p, repasse_realizado):
    response = jwt_authenticated_client_p.delete(
        f'/api/repasses/{repasse_realizado.uuid}/', content_type='application/json'
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    result = json.loads(response.content)
    assert result['erro'] == 'StatusNaoPermitido'


def test_destroy_repasse_com_receita_vinculada_retorna_400(jwt_authenticated_client_p, repasse):
    tipo = baker.make('TipoReceita')
    baker.make('Receita', repasse=repasse, tipo_receita=tipo)
    response = jwt_authenticated_client_p.delete(
        f'/api/repasses/{repasse.uuid}/', content_type='application/json'
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    result = json.loads(response.content)
    assert result['erro'] == 'ReceitaVinculada'


def test_destroy_repasse_pendente_sem_receita_retorna_204(jwt_authenticated_client_p, repasse):
    response = jwt_authenticated_client_p.delete(
        f'/api/repasses/{repasse.uuid}/', content_type='application/json'
    )
    assert response.status_code == HTTP_204_NO_CONTENT


def test_pendentes_sem_uuid_associacao_retorna_400(jwt_authenticated_client_p):
    response = jwt_authenticated_client_p.get(
        '/api/repasses/pendentes/', content_type='application/json'
    )
    assert response.status_code == HTTP_400_BAD_REQUEST


def test_tabelas_retorna_estrutura_completa(jwt_authenticated_client_p):
    response = jwt_authenticated_client_p.get('/api/repasses/tabelas/', content_type='application/json')
    assert response.status_code == HTTP_200_OK
    result = json.loads(response.content)
    assert 'periodos' in result
    assert 'tipos_contas' in result
    assert 'acoes' in result
    assert 'status' in result


def test_tabelas_por_associacao_sem_uuid_retorna_400(jwt_authenticated_client_p):
    response = jwt_authenticated_client_p.get(
        '/api/repasses/tabelas-por-associacao/', content_type='application/json'
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    result = json.loads(response.content)
    assert result['erro'] == 'parametros_requerido'


def test_tabelas_por_associacao_com_uuid_retorna_200(jwt_authenticated_client_p, associacao):
    response = jwt_authenticated_client_p.get(
        f'/api/repasses/tabelas-por-associacao/?associacao_uuid={associacao.uuid}',
        content_type='application/json'
    )
    assert response.status_code == HTTP_200_OK
    result = json.loads(response.content)
    assert 'acoes_associacao' in result
    assert 'contas_associacao' in result

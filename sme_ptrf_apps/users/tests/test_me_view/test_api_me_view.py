import pytest

from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APIClient
from waffle.testutils import override_flag

pytestmark = pytest.mark.django_db

ME_URL = '/api/me'


def mock_login_usuario_service(unidades):
    """Substitui GestaoUsuarioService/LoginUsuarioService por dublês, evitando
    reconstruir toda a infraestrutura de acesso (já coberta em test_user_v2)
    e mantendo o teste focado no comportamento da própria MeView."""
    gestao_patch = patch('sme_ptrf_apps.users.api.views.login.GestaoUsuarioService')
    login_service_patch = patch('sme_ptrf_apps.users.api.views.login.LoginUsuarioService')
    mock_gestao = gestao_patch.start()  # noqa
    mock_login_service_cls = login_service_patch.start()
    mock_login_service_cls.return_value.unidades_que_usuario_tem_acesso = unidades
    mock_login_service_cls.return_value.unidades_que_perdeu_acesso = []
    mock_login_service_cls.return_value.mensagem_perca_acesso = None
    return gestao_patch, login_service_patch


def test_me_view_sem_autenticacao_retorna_401():
    api_client = APIClient()

    response = api_client.get(ME_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_me_view_retorna_dados_do_usuario_autenticado(me_client, me_user, unidades_com_acesso):
    gestao_patch, login_service_patch = mock_login_usuario_service(unidades_com_acesso)
    try:
        response = me_client.get(ME_URL)
    finally:
        gestao_patch.stop()
        login_service_patch.stop()

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['login'] == me_user.username
    assert data['nome'] == me_user.name
    assert data['email'] == me_user.email
    assert data['visoes'] == ['UE']
    assert data['unidades'] == unidades_com_acesso
    assert data['permissoes'] == ['view_tipodevolucaoaotesouro']
    assert 'feature_flags' in data
    assert 'associacao' in data


def test_me_view_sem_acesso_a_nenhuma_unidade_retorna_403(me_client):
    gestao_patch, login_service_patch = mock_login_usuario_service([])
    try:
        response = me_client.get(ME_URL)
    finally:
        gestao_patch.stop()
        login_service_patch.stop()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert 'detail' in response.json()


def test_me_view_erro_interno_retorna_500(me_client):
    with patch(
        'sme_ptrf_apps.users.api.views.login.GestaoUsuarioService',
        side_effect=Exception('Falha ao consultar usuário'),
    ):
        response = me_client.get(ME_URL)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'Falha ao consultar usuário' in response.json()['detail']


def test_me_view_monta_associacao_quando_existe_para_a_unidade(me_client, unidade, associacao_unidade_a):
    unidades = [{
        'uuid': str(unidade.uuid),
        'nome': unidade.nome,
        'tipo_unidade': unidade.tipo_unidade,
        'associacao': {'uuid': '', 'nome': ''},
        'acesso_de_suporte': False,
        'notificar_devolucao_por_recurso': {},
    }]

    gestao_patch, login_service_patch = mock_login_usuario_service(unidades)
    try:
        response = me_client.get(ME_URL)
    finally:
        gestao_patch.stop()
        login_service_patch.stop()

    assert response.status_code == status.HTTP_200_OK
    associacao_dict = response.json()['associacao']
    assert associacao_dict == {
        'uuid': str(associacao_unidade_a.uuid),
        'nome': associacao_unidade_a.nome,
        'nome_escola': unidade.nome,
        'tipo_escola': unidade.tipo_unidade,
    }


def test_me_view_associacao_vazia_quando_nao_ha_associacao_para_a_unidade(me_client, unidades_com_acesso):
    gestao_patch, login_service_patch = mock_login_usuario_service(unidades_com_acesso)
    try:
        response = me_client.get(ME_URL)
    finally:
        gestao_patch.stop()
        login_service_patch.stop()

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['associacao'] == {'uuid': '', 'nome': '', 'nome_escola': '', 'tipo_escola': ''}


def test_me_view_permissoes_flag_desativada_retorna_permissoes_de_todos_os_grupos(
    me_client, me_user, grupo_suporte, unidades_com_acesso
):
    me_user.groups.add(grupo_suporte)

    gestao_patch, login_service_patch = mock_login_usuario_service(unidades_com_acesso)
    try:
        with override_flag('novo-suporte-unidades', active=False):
            response = me_client.get(ME_URL)
    finally:
        gestao_patch.stop()
        login_service_patch.stop()

    permissoes = response.json()['permissoes']
    assert sorted(permissoes) == ['view_tipodevolucaoaotesouro', 'view_unidade']


def test_me_view_permissoes_flag_ativa_sem_suporte_retorna_apenas_grupos_normais(
    me_client, me_user, grupo_suporte, unidades_com_acesso
):
    me_user.groups.add(grupo_suporte)

    gestao_patch, login_service_patch = mock_login_usuario_service(unidades_com_acesso)
    try:
        with override_flag('novo-suporte-unidades', active=True):
            response = me_client.get(ME_URL)
    finally:
        gestao_patch.stop()
        login_service_patch.stop()

    assert response.json()['permissoes'] == ['view_tipodevolucaoaotesouro']


def test_me_view_permissoes_flag_ativa_com_suporte_retorna_apenas_grupos_de_suporte(
    me_client, me_user, grupo_suporte, unidades_com_acesso
):
    me_user.groups.add(grupo_suporte)

    gestao_patch, login_service_patch = mock_login_usuario_service(unidades_com_acesso)
    try:
        with override_flag('novo-suporte-unidades', active=True):
            response = me_client.get(f'{ME_URL}?suporte=true')
    finally:
        gestao_patch.stop()
        login_service_patch.stop()

    assert response.json()['permissoes'] == ['view_unidade']


def test_me_view_remove_visao_sme_quando_flag_ativa_e_suporte_true(
    me_client, me_user, visao_sme, unidades_com_acesso
):
    me_user.visoes.add(visao_sme)

    gestao_patch, login_service_patch = mock_login_usuario_service(unidades_com_acesso)
    try:
        with override_flag('novo-suporte-unidades', active=True):
            response = me_client.get(f'{ME_URL}?suporte=true')
    finally:
        gestao_patch.stop()
        login_service_patch.stop()

    assert 'SME' not in response.json()['visoes']
    assert 'UE' in response.json()['visoes']


def test_me_view_mantem_visao_sme_quando_suporte_true_mas_flag_desativada(
    me_client, me_user, visao_sme, unidades_com_acesso
):
    me_user.visoes.add(visao_sme)

    gestao_patch, login_service_patch = mock_login_usuario_service(unidades_com_acesso)
    try:
        with override_flag('novo-suporte-unidades', active=False):
            response = me_client.get(f'{ME_URL}?suporte=true')
    finally:
        gestao_patch.stop()
        login_service_patch.stop()

    assert 'SME' in response.json()['visoes']


def test_me_view_repassa_suporte_para_login_usuario_service(me_client, unidades_com_acesso):
    with patch('sme_ptrf_apps.users.api.views.login.GestaoUsuarioService'), \
         patch('sme_ptrf_apps.users.api.views.login.LoginUsuarioService') as mock_login_service_cls:
        mock_login_service_cls.return_value.unidades_que_usuario_tem_acesso = unidades_com_acesso
        mock_login_service_cls.return_value.unidades_que_perdeu_acesso = []
        mock_login_service_cls.return_value.mensagem_perca_acesso = None

        with override_flag('novo-suporte-unidades', active=True):
            me_client.get(f'{ME_URL}?suporte=true')

        _, kwargs = mock_login_service_cls.call_args
        assert kwargs['suporte'] is True


def test_me_view_feature_flags_retorna_flags_ativas_para_todos(me_client, unidades_com_acesso):
    gestao_patch, login_service_patch = mock_login_usuario_service(unidades_com_acesso)
    try:
        with override_flag('flag-de-teste-me-view', active=True):
            response = me_client.get(ME_URL)
    finally:
        gestao_patch.stop()
        login_service_patch.stop()

    assert 'flag-de-teste-me-view' in response.json()['feature_flags']

import pytest

from sme_ptrf_apps.users.fixtures.factories.usuario_factory import UsuarioFactory
from sme_ptrf_apps.users.fixtures.factories.unidade_em_suporte_factory import UnidadeEmSuporteFactory

pytestmark = pytest.mark.django_db


def test_usuario_sem_unidades_em_suporte(jwt_authenticated_client_u):
    usuario = UsuarioFactory()

    response = jwt_authenticated_client_u.get(
        f'/api/usuarios/{usuario.username}/unidades-em-suporte/?page=1')

    assert response.json() == {'links': {'next': None, 'previous': None},
                               'count': 0, 'page': 1, 'page_size': 10, 'results': []}


def test_usuario_com_unidades_em_suporte(jwt_authenticated_client_u):
    usuario = UsuarioFactory()

    UnidadeEmSuporteFactory(user=usuario)
    UnidadeEmSuporteFactory(user=usuario)

    response = jwt_authenticated_client_u.get(
        f'/api/usuarios/{usuario.username}/unidades-em-suporte/?page=1')

    assert response.json()['count'] == 2

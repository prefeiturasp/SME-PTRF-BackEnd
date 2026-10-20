import pytest

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from rest_framework.test import APIClient

from sme_ptrf_apps.users.models import Grupo, Visao


@pytest.fixture
def visao_ue():
    return Visao.objects.create(nome='UE')


@pytest.fixture
def visao_sme():
    return Visao.objects.create(nome='SME')


@pytest.fixture
def permissao_1():
    return Permission.objects.filter(codename='view_tipodevolucaoaotesouro').first()


@pytest.fixture
def permissao_2():
    return Permission.objects.filter(codename='view_unidade').first()


@pytest.fixture
def grupo_padrao(permissao_1, visao_ue):
    grupo = Grupo.objects.create(name='grupo-padrao', suporte=False)
    grupo.permissions.add(permissao_1)
    grupo.visoes.add(visao_ue)
    return grupo


@pytest.fixture
def grupo_suporte(permissao_2, visao_sme):
    grupo = Grupo.objects.create(name='grupo-suporte', suporte=True)
    grupo.permissions.add(permissao_2)
    grupo.visoes.add(visao_sme)
    return grupo


@pytest.fixture
def me_user(unidade, grupo_padrao, visao_ue):
    User = get_user_model()
    user = User.objects.create_user(
        username='7210418',
        password='Sgp0418',
        email='fulano@amcom.com.br',
        name='Fulano de Tal',
    )
    user.unidades.add(unidade)
    user.groups.add(grupo_padrao)
    user.visoes.add(visao_ue)
    user.save()
    return user


@pytest.fixture
def me_client(me_user):
    api_client = APIClient()
    api_client.force_authenticate(user=me_user)
    return api_client


@pytest.fixture
def unidades_com_acesso(unidade):
    return [{
        'uuid': str(unidade.uuid),
        'nome': unidade.nome,
        'tipo_unidade': unidade.tipo_unidade,
        'associacao': {'uuid': '', 'nome': ''},
        'acesso_de_suporte': False,
        'notificar_devolucao_por_recurso': {},
    }]

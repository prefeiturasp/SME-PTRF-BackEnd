import pytest

from django.contrib.auth import get_user_model

from model_bakery import baker

@pytest.fixture
def visao_ue():
    return baker.make('Visao', nome='UE')


@pytest.fixture
def visao_dre():
    return baker.make('Visao', nome='DRE')


@pytest.fixture
def visao_sme():
    return baker.make('Visao', nome='SME')


@pytest.fixture
def unidade_do_suporte(dre):
    return baker.make(
        'Unidade',
        nome='Escola Unidade Diferente',
        tipo_unidade='EMEI',
        codigo_eol='12345',
        dre=dre,
    )


@pytest.fixture
def unidade_do_suporte_tipo_dre():
    return baker.make(
        'Unidade',
        nome='DRE Teste',
        tipo_unidade='DRE',
        codigo_eol='54321',
        dre=None,
    )


@pytest.fixture
def usuario_do_suporte(
        dre,
        visao_sme):

    senha = 'Sgp0418'
    login = '271170'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(dre)
    user.visoes.add(visao_sme)
    user.save()
    return user


@pytest.fixture
def unidade_em_suporte(unidade_do_suporte, usuario_do_suporte):
    return baker.make(
        'UnidadeEmSuporte',
        unidade=unidade_do_suporte,
        user=usuario_do_suporte,
    )

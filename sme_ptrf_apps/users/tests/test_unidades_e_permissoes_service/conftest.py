import pytest

from django.contrib.auth import get_user_model

from model_bakery import baker


@pytest.fixture
def dre_a():
    return baker.make('Unidade', codigo_eol='99991', tipo_unidade='DRE', nome='DRE A', sigla='DA')


@pytest.fixture
def dre_b():
    return baker.make('Unidade', codigo_eol='99992', tipo_unidade='DRE', nome='DRE B', sigla='DB')


@pytest.fixture
def unidade_ue_a_dre_a(dre_a):
    return baker.make(
        'Unidade',
        nome='Escola A',
        tipo_unidade='EMEI',
        codigo_eol='123459',
        dre=dre_a,
    )


@pytest.fixture
def unidade_ue_b_dre_b(dre_b):
    return baker.make(
        'Unidade',
        nome='Escola B',
        tipo_unidade='EMEI',
        codigo_eol='271170',
        dre=dre_b,
    )


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
def usuario_unidade_a_dre_a(
        unidade_ue_a_dre_a,
        visao_ue
):

    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade_ue_a_dre_a)
    user.visoes.add(visao_ue)
    user.save()
    return user


@pytest.fixture
def usuario_unidade_b_dre_b(
        unidade_ue_b_dre_b,
        visao_ue,
):

    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade_ue_b_dre_b)
    user.visoes.add(visao_ue)
    user.save()
    return user


@pytest.fixture
def usuario_dre_a(
        dre_a,
        visao_dre,
):

    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(dre_a)
    user.visoes.add(visao_dre)
    user.save()
    return user

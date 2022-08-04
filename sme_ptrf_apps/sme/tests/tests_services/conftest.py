import datetime
import pytest

from model_bakery import baker
from django.contrib.auth import get_user_model
from sme_ptrf_apps.receitas.models.receita import Receita
from sme_ptrf_apps.receitas.models.motivo_estorno import MotivoEstorno


pytestmark = pytest.mark.django_db


@pytest.fixture
def motivo_estorno_01():
    return baker.make(
        'MotivoEstorno',
        motivo="Motivo de estorno 01"
    )


@pytest.fixture
def motivo_estorno_02():
    return baker.make(
        'MotivoEstorno',
        motivo="Motivo de estorno 02"
    )


@pytest.fixture
def receita_queryset(associacao, conta_associacao, acao_associacao, tipo_receita, motivo_estorno_01, motivo_estorno_02):
    baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 28),
        valor=50.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
        motivos_estorno=[motivo_estorno_01, motivo_estorno_02],
        _quantity=2
    )
    return Receita.objects.all()


@pytest.fixture
def usuario_para_teste():
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(
        username=login,
        password=senha,
        email=email
    )
    user.save()

    return user

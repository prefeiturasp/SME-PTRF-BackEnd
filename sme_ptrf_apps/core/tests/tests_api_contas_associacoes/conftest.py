import pytest

from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.core.models import ContaAssociacao
from sme_ptrf_apps.core.models import TipoConta


@pytest.fixture
def conta_associacao_1(conta_associacao_factory):
    conta_associacao_factory.create()
    return ContaAssociacao.objects.first()


@pytest.fixture
def conta_associacao_2(conta_associacao_factory):
    conta_associacao_factory.create()
    conta_associacao_factory.create()
    return ContaAssociacao.objects.all()


@pytest.fixture
def associacao_1(associacao_factory):
    associacao_factory.create()
    return Associacao.objects.first()


@pytest.fixture
def tipo_conta_1(tipo_conta_factory):
    tipo_conta_factory.create()
    return TipoConta.objects.first()

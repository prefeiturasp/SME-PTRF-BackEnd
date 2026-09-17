import pytest
from django.core.exceptions import ValidationError
from model_bakery import baker

from sme_ptrf_apps.core.models import Recurso
from sme_ptrf_apps.core.services.acao_associacao_service import validar_troca_recurso

pytestmark = pytest.mark.django_db


@pytest.fixture
def outro_recurso():
    return baker.make(
        'Recurso',
        nome_exibicao='Outro Recurso',
        cor=Recurso.CorChoices.VERDE,
    )


def test_validar_troca_recurso_acao_sem_pk(acao_factory, outro_recurso):
    acao_nova = acao_factory.build()

    assert validar_troca_recurso(acao_nova, outro_recurso) is None


def test_validar_troca_recurso_mesmo_recurso(acao):
    assert validar_troca_recurso(acao, acao.recurso) is None


def test_validar_troca_recurso_sem_nenhuma_associacao(acao, outro_recurso):
    with pytest.raises(ValidationError):
        validar_troca_recurso(acao, outro_recurso)


def test_validar_troca_recurso_com_acao_associacao_vinculada(acao, acao_associacao, outro_recurso):
    assert validar_troca_recurso(acao, outro_recurso) is None


def test_validar_troca_recurso_com_rateio_vinculado(
    acao, acao_associacao, rateio_despesa_factory, outro_recurso,
):
    rateio_despesa_factory(acao_associacao=acao_associacao)

    assert validar_troca_recurso(acao, outro_recurso) is None

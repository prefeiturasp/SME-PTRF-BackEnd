import pytest

from django.contrib import admin
from model_bakery import baker

from ...models import PrestacaoConta, ComentarioAnalisePrestacao

pytestmark = pytest.mark.django_db

@pytest.fixture
def comentario_analise_prestacao(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'ComentarioAnalisePrestacao',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        ordem=1,
        comentario='Teste',
    )


def test_instance_model(comentario_analise_prestacao):
    model = comentario_analise_prestacao
    assert isinstance(model, ComentarioAnalisePrestacao)
    assert isinstance(model.prestacao_conta, PrestacaoConta)
    assert model.ordem
    assert model.comentario


def test_srt_model(comentario_analise_prestacao):
    assert comentario_analise_prestacao.__str__() == '1 - Teste'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[ComentarioAnalisePrestacao]

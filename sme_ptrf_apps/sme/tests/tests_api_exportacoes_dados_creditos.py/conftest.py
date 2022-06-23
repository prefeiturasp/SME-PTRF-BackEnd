import datetime
import pytest

from model_bakery import baker

pytestmark = pytest.mark.django_db


@pytest.fixture
def receita_queryset(associacao, conta_associacao, acao_associacao, tipo_receita, motivo_estorno_01, motivo_estorno_02):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 28),
        valor=50.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
        motivos_estorno=[motivo_estorno_01, motivo_estorno_02],
    )

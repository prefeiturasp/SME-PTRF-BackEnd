import pytest

from ....models.prestacao_conta import STATUS_ABERTO
from ....services import iniciar_prestacao_de_contas

pytestmark = pytest.mark.django_db


def test_prestacao_de_contas_deve_ser_criada(associacao, periodo):
    prestacao = iniciar_prestacao_de_contas(associacao=associacao, periodo=periodo)

    assert prestacao.periodo == periodo
    assert prestacao.associacao == associacao
    assert prestacao.status == STATUS_ABERTO

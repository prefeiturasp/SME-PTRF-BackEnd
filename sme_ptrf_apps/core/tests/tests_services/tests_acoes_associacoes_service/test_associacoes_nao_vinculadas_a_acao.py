import pytest

from ....services import associacoes_nao_vinculadas_a_acao

pytestmark = pytest.mark.django_db


def test_retorna_associacoes_nao_vinculadas(
    acao_x,
    acao_y,
    associacao_eco_delta_000087,
    associacao_charli_bravo_000086,
    acao_associacao_eco_delta_000087_x,
    acao_associacao_eco_delta_000087_y_inativa,
    acao_associacao_charli_bravo_000086_y
):
    result = associacoes_nao_vinculadas_a_acao(acao_x)
    assert result.count() == 1
    assert result.first() == associacao_charli_bravo_000086

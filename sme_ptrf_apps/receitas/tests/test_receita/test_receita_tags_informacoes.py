import pytest

from ...models import Receita

pytestmark = pytest.mark.django_db


def test_get_tags_informacoes_list():
    tags = Receita.get_tags_informacoes_list()
    assert tags == [
        {"id": "6", "nome": "Inativado", "descricao": "Lançamento inativado."},
    ]

import pytest

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
def test_str_representation(bem_produzido_despesa_1):
    assert str(bem_produzido_despesa_1) == f"Despesa {bem_produzido_despesa_1.id} - ({bem_produzido_despesa_1.despesa.id}) do {bem_produzido_despesa_1.bem_produzido}"

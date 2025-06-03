import pytest

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
def test_str_representation(bem_produzido_rateio_1):
    assert str(bem_produzido_rateio_1) == f"Rateio {bem_produzido_rateio_1.id} - ({bem_produzido_rateio_1.rateio.id}) da {bem_produzido_rateio_1.bem_produzido_despesa}"
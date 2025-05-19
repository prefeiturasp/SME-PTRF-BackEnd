import pytest

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
def test_str_representation(bem_produzido_1):
    assert str(bem_produzido_1) == f"Bem produzido {bem_produzido_1.pk}"

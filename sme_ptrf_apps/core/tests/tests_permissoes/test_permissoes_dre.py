import pytest

from django.contrib.auth.models import Permission

pytestmark = pytest.mark.django_db


def test_suporte_unidades_dre_permissions():
    assert Permission.objects.filter(codename='access_suporte_unidades_dre').exists()

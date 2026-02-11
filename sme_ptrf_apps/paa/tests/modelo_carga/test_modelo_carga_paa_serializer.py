import pytest

from sme_ptrf_apps.paa.api.serializers import ModeloCargaPaaSerializer

pytestmark = pytest.mark.django_db


def test_modelo_carga_paa_list_serializer(modelo_carga_paa_plano_anual):
    serializer = ModeloCargaPaaSerializer(modelo_carga_paa_plano_anual)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'tipo_carga' in serializer.data
    assert 'arquivo' in serializer.data

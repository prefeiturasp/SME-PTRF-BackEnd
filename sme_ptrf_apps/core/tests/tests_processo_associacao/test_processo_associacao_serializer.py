import pytest

from sme_ptrf_apps.core.api.serializers import ProcessoAssociacaoRetrieveSerializer, ProcessoAssociacaoCreateSerializer

pytestmark = pytest.mark.django_db


def test_processo_associacao_list_serializer(processo_associacao_123456_2019):
    serializer = ProcessoAssociacaoRetrieveSerializer(processo_associacao_123456_2019)
    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['associacao']
    assert serializer.data['numero_processo']
    assert serializer.data['ano']
    assert serializer.data['criado_em']
    assert serializer.data['alterado_em']


def test_processo_associacao_create_serializer(processo_associacao_123456_2019):
    serializer = ProcessoAssociacaoCreateSerializer(processo_associacao_123456_2019)
    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['associacao']
    assert serializer.data['numero_processo']
    assert serializer.data['ano']



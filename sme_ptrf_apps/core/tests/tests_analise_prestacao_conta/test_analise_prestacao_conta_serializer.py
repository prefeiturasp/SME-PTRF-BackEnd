import pytest

from ...api.serializers import AnalisePrestacaoContaRetrieveSerializer

pytestmark = pytest.mark.django_db


def test_retrieve_serializer(analise_prestacao_conta_2020_1):
    serializer = AnalisePrestacaoContaRetrieveSerializer(analise_prestacao_conta_2020_1)
    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['id']
    assert serializer.data['prestacao_conta']
    assert serializer.data['devolucao_prestacao_conta']
    assert serializer.data['status']
    assert serializer.data['criado_em']
    assert serializer.data['versao']
    assert serializer.data['versao_pdf_apresentacao_apos_acertos']

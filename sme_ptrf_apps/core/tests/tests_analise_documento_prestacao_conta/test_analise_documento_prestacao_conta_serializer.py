import pytest

from ...api.serializers import AnaliseDocumentoPrestacaoContaRetrieveSerializer

pytestmark = pytest.mark.django_db


def test_retrieve_serializer(
    analise_documento_prestacao_conta_2020_1_ata_correta,
    despesa_no_periodo,
    receita_100_no_periodo
):
    serializer = AnaliseDocumentoPrestacaoContaRetrieveSerializer(analise_documento_prestacao_conta_2020_1_ata_correta)
    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['id']
    assert serializer.data['resultado'] == 'CORRETO'
    assert serializer.data['conta_associacao']
    assert serializer.data['analise_prestacao_conta']
    assert serializer.data['tipo_documento_prestacao_conta']
    assert serializer.data['solicitacoes_de_ajuste_da_analise'] == []
    assert serializer.data['status_realizacao']
    assert serializer.data['requer_esclarecimentos'] is not None
    assert serializer.data['requer_inclusao_credito'] is not None
    assert serializer.data['requer_inclusao_gasto'] is not None
    assert serializer.data['requer_ajuste_externo'] is not None
    assert serializer.data['requer_edicao_informacao_conciliacao'] is not None


def test_update_serializer(analise_documento_prestacao_conta_com_justificativa_2020_1_ata_correta):
    serializer = AnaliseDocumentoPrestacaoContaRetrieveSerializer(
        analise_documento_prestacao_conta_com_justificativa_2020_1_ata_correta)
    assert serializer.data is not None

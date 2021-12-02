import pytest
from sme_ptrf_apps.core.api.serializers import AnaliseValorReprogramadoPrestacaoContaSerializer

pytestmark = pytest.mark.django_db


def test_analise_valor_reprogramado_serializer(analise_valor_reprogramado_por_acao):
    serializer = AnaliseValorReprogramadoPrestacaoContaSerializer(analise_valor_reprogramado_por_acao)

    campos_esperados = [
        "uuid",
        "analise_prestacao_conta",
        "conta_associacao",
        "acao_associacao",
        "valor_saldo_reprogramado_correto",
        "novo_saldo_reprogramado_custeio",
        "novo_saldo_reprogramado_capital",
        "novo_saldo_reprogramado_livre",
    ]

    assert serializer.data
    assert [key for key in serializer.data.keys()] == campos_esperados

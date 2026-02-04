import pytest
from rest_framework.exceptions import ValidationError

from sme_ptrf_apps.paa.api.serializers import ReceitaPrevistaPaaSerializer
from sme_ptrf_apps.paa.fixtures.factories.documento_paa_factory import DocumentoPaaFactory

pytestmark = pytest.mark.django_db


def test_receita_prevista_serializer_list_serializer(receita_prevista_paa):
    serializer = ReceitaPrevistaPaaSerializer(receita_prevista_paa)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'acao_associacao' in serializer.data
    assert 'previsao_valor_custeio' in serializer.data
    assert 'previsao_valor_capital' in serializer.data
    assert 'previsao_valor_livre' in serializer.data
    assert 'saldo_congelado_custeio' in serializer.data
    assert 'saldo_congelado_capital' in serializer.data
    assert 'saldo_congelado_livre' in serializer.data


def test_receita_prevista_serializer_bloqueia_edicao_com_documento_final_concluido(
    receita_prevista_paa, acao_associacao
):
    """Testa que não é possível editar receita prevista quando documento final está concluído"""
    DocumentoPaaFactory.create(paa=receita_prevista_paa.paa, versao="FINAL", status_geracao="CONCLUIDO")
    
    payload = {
        "previsao_valor_custeio": "1000.00",
    }
    
    serializer = ReceitaPrevistaPaaSerializer(
        instance=receita_prevista_paa,
        data=payload,
        partial=True
    )
    
    assert not serializer.is_valid()
    assert 'mensagem' in serializer.errors
    assert 'Não é possível editar receitas previstas após a geração do documento final do PAA.' in serializer.errors['mensagem']

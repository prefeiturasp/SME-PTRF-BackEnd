import pytest
from unittest.mock import patch

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
    assert (
        'Não é possível editar receitas previstas após a '
        'geração do documento final do PAA.') in serializer.errors['mensagem']


def test_get_acao_associacao_objeto_retorna_dados(receita_prevista_paa):
    serializer = ReceitaPrevistaPaaSerializer(receita_prevista_paa)
    objeto = serializer.data['acao_associacao_objeto']
    assert objeto is not None
    assert 'uuid' in objeto
    assert 'acao_objeto' in objeto


def test_get_acao_associacao_objeto_none_quando_sem_acao_associacao(receita_prevista_paa):
    receita_prevista_paa.acao_associacao = None
    serializer = ReceitaPrevistaPaaSerializer(receita_prevista_paa)
    assert serializer.data['acao_associacao_objeto'] is None


def test_validate_sem_paa_no_create_retorna_erro():
    from rest_framework.exceptions import ValidationError
    serializer = ReceitaPrevistaPaaSerializer()
    with pytest.raises(ValidationError) as exc_info:
        serializer.validate({})
    assert 'paa' in exc_info.value.detail
    assert 'obrigat' in str(exc_info.value.detail['paa'])


def test_validate_sem_acao_associacao_no_create_retorna_erro(paa):
    from rest_framework.exceptions import ValidationError
    serializer = ReceitaPrevistaPaaSerializer()
    with pytest.raises(ValidationError) as exc_info:
        serializer.validate({"paa": paa})
    assert 'acao_associacao' in exc_info.value.detail
    assert 'obrigat' in str(exc_info.value.detail['acao_associacao'])


def test_validate_paa_string_uuid_nao_encontrado(acao_associacao):
    serializer = ReceitaPrevistaPaaSerializer()
    with pytest.raises(Exception) as exc_info:
        serializer.validate({
            "paa": "00000000-0000-0000-0000-000000000000",
            "acao_associacao": acao_associacao,
        })
    assert exc_info.value.detail["mensagem"] == "PAA não encontrado!"


def test_update_sem_confirmar_limpeza_nao_chama_limpar_prioridades(receita_prevista_paa):
    payload = {"previsao_valor_custeio": "999.00"}
    serializer = ReceitaPrevistaPaaSerializer(
        instance=receita_prevista_paa, data=payload, partial=True
    )
    with patch.object(ReceitaPrevistaPaaSerializer, '_verificar_prioridades_paa_impactadas'):
        with patch.object(ReceitaPrevistaPaaSerializer, '_limpar_prioridades_paa') as mock_limpar:
            assert serializer.is_valid(), serializer.errors
            serializer.save()
            mock_limpar.assert_not_called()


def test_update_com_confirmar_limpeza_chama_limpar_prioridades(receita_prevista_paa):
    payload = {
        "previsao_valor_custeio": "999.00",
        "confirmar_limpeza_prioridades_paa": True,
    }
    serializer = ReceitaPrevistaPaaSerializer(
        instance=receita_prevista_paa, data=payload, partial=True
    )
    with patch.object(ReceitaPrevistaPaaSerializer, '_verificar_prioridades_paa_impactadas'):
        with patch.object(ReceitaPrevistaPaaSerializer, '_limpar_prioridades_paa') as mock_limpar:
            assert serializer.is_valid(), serializer.errors
            serializer.save()
            mock_limpar.assert_called_once()


def test_create_remove_flag_confirmacao_do_validated_data(paa, acao_associacao):
    payload = {
        "paa": str(paa.uuid),
        "acao_associacao": str(acao_associacao.uuid),
        "previsao_valor_custeio": "50.00",
        "confirmar_limpeza_prioridades_paa": True,
    }
    serializer = ReceitaPrevistaPaaSerializer(data=payload)
    with patch.object(ReceitaPrevistaPaaSerializer, '_verificar_prioridades_paa_impactadas'):
        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()
        assert instance.pk is not None


def test_prioridades_impactadas_sem_confirmar_levanta_erro(receita_prevista_paa):
    from sme_ptrf_apps.paa.services import PrioridadesPaaImpactadasReceitasPrevistasPTRFService

    payload = {"previsao_valor_custeio": "1.00"}
    serializer = ReceitaPrevistaPaaSerializer(
        instance=receita_prevista_paa, data=payload, partial=True
    )
    with patch.object(
        PrioridadesPaaImpactadasReceitasPrevistasPTRFService,
        'verificar_prioridades_impactadas',
        return_value=[{'uuid': 'x'}]
    ):
        assert not serializer.is_valid()
        assert 'confirmar' in serializer.errors

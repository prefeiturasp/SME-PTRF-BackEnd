import pytest
from unittest.mock import Mock, patch
from django.db import DatabaseError
from ...api.serializers.despesa_serializer import (DespesaSerializer, DespesaCreateSerializer, DespesaListSerializer)

pytestmark = pytest.mark.django_db


def test_serializer(despesa):

    serializer = DespesaSerializer(despesa)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['associacao']
    assert serializer.data['numero_documento']
    assert serializer.data['data_documento']
    assert serializer.data['tipo_documento']
    assert serializer.data['cpf_cnpj_fornecedor']
    assert serializer.data['nome_fornecedor']
    assert serializer.data['tipo_transacao']
    assert serializer.data['documento_transacao'] is not None
    assert serializer.data['data_transacao']
    assert serializer.data['valor_total']
    assert serializer.data['valor_recursos_proprios']
    assert serializer.data['eh_despesa_sem_comprovacao_fiscal'] is False
    assert serializer.data['eh_despesa_reconhecida_pela_associacao']
    assert serializer.data['numero_boletim_de_ocorrencia']
    assert serializer.data['retem_imposto'] is False
    assert serializer.data['motivos_pagamento_antecipado'] is not None
    assert serializer.data['outros_motivos_pagamento_antecipado'] is not None


def test_create_serializer(despesa, rateio_despesa_capital):

    serializer = DespesaCreateSerializer(despesa)

    assert serializer.data is not None


def test_list_serializer(despesa):

    serializer = DespesaListSerializer(despesa)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['associacao']
    assert serializer.data['numero_documento']
    assert serializer.data['data_documento']
    assert serializer.data['tipo_documento']
    assert serializer.data['cpf_cnpj_fornecedor']
    assert serializer.data['nome_fornecedor']
    assert serializer.data['valor_total']
    assert serializer.data['valor_ptrf']

def test_update_do_create_serializer_deve_fazer_retry_quando_ocorrer_timeout(despesa):
    validated_data = {}

    resultado_esperado = Mock()

    with patch(
        "sme_ptrf_apps.despesas.services.despesa_service.DespesaService.update"
    ) as mock_update, patch("time.sleep") as mock_sleep:

        mock_update.side_effect = [
            DatabaseError("timeout na conexão"),
            resultado_esperado,
        ]
       
        resultado = DespesaCreateSerializer(despesa).update(
            instance=despesa,
            validated_data=validated_data
        )

        assert resultado == resultado_esperado
        assert mock_update.call_count == 2

        mock_sleep.assert_called_once_with(2)


def test_update_do_create_nao_deve_fazer_retry_para_erros_nao_recuperaveis(
    despesa
):
    validated_data = {}

    with patch(
        "sme_ptrf_apps.despesas.services.despesa_service.DespesaService.update"
    ) as mock_update, patch("time.sleep") as mock_sleep:

        mock_update.side_effect = DatabaseError(
            "violacao de constraint"
        )

        with pytest.raises(DatabaseError):
            DespesaCreateSerializer(despesa).update(
                instance=despesa,
                validated_data=validated_data
            )

        assert mock_update.call_count == 1
        mock_sleep.assert_not_called()

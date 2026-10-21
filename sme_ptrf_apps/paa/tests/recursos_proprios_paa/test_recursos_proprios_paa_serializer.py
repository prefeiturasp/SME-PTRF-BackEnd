import pytest
from datetime import date
from unittest.mock import patch

from sme_ptrf_apps.paa.api.serializers.fonte_recurso_paa_serializer import FonteRecursoPaaSerializer
from sme_ptrf_apps.paa.api.serializers.recurso_proprio_paa_serializer import (
    RecursoProprioPaaCreateSerializer,
    RecursoProprioPaaListSerializer,
    RecursoProprioPaaListDocumentoPaaSerializer,
)

pytestmark = pytest.mark.django_db


def test_fonte_recurso_paa_list_serializer(fonte_recurso_paa):
    serializer = FonteRecursoPaaSerializer(fonte_recurso_paa)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'nome' in serializer.data
    assert 'id' in serializer.data


class TestRecursoProprioPaaCreateSerializer:

    def test_campos_serializados(self, recurso_proprio_paa):
        serializer = RecursoProprioPaaCreateSerializer(recurso_proprio_paa)
        assert 'uuid' in serializer.data
        assert 'paa' in serializer.data
        assert 'associacao' in serializer.data
        assert 'fonte_recurso' in serializer.data
        assert 'data_prevista' in serializer.data
        assert 'descricao' in serializer.data
        assert 'valor' in serializer.data

    def test_validate_sem_paa_no_create_retorna_erro(self):
        serializer = RecursoProprioPaaCreateSerializer()
        with pytest.raises(Exception) as exc_info:
            serializer.validate({})
        assert exc_info.value.detail['paa'] == 'PAA não informado.'

    def test_validate_paa_string_uuid_nao_encontrado(self, associacao, fonte_recurso_paa):
        serializer = RecursoProprioPaaCreateSerializer()
        with pytest.raises(Exception) as exc_info:
            serializer.validate({
                "paa": "00000000-0000-0000-0000-000000000000",
                "associacao": associacao,
                "fonte_recurso": fonte_recurso_paa,
            })
        assert exc_info.value.detail["mensagem"] == "PAA não encontrado!"

    def test_validate_bloqueia_edicao_com_documento_final_concluido(self, recurso_proprio_paa):
        from sme_ptrf_apps.paa.fixtures.factories.documento_paa_factory import DocumentoPaaFactory

        DocumentoPaaFactory.create(
            paa=recurso_proprio_paa.paa, versao="FINAL", status_geracao="CONCLUIDO"
        )
        payload = {"descricao": "Novo valor"}
        serializer = RecursoProprioPaaCreateSerializer(
            instance=recurso_proprio_paa, data=payload, partial=True
        )
        assert not serializer.is_valid()
        assert 'mensagem' in serializer.errors
        assert (
            'Não é possível editar receitas previstas de Recurso Próprio após a '
            'geração do documento final do PAA.') in serializer.errors['mensagem']

    def test_update_sem_confirmar_limpeza_nao_chama_limpar_prioridades(self, recurso_proprio_paa):
        payload = {"descricao": "Atualizado"}
        serializer = RecursoProprioPaaCreateSerializer(
            instance=recurso_proprio_paa, data=payload, partial=True
        )
        with patch.object(RecursoProprioPaaCreateSerializer, '_verificar_prioridades_paa_impactadas'):
            with patch.object(RecursoProprioPaaCreateSerializer, '_limpar_prioridades_paa') as mock_limpar:
                assert serializer.is_valid(), serializer.errors
                serializer.save()
                mock_limpar.assert_not_called()

    def test_update_com_confirmar_limpeza_chama_limpar_prioridades(self, recurso_proprio_paa):
        payload = {
            "descricao": "Atualizado",
            "confirmar_limpeza_prioridades_paa": True,
        }
        serializer = RecursoProprioPaaCreateSerializer(
            instance=recurso_proprio_paa, data=payload, partial=True
        )
        with patch.object(RecursoProprioPaaCreateSerializer, '_verificar_prioridades_paa_impactadas'):
            with patch.object(RecursoProprioPaaCreateSerializer, '_limpar_prioridades_paa') as mock_limpar:
                assert serializer.is_valid(), serializer.errors
                serializer.save()
                mock_limpar.assert_called_once()

    def test_create_remove_flag_confirmacao_do_validated_data(self, paa, associacao, fonte_recurso_paa):
        payload = {
            "paa": str(paa.uuid),
            "associacao": str(associacao.uuid),
            "fonte_recurso": str(fonte_recurso_paa.uuid),
            "descricao": "Recurso novo",
            "valor": "100.00",
            "confirmar_limpeza_prioridades_paa": True,
        }
        serializer = RecursoProprioPaaCreateSerializer(data=payload)
        with patch.object(RecursoProprioPaaCreateSerializer, '_verificar_prioridades_paa_impactadas'):
            assert serializer.is_valid(), serializer.errors
            instance = serializer.save()
            assert instance.pk is not None

    def test_prioridades_impactadas_sem_confirmar_levanta_erro(self, recurso_proprio_paa):
        from sme_ptrf_apps.paa.services import PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService

        payload = {"descricao": "Atualizado"}
        serializer = RecursoProprioPaaCreateSerializer(
            instance=recurso_proprio_paa, data=payload, partial=True
        )
        with patch.object(
            PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService,
            'verificar_prioridades_impactadas',
            return_value=[{'uuid': 'x'}]
        ):
            assert not serializer.is_valid()
            assert 'confirmar' in serializer.errors


class TestRecursoProprioPaaListSerializer:

    def test_campos_serializados(self, recurso_proprio_paa):
        serializer = RecursoProprioPaaListSerializer(recurso_proprio_paa)
        assert 'uuid' in serializer.data
        assert 'paa' in serializer.data
        assert 'associacao' in serializer.data
        assert 'fonte_recurso' in serializer.data
        assert 'alteracao' in serializer.data

    def test_get_alteracao_sem_context_retorna_none(self, recurso_proprio_paa):
        serializer = RecursoProprioPaaListSerializer(recurso_proprio_paa)
        assert serializer.data['alteracao'] is None

    def test_get_alteracao_com_context_sem_item_retorna_none(self, recurso_proprio_paa):
        serializer = RecursoProprioPaaListSerializer(
            recurso_proprio_paa, context={'alteracoes': {'receitas_recurso_proprio': {}}}
        )
        assert serializer.data['alteracao'] is None

    def test_get_alteracao_com_context_retorna_acao(self, recurso_proprio_paa):
        alteracoes = {
            'receitas_recurso_proprio': {
                str(recurso_proprio_paa.uuid): {'acao': 'modificado'}
            }
        }
        serializer = RecursoProprioPaaListSerializer(recurso_proprio_paa, context={'alteracoes': alteracoes})
        assert serializer.data['alteracao'] == 'modificado'

    def test_get_associacao_uuid(self, recurso_proprio_paa):
        serializer = RecursoProprioPaaListSerializer(recurso_proprio_paa)
        assert serializer.data['associacao'] == recurso_proprio_paa.associacao.uuid


class TestRecursoProprioPaaListDocumentoPaaSerializer:

    def test_get_data_prevista_formatada(self, recurso_proprio_paa_factory):
        recurso = recurso_proprio_paa_factory(data_prevista=date(2025, 3, 15))
        serializer = RecursoProprioPaaListDocumentoPaaSerializer(recurso)
        assert serializer.data['data_prevista'] == '15/03/2025'

    def test_get_associacao_uuid(self, recurso_proprio_paa):
        serializer = RecursoProprioPaaListDocumentoPaaSerializer(recurso_proprio_paa)
        assert serializer.data['associacao'] == recurso_proprio_paa.associacao.uuid

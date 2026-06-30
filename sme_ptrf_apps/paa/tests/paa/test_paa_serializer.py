import pytest
from unittest.mock import patch

from sme_ptrf_apps.paa.api.serializers import PaaSerializer
from sme_ptrf_apps.paa.api.serializers.paa_serializer import PaaRetificacaoComparativoSerializer, PaaDreSerializer

pytestmark = pytest.mark.django_db


def test_paa_retriever_serializer(paa):
    serializer = PaaSerializer(paa)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'periodo_paa' in serializer.data
    assert 'associacao' in serializer.data
    assert 'periodo_paa_objeto' in serializer.data
    assert 'saldo_congelado_em' in serializer.data
    assert 'texto_introducao' in serializer.data
    assert 'texto_conclusao' in serializer.data
    assert 'status' in serializer.data


def test_paa_model_tem_campos_acoes_conclusao(paa):
    """Testa que o modelo PAA tem os campos ManyToMany para ações na conclusão"""
    assert hasattr(paa, 'acoes_conclusao')
    assert hasattr(paa, 'acoes_pdde_conclusao')
    assert hasattr(paa, 'outros_recursos_periodo_conclusao')
    assert paa.acoes_conclusao.count() == 0
    assert paa.acoes_pdde_conclusao.count() == 0
    assert paa.outros_recursos_periodo_conclusao.count() == 0


def test_paa_serializer_status_andamento(paa):
    serializer = PaaSerializer(paa)
    assert 'status_andamento' in serializer.data


def test_paa_serializer_tem_documento_final_sem_retificacao(paa):
    serializer = PaaSerializer(paa)
    assert 'tem_documento_final_concluido' in serializer.data
    assert serializer.data['tem_documento_final_concluido'] is False


def test_paa_serializer_tem_documento_final_com_retificacao(paa_factory, documento_paa_factory):
    paa = paa_factory()
    paa.set_paa_status_em_retificacao()
    serializer = PaaSerializer(paa)
    assert 'tem_documento_final_concluido' in serializer.data


def test_paa_serializer_tem_ata_concluida_sem_retificacao(paa):
    serializer = PaaSerializer(paa)
    assert 'tem_ata_concluida' in serializer.data
    assert serializer.data['tem_ata_concluida'] is False


def test_paa_serializer_tem_ata_concluida_com_retificacao(paa_factory):
    paa = paa_factory()
    paa.set_paa_status_em_retificacao()
    serializer = PaaSerializer(paa)
    assert 'tem_ata_concluida' in serializer.data


def test_paa_serializer_validate_sem_periodo_vigente(paa_factory, associacao):
    paa_factory()
    data = {'associacao': str(associacao.uuid)}
    serializer = PaaSerializer(data=data)
    with patch('sme_ptrf_apps.paa.services.paa_service.PaaService.pode_elaborar_novo_paa'):
        with patch('sme_ptrf_apps.paa.api.serializers.paa_serializer.PeriodoPaa.periodo_vigente', return_value=None):
            assert not serializer.is_valid()
            assert 'non_field_errors' in serializer.errors


def test_paa_serializer_validate_paa_service_exception(paa_factory, associacao):
    paa_factory()
    data = {'associacao': str(associacao.uuid)}
    serializer = PaaSerializer(data=data)
    with patch('sme_ptrf_apps.paa.services.paa_service.PaaService.pode_elaborar_novo_paa',
               side_effect=Exception('Não pode elaborar')):
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors


class TestPaaRetificacaoComparativoSerializer:

    def test_campos_adicionais_retificacao(self, paa):
        serializer = PaaRetificacaoComparativoSerializer(paa, context={'alteracoes': {'prioridades': {}}})
        assert 'alteracoes' in serializer.data
        assert 'ata_elaboracao' in serializer.data
        assert 'ata_retificacao' in serializer.data

    def test_get_alteracoes_retorna_context(self, paa):
        alteracoes = {'prioridades': {'uuid': {'acao': 'modificado'}}}
        serializer = PaaRetificacaoComparativoSerializer(paa, context={'alteracoes': alteracoes})
        assert serializer.data['alteracoes'] == alteracoes

    def test_get_alteracoes_sem_context_retorna_vazio(self, paa):
        serializer = PaaRetificacaoComparativoSerializer(paa)
        assert serializer.data['alteracoes'] == {}


class TestPaaDreSerializer:

    def test_campos_paa_dre_serializer(self, paa):
        serializer = PaaDreSerializer(paa)
        assert 'uuid' in serializer.data
        assert 'periodo_paa' in serializer.data
        assert 'unidade' in serializer.data
        assert 'status' in serializer.data
        assert 'status_display' in serializer.data
        assert 'tem_documentos' in serializer.data

    def test_tem_documentos_false_sem_documentos(self, paa):
        serializer = PaaDreSerializer(paa)
        assert serializer.data['tem_documentos'] is False

import pytest
from datetime import timedelta

from sme_ptrf_apps.paa.api.serializers.ata_paa_serializer import AtaPaaLookUpSerializer, AtaPaaSerializer
from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_COMPLETO

pytestmark = pytest.mark.django_db


def test_lookup_serializer(ata_paa):
    serializer = AtaPaaLookUpSerializer(ata_paa)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['nome']
    assert serializer.data['alterado_em'] is None


def test_serializer(ata_paa):
    serializer = AtaPaaSerializer(ata_paa)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['paa']
    assert serializer.data['associacao']
    assert serializer.data['tipo_ata']
    assert serializer.data['tipo_reuniao']
    assert serializer.data['convocacao']
    assert serializer.data['data_reuniao']
    assert serializer.data['local_reuniao']
    assert serializer.data['comentarios']
    assert serializer.data['parecer_conselho']
    assert serializer.data['nome']
    assert serializer.data['hora_reuniao'] == "00:00"
    assert serializer.data['justificativa'] == ""
    assert 'precisa_professor_gremio' in serializer.data
    assert isinstance(serializer.data['precisa_professor_gremio'], bool)


def test_serializer_precisa_professor_gremio_true(ata_paa, parametros, acao_factory, acao_associacao_factory, despesa_factory, rateio_despesa_factory):
    """Testa se serializer retorna precisa_professor_gremio=True quando unidade precisa e há despesas completas com ação grêmio no período"""
    parametros.tipos_unidades_professor_gremio = ['EMEF']
    parametros.save()
    
    ata_paa.paa.associacao.unidade.tipo_unidade = 'EMEF'
    ata_paa.paa.associacao.unidade.save()
    
    # Cria ação "Orçamento Grêmio Estudantil"
    acao_gremio = acao_factory.create(nome='Orçamento Grêmio Estudantil')
    acao_associacao_gremio = acao_associacao_factory.create(
        associacao=ata_paa.paa.associacao,
        acao=acao_gremio,
        status='ATIVA'
    )
    
    # Cria despesa completa no período do PAA
    periodo_paa = ata_paa.paa.periodo_paa
    despesa = despesa_factory.create(
        associacao=ata_paa.paa.associacao,
        data_transacao=periodo_paa.data_inicial + timedelta(days=1),
        status=STATUS_COMPLETO
    )
    
    # Cria rateio completo com a ação do grêmio
    rateio_despesa_factory.create(
        despesa=despesa,
        associacao=ata_paa.paa.associacao,
        acao_associacao=acao_associacao_gremio
    )
    
    serializer = AtaPaaSerializer(ata_paa)
    assert serializer.data['precisa_professor_gremio'] is True


def test_serializer_precisa_professor_gremio_false(ata_paa, parametros):
    """Testa se serializer retorna precisa_professor_gremio=False quando unidade não precisa"""
    parametros.tipos_unidades_professor_gremio = []
    parametros.save()
    
    serializer = AtaPaaSerializer(ata_paa)
    assert serializer.data['precisa_professor_gremio'] is False


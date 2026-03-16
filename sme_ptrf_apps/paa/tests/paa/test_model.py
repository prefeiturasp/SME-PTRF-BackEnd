import pytest
import datetime
from sme_ptrf_apps.paa.models import AtaPaa

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
def test_str_representation(paa):
    assert str(paa) == f"{paa.periodo_paa.referencia} - {paa.associacao}"


@pytest.mark.django_db
def test_paa_model_tem_campos_acoes_conclusao(paa_factory, periodo_paa_1):
    """Testa que o modelo PAA tem os campos ManyToMany para ações na conclusão"""
    paa = paa_factory.create(periodo_paa=periodo_paa_1)
    assert hasattr(paa, 'acoes_conclusao')
    assert hasattr(paa, 'acoes_pdde_conclusao')
    assert hasattr(paa, 'outros_recursos_periodo_conclusao')
    assert paa.acoes_conclusao.count() == 0
    assert paa.acoes_pdde_conclusao.count() == 0
    assert paa.outros_recursos_periodo_conclusao.count() == 0


@pytest.mark.django_db
def test_paa_model_propriedade_completa_com_historico_de_membros_habilitado(paa_factory, periodo_paa_1, ata_paa_factory, flag_factory, participante_ata_paa_factory):
    """Testa que a propriedade completa do modelo AtaPaa para o caso de flag historico-de-membros habilitada"""
    paa = paa_factory.create(periodo_paa=periodo_paa_1)

    flag_factory.create(name='historico-de-membros', everyone=True)
    
    ata_paa = ata_paa_factory.create(
        paa=paa,
        tipo_ata=AtaPaa.ATA_APRESENTACAO,
        tipo_reuniao=AtaPaa.REUNIAO_ORDINARIA,
        data_reuniao=datetime.datetime.now().date(),
        hora_reuniao="12:00",
        local_reuniao="Local teste",
        convocacao=AtaPaa.CONVOCACAO_PRIMEIRA,
        parecer_conselho=AtaPaa.PARECER_APROVADA,       
    )

    presidente = participante_ata_paa_factory.create(
        ata_paa=ata_paa,
        nome="Presidente Teste",
    )
    secretario = participante_ata_paa_factory.create(
        ata_paa=ata_paa,
        nome="Secretario Teste",
    )

    ata_paa.presidente_da_reuniao = presidente
    ata_paa.secretario_da_reuniao = secretario
    ata_paa.save()

    assert ata_paa.completa

@pytest.mark.django_db
def test_paa_model_propriedade_completa_com_historico_de_membros_desabilitado(paa_factory, periodo_paa_1, ata_paa_factory, flag_factory):
    """Testa que a propriedade completa do modelo AtaPaa para o caso de flag historico-de-membros desabilitado"""
    paa = paa_factory.create(periodo_paa=periodo_paa_1)

    flag_factory.create(name='historico-de-membros', everyone=False)
    
    ata_paa = ata_paa_factory.create(
        paa=paa,
        tipo_ata=AtaPaa.ATA_APRESENTACAO,
        tipo_reuniao=AtaPaa.REUNIAO_ORDINARIA,
        data_reuniao=datetime.datetime.now().date(),
        hora_reuniao="12:00",
        local_reuniao="Local teste",
        convocacao=AtaPaa.CONVOCACAO_PRIMEIRA,
        parecer_conselho=AtaPaa.PARECER_APROVADA,
        presidente_reuniao="PRESIDENTE TESTE",
        secretario_reuniao="SECRETARIO TESTE"
    )

    assert ata_paa.completa

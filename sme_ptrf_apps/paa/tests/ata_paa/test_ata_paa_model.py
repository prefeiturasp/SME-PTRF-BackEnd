import pytest

from sme_ptrf_apps.paa.models import AtaPaa, Paa
from sme_ptrf_apps.core.models import Parametros

pytestmark = pytest.mark.django_db


def test_instance_model(ata_paa):
    model = ata_paa
    assert isinstance(model, AtaPaa)
    assert isinstance(model.paa, Paa)
    assert model.tipo_ata
    assert model.tipo_reuniao
    assert model.convocacao
    assert model.status_geracao_pdf
    assert model.data_reuniao
    assert model.local_reuniao
    assert model.comentarios
    assert model.parecer_conselho
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.preenchida_em is None
    assert model.justificativa == ""
    assert model.hora_reuniao
    assert model.previa is False
    assert model.pdf_gerado_previamente is False


def test_completa_ata_aprovada_com_professor_gremio(ata_paa, participante_ata_paa_factory):
    """Testa se ata está completa com parecer APROVADA e professor do grêmio"""
    # Cria presidente e secretário
    presidente = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Presidente")
    secretario = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Secretário")
    
    # Cria professor do grêmio
    participante_ata_paa_factory.create(
        ata_paa=ata_paa,
        nome="Professor Grêmio",
        professor_gremio=True
    )
    
    ata_paa.presidente_da_reuniao = presidente
    ata_paa.secretario_da_reuniao = secretario
    ata_paa.parecer_conselho = AtaPaa.PARECER_APROVADA
    ata_paa.save()
    
    assert ata_paa.completa is True


def test_completa_ata_rejeitada_com_justificativa_e_professor_gremio(ata_paa, participante_ata_paa_factory):
    """Testa se ata está completa com parecer REJEITADA, justificativa e professor do grêmio"""
    # Cria presidente e secretário
    presidente = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Presidente")
    secretario = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Secretário")
    
    # Cria professor do grêmio
    participante_ata_paa_factory.create(
        ata_paa=ata_paa,
        nome="Professor Grêmio",
        professor_gremio=True
    )
    
    ata_paa.presidente_da_reuniao = presidente
    ata_paa.secretario_da_reuniao = secretario
    ata_paa.parecer_conselho = AtaPaa.PARECER_REJEITADA
    ata_paa.justificativa = "Justificativa de rejeição"
    ata_paa.save()
    
    assert ata_paa.completa is True


def test_completa_ata_incompleta_sem_presidente(ata_paa, participante_ata_paa_factory):
    """Testa se ata está incompleta sem presidente"""
    secretario = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Secretário")
    
    participante_ata_paa_factory.create(
        ata_paa=ata_paa,
        nome="Professor Grêmio",
        professor_gremio=True
    )
    
    ata_paa.secretario_da_reuniao = secretario
    ata_paa.presidente_da_reuniao = None
    ata_paa.save()
    
    assert ata_paa.completa is False


def test_completa_ata_incompleta_sem_secretario(ata_paa, participante_ata_paa_factory):
    """Testa se ata está incompleta sem secretário"""
    presidente = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Presidente")
    
    participante_ata_paa_factory.create(
        ata_paa=ata_paa,
        nome="Professor Grêmio",
        professor_gremio=True
    )
    
    ata_paa.presidente_da_reuniao = presidente
    ata_paa.secretario_da_reuniao = None
    ata_paa.save()
    
    assert ata_paa.completa is False


def test_completa_ata_rejeitada_sem_justificativa(ata_paa, participante_ata_paa_factory):
    """Testa se ata está incompleta quando rejeitada sem justificativa"""
    presidente = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Presidente")
    secretario = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Secretário")
    
    participante_ata_paa_factory.create(
        ata_paa=ata_paa,
        nome="Professor Grêmio",
        professor_gremio=True
    )
    
    ata_paa.presidente_da_reuniao = presidente
    ata_paa.secretario_da_reuniao = secretario
    ata_paa.parecer_conselho = AtaPaa.PARECER_REJEITADA
    ata_paa.justificativa = ""
    ata_paa.save()
    
    assert ata_paa.completa is False


def test_completa_ata_rejeitada_justificativa_vazia(ata_paa, participante_ata_paa_factory):
    """Testa se ata está incompleta quando rejeitada com justificativa apenas com espaços"""
    presidente = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Presidente")
    secretario = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Secretário")
    
    participante_ata_paa_factory.create(
        ata_paa=ata_paa,
        nome="Professor Grêmio",
        professor_gremio=True
    )
    
    ata_paa.presidente_da_reuniao = presidente
    ata_paa.secretario_da_reuniao = secretario
    ata_paa.parecer_conselho = AtaPaa.PARECER_REJEITADA
    ata_paa.justificativa = "   "
    ata_paa.save()
    
    assert ata_paa.completa is False


def test_completa_ata_sem_professor_gremio_quando_precisa(ata_paa, participante_ata_paa_factory, parametros):
    """Testa se ata está incompleta sem professor do grêmio quando unidade precisa"""
    parametros.tipos_unidades_professor_gremio = ['EMEF']
    parametros.save()
    
    ata_paa.paa.associacao.unidade.tipo_unidade = 'EMEF'
    ata_paa.paa.associacao.unidade.save()
    
    presidente = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Presidente")
    secretario = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Secretário")
    
    # Cria participante sem ser professor do grêmio
    participante_ata_paa_factory.create(
        ata_paa=ata_paa,
        nome="Participante Normal",
        professor_gremio=False
    )
    
    ata_paa.presidente_da_reuniao = presidente
    ata_paa.secretario_da_reuniao = secretario
    ata_paa.parecer_conselho = AtaPaa.PARECER_APROVADA
    ata_paa.save()
    
    assert ata_paa.completa is False


def test_unidade_precisa_professor_gremio_com_tipo_configurado(parametros):
    """Testa se unidade_precisa_professor_gremio retorna True quando tipo está configurado"""
    parametros.tipos_unidades_professor_gremio = ['EMEF', 'EMEI']
    parametros.save()
    
    assert AtaPaa.unidade_precisa_professor_gremio('EMEF') is True
    assert AtaPaa.unidade_precisa_professor_gremio('EMEI') is True
    assert AtaPaa.unidade_precisa_professor_gremio('CEU') is False


def test_unidade_precisa_professor_gremio_sem_configuracao(parametros):
    """Testa se unidade_precisa_professor_gremio retorna False quando não há configuração"""
    parametros.tipos_unidades_professor_gremio = []
    parametros.save()
    
    assert AtaPaa.unidade_precisa_professor_gremio('EMEF') is False


def test_precisa_professor_gremio_com_tipo_configurado(ata_paa, parametros):
    """Testa se precisa_professor_gremio retorna True quando tipo da unidade está configurado"""
    parametros.tipos_unidades_professor_gremio = ['EMEF']
    parametros.save()
    
    ata_paa.paa.associacao.unidade.tipo_unidade = 'EMEF'
    ata_paa.paa.associacao.unidade.save()
    
    assert ata_paa.precisa_professor_gremio is True


def test_precisa_professor_gremio_sem_tipo_configurado(ata_paa, parametros):
    """Testa se precisa_professor_gremio retorna False quando tipo da unidade não está configurado"""
    parametros.tipos_unidades_professor_gremio = ['EMEI']
    parametros.save()
    
    ata_paa.paa.associacao.unidade.tipo_unidade = 'EMEF'
    ata_paa.paa.associacao.unidade.save()
    
    assert ata_paa.precisa_professor_gremio is False


def test_precisa_professor_gremio_sem_associacao(ata_paa):
    """Testa se precisa_professor_gremio retorna False quando não há associação"""
    ata_paa.paa.associacao = None
    ata_paa.paa.save()
    
    assert ata_paa.precisa_professor_gremio is False


def test_completa_ata_aprovada_sem_professor_gremio_quando_nao_precisa(ata_paa, participante_ata_paa_factory, parametros):
    """Testa se ata está completa sem professor do grêmio quando unidade não precisa"""
    parametros.tipos_unidades_professor_gremio = []
    parametros.save()
    
    presidente = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Presidente")
    secretario = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Secretário")
    
    ata_paa.presidente_da_reuniao = presidente
    ata_paa.secretario_da_reuniao = secretario
    ata_paa.parecer_conselho = AtaPaa.PARECER_APROVADA
    ata_paa.save()
    
    assert ata_paa.completa is True


def test_completa_ata_aprovada_sem_professor_gremio_quando_precisa(ata_paa, participante_ata_paa_factory, parametros):
    """Testa se ata está incompleta sem professor do grêmio quando unidade precisa"""
    parametros.tipos_unidades_professor_gremio = ['EMEF']
    parametros.save()
    
    ata_paa.paa.associacao.unidade.tipo_unidade = 'EMEF'
    ata_paa.paa.associacao.unidade.save()
    
    presidente = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Presidente")
    secretario = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Secretário")
    
    ata_paa.presidente_da_reuniao = presidente
    ata_paa.secretario_da_reuniao = secretario
    ata_paa.parecer_conselho = AtaPaa.PARECER_APROVADA
    ata_paa.save()
    
    assert ata_paa.completa is False


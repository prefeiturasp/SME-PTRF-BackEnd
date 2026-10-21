import pytest

from sme_ptrf_apps.paa.models import AtaPaa, Paa
from sme_ptrf_apps.paa.services.ata_paa_service import unidade_precisa_professor_gremio

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


def test_completa_ata_aprovada_com_professor_gremio(ata_paa, participante_ata_paa_factory, flag_factory):
    """Testa se ata está completa com parecer APROVADA e professor do grêmio"""

    flag_factory.create(name='historico-de-membros', everyone=True)

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


def test_completa_ata_rejeitada_com_justificativa_e_professor_gremio(
        ata_paa, participante_ata_paa_factory, flag_factory):
    """Testa se ata está completa com parecer REJEITADA, justificativa e professor do grêmio"""

    flag_factory.create(name='historico-de-membros', everyone=True)

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


def test_completa_ata_incompleta_sem_presidente(ata_paa, participante_ata_paa_factory, flag_factory):
    """Testa se ata está incompleta sem presidente"""
    flag_factory.create(name='historico-de-membros', everyone=True)

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


def test_completa_ata_incompleta_sem_secretario(ata_paa, participante_ata_paa_factory, flag_factory):
    """Testa se ata está incompleta sem secretário"""
    flag_factory.create(name='historico-de-membros', everyone=True)

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


def test_completa_ata_rejeitada_sem_justificativa(ata_paa, participante_ata_paa_factory, flag_factory):
    """Testa se ata está incompleta quando rejeitada sem justificativa"""
    flag_factory.create(name='historico-de-membros', everyone=True)

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


def test_completa_ata_rejeitada_justificativa_vazia(ata_paa, participante_ata_paa_factory, flag_factory):
    """Testa se ata está incompleta quando rejeitada com justificativa apenas com espaços"""
    flag_factory.create(name='historico-de-membros', everyone=True)

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


def test_completa_ata_sem_professor_gremio_quando_precisa(
        ata_paa, participante_ata_paa_factory, parametros, flag_factory):
    """Testa se ata está completa sem professor do grêmio quando unidade precisa (professor não é obrigatório)"""
    flag_factory.create(name='historico-de-membros', everyone=True)

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

    # Professor do grêmio nunca é obrigatório, então a ata deve estar completa
    assert ata_paa.completa is True


def test_unidade_precisa_professor_gremio_com_tipo_configurado(parametros):
    """Testa se unidade_precisa_professor_gremio retorna True quando tipo está configurado"""
    parametros.tipos_unidades_professor_gremio = ['EMEF', 'EMEI']
    parametros.save()

    assert unidade_precisa_professor_gremio('EMEF') is True
    assert unidade_precisa_professor_gremio('EMEI') is True
    assert unidade_precisa_professor_gremio('CEU') is False


def test_unidade_precisa_professor_gremio_sem_configuracao(parametros):
    """Testa se unidade_precisa_professor_gremio retorna False quando não há configuração"""
    parametros.tipos_unidades_professor_gremio = []
    parametros.save()

    assert unidade_precisa_professor_gremio('EMEF') is False


def test_precisa_professor_gremio_com_tipo_configurado_sem_receitas_previstas(ata_paa, parametros, acao_factory,
                                                                               acao_associacao_factory,
                                                                               receita_prevista_paa_factory):
    """Testa se precisa_professor_gremio retorna False quando tipo está configurado mas não há receitas previstas"""
    parametros.tipos_unidades_professor_gremio = ['EMEF']
    parametros.save()

    ata_paa.paa.associacao.unidade.tipo_unidade = 'CIEJA'
    ata_paa.paa.associacao.unidade.save()

    acao_gremio = acao_factory.create(nome='Orçamento Grêmio Estudantil')
    acao_associacao_gremio = acao_associacao_factory.create(
        associacao=ata_paa.paa.associacao,
        acao=acao_gremio,
        status='ATIVA'
    )

    receita_prevista_paa_factory.create(paa=ata_paa.paa, acao_associacao=acao_associacao_gremio)
    assert ata_paa.precisa_professor_gremio is False


def test_precisa_professor_gremio_sem_tipo_configurado(ata_paa, parametros):
    """Testa se precisa_professor_gremio retorna False quando tipo da unidade não está configurado"""
    parametros.tipos_unidades_professor_gremio = ['EMEI']
    parametros.save()

    ata_paa.paa.associacao.unidade.tipo_unidade = 'EMEF'
    ata_paa.paa.associacao.unidade.save()

    assert ata_paa.precisa_professor_gremio is False


def test_precisa_professor_gremio_retorna_bool(ata_paa):
    """Testa se precisa_professor_gremio retorna um booleano"""
    assert isinstance(ata_paa.precisa_professor_gremio, bool)


def test_precisa_professor_gremio_sem_associacao(ata_paa):
    """Testa se precisa_professor_gremio retorna False quando não há associação"""
    ata_paa.paa.associacao = None
    ata_paa.paa.save()

    assert ata_paa.precisa_professor_gremio is False


def test_completa_ata_aprovada_sem_professor_gremio_quando_nao_precisa(
        ata_paa, participante_ata_paa_factory, parametros, flag_factory):
    """Testa se ata está completa sem professor do grêmio quando unidade não precisa"""
    flag_factory.create(name='historico-de-membros', everyone=True)

    parametros.tipos_unidades_professor_gremio = []
    parametros.save()

    presidente = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Presidente")
    secretario = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Secretário")

    ata_paa.presidente_da_reuniao = presidente
    ata_paa.secretario_da_reuniao = secretario
    ata_paa.parecer_conselho = AtaPaa.PARECER_APROVADA
    ata_paa.save()

    assert ata_paa.completa is True


def test_completa_ata_aprovada_sem_professor_gremio_quando_precisa(
        ata_paa, participante_ata_paa_factory, parametros,
        flag_factory, acao_factory, acao_associacao_factory):
    """Testa se ata está completa sem professor do grêmio quando unidade precisa (professor não é obrigatório)"""
    flag_factory.create(name='historico-de-membros', everyone=True)
    parametros.tipos_unidades_professor_gremio = ['EMEF']
    parametros.save()

    ata_paa.paa.associacao.unidade.tipo_unidade = 'EMEF'
    ata_paa.paa.associacao.unidade.save()

    # Cria ação "Orçamento Grêmio Estudantil"
    acao_gremio = acao_factory.create(nome='Orçamento Grêmio Estudantil')
    acao_associacao_factory.create(
        associacao=ata_paa.paa.associacao,
        acao=acao_gremio,
        status='ATIVA'
    )

    presidente = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Presidente")
    secretario = participante_ata_paa_factory.create(ata_paa=ata_paa, nome="Secretário")

    ata_paa.presidente_da_reuniao = presidente
    ata_paa.secretario_da_reuniao = secretario
    ata_paa.parecer_conselho = AtaPaa.PARECER_APROVADA
    ata_paa.save()

    # Professor do grêmio nunca é obrigatório, então a ata deve estar completa
    assert ata_paa.completa is True


def test_precisa_professor_gremio_com_acao_associacao_gremio_no_periodo(
        ata_paa, parametros, acao_factory, acao_associacao_factory, receita_prevista_paa_factory):
    """
        Testa se precisa_professor_gremio retorna True quando há receitas previstas com
        ação 'Orçamento Grêmio Estudantil' no período do PAA
    """
    parametros.tipos_unidades_professor_gremio = ['CIEJA']
    parametros.save()

    ata_paa.paa.associacao.unidade.tipo_unidade = 'CIEJA'
    ata_paa.paa.associacao.unidade.save()

    # Cria ação "Orçamento Grêmio Estudantil"
    acao_gremio = acao_factory.create(nome='Orçamento Grêmio Estudantil')
    acao_associacao_factory.create(
        associacao=ata_paa.paa.associacao,
        acao=acao_gremio,
        status='ATIVA'
    )

    assert ata_paa.precisa_professor_gremio is True


def test_precisa_professor_gremio_sem_acao_associacao_gremio_no_periodo(
        ata_paa, parametros, acao_factory, acao_associacao_factory):
    """
        Testa se precisa_professor_gremio retorna False quando não há receitas previstas com
        ação 'Orçamento Grêmio Estudantil' no período do PAA
    """
    parametros.tipos_unidades_professor_gremio = ['CIEJA']
    parametros.save()

    ata_paa.paa.associacao.unidade.tipo_unidade = 'CIEJA'
    ata_paa.paa.associacao.unidade.save()

    acao_factory.create(nome='Orçamento Grêmio Estudantil')

    assert ata_paa.precisa_professor_gremio is False


def test_precisa_professor_gremio_sem_acao_gremio(ata_paa, parametros):
    """Testa se precisa_professor_gremio retorna False quando não há ação 'Orçamento Grêmio Estudantil'"""
    parametros.tipos_unidades_professor_gremio = ['EMEF']
    parametros.save()

    ata_paa.paa.associacao.unidade.tipo_unidade = 'EMEF'
    ata_paa.paa.associacao.unidade.save()

    # Não cria ação "Orçamento Grêmio Estudantil"
    assert ata_paa.precisa_professor_gremio is False

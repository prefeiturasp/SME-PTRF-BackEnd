import pytest
import datetime
from sme_ptrf_apps.paa.models import AtaPaa, DocumentoPaa
from sme_ptrf_apps.paa.enums import PaaStatusEnum

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
def test_paa_model_propriedade_completa_com_historico_de_membros_habilitado(
        paa_factory, periodo_paa_1, ata_paa_factory, flag_factory,
        participante_ata_paa_factory):
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
def test_paa_model_propriedade_completa_com_historico_de_membros_desabilitado(
        paa_factory, periodo_paa_1, ata_paa_factory, flag_factory):
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


# ---------------------------------------------------------------------------
# Métodos de mutação de estado
# ---------------------------------------------------------------------------

def test_set_congelar_saldo_define_saldo_congelado_em(paa):
    assert paa.saldo_congelado_em is None
    paa.set_congelar_saldo()
    paa.refresh_from_db()
    assert paa.saldo_congelado_em is not None


def test_set_descongelar_saldo_limpa_saldo_congelado_em(paa_factory, periodo_paa_1):
    paa = paa_factory.create(periodo_paa=periodo_paa_1, saldo_congelado_em=datetime.datetime.now())
    paa.set_descongelar_saldo()
    paa.refresh_from_db()
    assert paa.saldo_congelado_em is None


def test_set_paa_status_em_retificacao(paa):
    paa.set_paa_status_em_retificacao()
    paa.refresh_from_db()
    assert paa.status == PaaStatusEnum.EM_RETIFICACAO.name


def test_set_paa_status_gerado(paa):
    paa.set_paa_status_gerado()
    paa.refresh_from_db()
    assert paa.status == PaaStatusEnum.GERADO.name


# ---------------------------------------------------------------------------
# Propriedades e métodos de leitura
# ---------------------------------------------------------------------------

def test_get_total_recursos_proprios_sem_recursos(paa):
    assert paa.get_total_recursos_proprios() == 0


def test_get_total_recursos_proprios_com_recursos(paa, recurso_proprio_paa_factory):
    recurso_proprio_paa_factory.create(paa=paa, valor=300)
    recurso_proprio_paa_factory.create(paa=paa, valor=200)
    assert paa.get_total_recursos_proprios() == 500


def test_tem_documentos_retorna_false_quando_sem_documentos(paa):
    assert paa.tem_documentos is False


def test_tem_documentos_retorna_true_quando_tem_documento_paa(paa, documento_paa_factory):
    documento_paa_factory.create(paa=paa)
    assert paa.tem_documentos is True


def test_tem_documentos_retorna_true_quando_tem_ata(paa, ata_paa_factory):
    ata_paa_factory.create(paa=paa)
    assert paa.tem_documentos is True


def test_get_condicao_status_andamento_retorna_string(paa):
    resultado = paa.get_condicao_status_andamento()
    assert isinstance(resultado, str)
    assert resultado.startswith('Condição')


def test_get_tem_documento_final_concluido_sem_documento(paa):
    assert paa.get_tem_documento_final_concluido() is False


def test_get_tem_documento_final_concluido_com_documento(paa, documento_paa_factory):
    documento_paa_factory.create(
        paa=paa,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        retificacao=False,
    )
    assert paa.get_tem_documento_final_concluido() is True


def test_get_tem_ata_concluida_sem_ata(paa):
    assert paa.get_tem_ata_concluida() is False


def test_get_tem_ata_concluida_com_ata_concluida(paa, ata_paa_factory):
    ata_paa_factory.create(paa=paa, status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO)
    assert paa.get_tem_ata_concluida() is True

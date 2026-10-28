from datetime import date

import pytest
from freezegun import freeze_time
from waffle.testutils import override_flag

from sme_ptrf_apps.paa.fixtures.factories.ata_paa_factory import AtaPaaFactory, ParticipanteAtaPaaFactory
from sme_ptrf_apps.paa.fixtures.factories.paa import PaaFactory
from sme_ptrf_apps.paa.models import AtaPaa, ParticipanteAtaPaa
from sme_ptrf_apps.paa.services.sincronizar_participante_ata_paa_service import (
    SincronizarParticipanteAtaPaaService,
)
from sme_ptrf_apps.mandatos.choices import CargoComposicaoVacanciaChoices as Cargos
from sme_ptrf_apps.mandatos.fixtures.factories.mandato_factory import MandatoFactory
from sme_ptrf_apps.mandatos.fixtures.factories.ocupante_cargo_factory import OcupanteCargoFactory
from sme_ptrf_apps.mandatos.models import CargoComposicaoVacancia
from sme_ptrf_apps.mandatos.services import ServicoHistoricoCargoComposicao

pytestmark = pytest.mark.django_db

# "Hoje" congelado após o fim do mandato, para nenhuma data do cenário ser considerada futura
DATA_CONGELADA = '2027-01-15'

CARGO = Cargos.CARGO_ASSOCIACAO_VOGAL_4
CARGO_LABEL = Cargos.CARGO_ASSOCIACAO_VOGAL_4.label
TESOUREIRO_LABEL = Cargos.CARGO_ASSOCIACAO_TESOUREIRO.label
INICIO_MANDATO = date(2026, 1, 1)
FIM_MANDATO = date(2026, 12, 31)


@pytest.fixture
def mandato_2026():
    return MandatoFactory(data_inicial=INICIO_MANDATO, data_final=FIM_MANDATO)


@pytest.fixture
def composicao_vacancia(mandato_2026, associacao_factory):
    associacao = associacao_factory.create()
    return ServicoHistoricoCargoComposicao.get_or_create_composicao_vacancia(
        associacao=associacao, mandato=mandato_2026
    )


@pytest.fixture
def ocupante():
    return OcupanteCargoFactory(nome='Pedro Silva', codigo_identificacao='1234567', cpf_responsavel='111.111.111-11')


def _registro(composicao_vacancia, inicio, fim, ocupante=None, cargo=CARGO):
    return CargoComposicaoVacancia.objects.create(
        composicao=composicao_vacancia,
        cargo_associacao=cargo,
        ocupante_do_cargo=ocupante,
        data_inicio_no_cargo=inicio,
        data_fim_no_cargo=fim,
    )


def _ata(associacao, data_reuniao, status=AtaPaa.STATUS_NAO_GERADO, com_membros=True):
    ata = AtaPaaFactory(paa=PaaFactory(associacao=associacao), data_reuniao=data_reuniao, status_geracao_pdf=status)
    if com_membros:
        ParticipanteAtaPaaFactory(ata_paa=ata, membro=True, cargo=CARGO_LABEL, nome='Antigo',
                                  identificacao='0000000', vago=False, presente=True)
        ParticipanteAtaPaaFactory(ata_paa=ata, membro=True, cargo=TESOUREIRO_LABEL, nome='Tesoureira',
                                  identificacao='7777777', presente=False)
    return ata


def _participante_do_cargo(ata):
    return ParticipanteAtaPaa.objects.get(ata_paa=ata, membro=True, cargo=CARGO_LABEL)


def _sincroniza(composicao_vacancia, inicio=INICIO_MANDATO, fim=FIM_MANDATO):
    SincronizarParticipanteAtaPaaService.sincroniza_participante_nas_atas_paa(
        composicao_vacancia=composicao_vacancia,
        cargo_associacao=CARGO,
        data_inicio=inicio,
        data_fim=fim,
    )


# --- Atualização do participante do cargo ---------------------------------------------

def test_cargo_ocupado_atualiza_participante_com_dados_do_ocupante(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, date(2026, 3, 1), FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))

    _sincroniza(composicao_vacancia)

    participante = _participante_do_cargo(ata)
    assert participante.nome == 'Pedro Silva'
    assert participante.identificacao == '1234567'
    assert participante.vago is False
    assert participante.presente is True
    assert participante.data_inicio_no_cargo == date(2026, 3, 1)


def test_cargo_vago_marca_participante_como_vago(composicao_vacancia):
    _registro(composicao_vacancia, date(2026, 4, 1), FIM_MANDATO)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))

    _sincroniza(composicao_vacancia)

    participante = _participante_do_cargo(ata)
    assert participante.nome == ''
    assert participante.identificacao == ''
    assert participante.vago is True
    assert participante.presente is False
    assert participante.data_inicio_no_cargo == date(2026, 4, 1)


def test_identificacao_usa_cpf_quando_ocupante_nao_tem_rf(composicao_vacancia):
    ocupante = OcupanteCargoFactory(codigo_identificacao='', cpf_responsavel='222.222.222-22')
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))

    _sincroniza(composicao_vacancia)

    assert _participante_do_cargo(ata).identificacao == '222.222.222-22'


def test_ocupante_sem_rf_e_sem_cpf_nao_quebra(composicao_vacancia):
    """Ocupante pode não ter RF nem CPF (identificação vazia é comum nas atas)."""
    ocupante = OcupanteCargoFactory(codigo_identificacao='', cpf_responsavel='')
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))

    _sincroniza(composicao_vacancia)

    participante = _participante_do_cargo(ata)
    assert participante.nome == ocupante.nome
    assert participante.identificacao == ''


def test_nao_altera_participantes_de_outros_cargos(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))

    _sincroniza(composicao_vacancia)

    tesoureira = ParticipanteAtaPaa.objects.get(ata_paa=ata, cargo=TESOUREIRO_LABEL)
    assert tesoureira.nome == 'Tesoureira'
    assert tesoureira.presente is False


def test_cria_participante_do_cargo_quando_ata_tem_membros_mas_nao_tem_o_cargo(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))
    _participante_do_cargo(ata).delete()

    _sincroniza(composicao_vacancia)

    assert _participante_do_cargo(ata).nome == 'Pedro Silva'


def test_sincronizar_duas_vezes_nao_duplica_participante(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))

    _sincroniza(composicao_vacancia)
    _sincroniza(composicao_vacancia)

    assert ParticipanteAtaPaa.objects.filter(ata_paa=ata, membro=True, cargo=CARGO_LABEL).count() == 1


def test_cada_ata_recebe_o_ocupante_vigente_na_data_da_reuniao(composicao_vacancia):
    pedro = OcupanteCargoFactory(nome='Pedro')
    maria = OcupanteCargoFactory(nome='Maria')
    _registro(composicao_vacancia, INICIO_MANDATO, date(2026, 6, 30), pedro)
    _registro(composicao_vacancia, date(2026, 7, 1), date(2026, 8, 31))
    _registro(composicao_vacancia, date(2026, 9, 1), FIM_MANDATO, maria)

    ata_pedro = _ata(composicao_vacancia.associacao, date(2026, 6, 30))
    ata_vago = _ata(composicao_vacancia.associacao, date(2026, 7, 1))
    ata_maria = _ata(composicao_vacancia.associacao, date(2026, 9, 1))

    _sincroniza(composicao_vacancia)

    assert _participante_do_cargo(ata_pedro).nome == 'Pedro'
    assert _participante_do_cargo(ata_vago).vago is True
    assert _participante_do_cargo(ata_maria).nome == 'Maria'


def test_ignora_registro_de_outro_cargo(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante, cargo=Cargos.CARGO_ASSOCIACAO_TESOUREIRO)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))

    _sincroniza(composicao_vacancia)

    assert _participante_do_cargo(ata).nome == 'Antigo'


# --- Presença e presidente/secretário da reunião ---------------------------------------

def _ocupante_igual_ao_participante(composicao_vacancia):
    """Registro cujo ocupante é a mesma pessoa já gravada no participante do cargo ('Antigo')."""
    antigo = OcupanteCargoFactory(nome='Antigo', codigo_identificacao='0000000')
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, antigo)


def test_mesmo_ocupante_mantem_ausencia_marcada_pelo_usuario(composicao_vacancia):
    _ocupante_igual_ao_participante(composicao_vacancia)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))
    ParticipanteAtaPaa.objects.filter(ata_paa=ata, cargo=CARGO_LABEL).update(presente=False)

    _sincroniza(composicao_vacancia)

    assert _participante_do_cargo(ata).presente is False


def test_mesmo_ocupante_mantem_presidente_e_secretario(composicao_vacancia):
    _ocupante_igual_ao_participante(composicao_vacancia)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))
    participante = _participante_do_cargo(ata)
    ata.presidente_da_reuniao = participante
    ata.secretario_da_reuniao = participante
    ata.save()

    _sincroniza(composicao_vacancia)

    ata.refresh_from_db()
    assert ata.presidente_da_reuniao == participante
    assert ata.secretario_da_reuniao == participante


def test_novo_ocupante_marca_como_presente(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))
    ParticipanteAtaPaa.objects.filter(ata_paa=ata, cargo=CARGO_LABEL).update(presente=False)

    _sincroniza(composicao_vacancia)

    assert _participante_do_cargo(ata).presente is True


@pytest.fixture(params=[None, 'historico-de-membros', 'historico-de-membros-v2'])
def flag_historico(request):
    """A limpeza de presidente/secretário independe das flags de histórico de membros."""
    if request.param is None:
        yield
        return
    with override_flag(request.param, active=True):
        yield


@pytest.mark.usefixtures('flag_historico')
def test_novo_ocupante_deixa_de_ser_presidente_e_secretario(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))
    participante = _participante_do_cargo(ata)
    ata.presidente_da_reuniao = participante
    ata.secretario_da_reuniao = participante
    ata.save()

    _sincroniza(composicao_vacancia)

    ata.refresh_from_db()
    assert ata.presidente_da_reuniao is None
    assert ata.secretario_da_reuniao is None


@pytest.mark.usefixtures('flag_historico')
def test_cargo_vago_deixa_de_ser_presidente(composicao_vacancia):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))
    ata.presidente_da_reuniao = _participante_do_cargo(ata)
    ata.save()

    _sincroniza(composicao_vacancia)

    ata.refresh_from_db()
    assert ata.presidente_da_reuniao is None


@pytest.mark.usefixtures('flag_historico')
def test_novo_ocupante_nao_altera_presidente_de_outro_cargo(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))
    tesoureira = ParticipanteAtaPaa.objects.get(ata_paa=ata, cargo=TESOUREIRO_LABEL)
    ata.presidente_da_reuniao = tesoureira
    ata.secretario_da_reuniao = _participante_do_cargo(ata)
    ata.save()

    _sincroniza(composicao_vacancia)

    ata.refresh_from_db()
    assert ata.presidente_da_reuniao == tesoureira
    assert ata.secretario_da_reuniao is None


@pytest.mark.usefixtures('flag_historico')
def test_novo_ocupante_limpa_fks_e_campos_textuais(composicao_vacancia, ocupante):
    """Ao salvar, a ata grava presidente/secretário nas FKs e em texto, com ou sem flag."""
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))
    participante = _participante_do_cargo(ata)
    ata.presidente_da_reuniao = participante
    ata.secretario_da_reuniao = participante
    ata.presidente_reuniao = 'Antigo'
    ata.cargo_presidente_reuniao = CARGO_LABEL.upper()
    ata.secretario_reuniao = 'Antigo'
    ata.cargo_secretaria_reuniao = CARGO_LABEL
    ata.save()

    _sincroniza(composicao_vacancia)

    ata.refresh_from_db()
    assert ata.presidente_da_reuniao is None
    assert ata.secretario_da_reuniao is None
    assert ata.presidente_reuniao == ''
    assert ata.cargo_presidente_reuniao == ''
    assert ata.secretario_reuniao == ''
    assert ata.cargo_secretaria_reuniao == ''


@pytest.mark.usefixtures('flag_historico')
def test_nao_limpa_campos_textuais_de_outro_cargo(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))
    ata.presidente_reuniao = 'Antigo'
    ata.cargo_presidente_reuniao = TESOUREIRO_LABEL
    ata.save()

    _sincroniza(composicao_vacancia)

    ata.refresh_from_db()
    assert ata.presidente_reuniao == 'Antigo'
    assert ata.cargo_presidente_reuniao == TESOUREIRO_LABEL


# --- Quais atas são sincronizadas -------------------------------------------------------

def test_limites_do_intervalo_sao_inclusivos(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata_inicio = _ata(composicao_vacancia.associacao, date(2026, 5, 1))
    ata_fim = _ata(composicao_vacancia.associacao, date(2026, 5, 31))

    _sincroniza(composicao_vacancia, inicio=date(2026, 5, 1), fim=date(2026, 5, 31))

    assert _participante_do_cargo(ata_inicio).nome == 'Pedro Silva'
    assert _participante_do_cargo(ata_fim).nome == 'Pedro Silva'


def test_nao_altera_atas_fora_do_intervalo(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata_antes = _ata(composicao_vacancia.associacao, date(2026, 4, 30))
    ata_depois = _ata(composicao_vacancia.associacao, date(2026, 6, 1))

    _sincroniza(composicao_vacancia, inicio=date(2026, 5, 1), fim=date(2026, 5, 31))

    assert _participante_do_cargo(ata_antes).nome == 'Antigo'
    assert _participante_do_cargo(ata_depois).nome == 'Antigo'


@pytest.mark.parametrize('status', [AtaPaa.STATUS_CONCLUIDO, AtaPaa.STATUS_EM_PROCESSAMENTO])
def test_nao_altera_ata_ja_gerada_ou_em_processamento(composicao_vacancia, ocupante, status):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10), status=status)

    _sincroniza(composicao_vacancia)

    assert _participante_do_cargo(ata).nome == 'Antigo'


def test_nao_altera_ata_de_outra_associacao(composicao_vacancia, ocupante, associacao_factory):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata_outra = _ata(associacao_factory.create(), date(2026, 5, 10))

    _sincroniza(composicao_vacancia)

    assert _participante_do_cargo(ata_outra).nome == 'Antigo'


def test_ignora_ata_sem_membros(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10), com_membros=False)
    ParticipanteAtaPaaFactory(ata_paa=ata, membro=False, nome='Convidado')

    _sincroniza(composicao_vacancia)

    assert not ParticipanteAtaPaa.objects.filter(ata_paa=ata, membro=True).exists()


def test_ignora_ata_sem_data_de_reuniao(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, None)

    _sincroniza(composicao_vacancia)

    assert _participante_do_cargo(ata).nome == 'Antigo'


def test_nao_altera_ata_quando_nao_ha_registro_do_cargo_na_data(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, date(2026, 6, 1), FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))

    _sincroniza(composicao_vacancia)

    assert _participante_do_cargo(ata).nome == 'Antigo'


# --- Remoção do ocupante da lista de não membros --------------------------------------

def test_remove_nao_membro_com_mesmo_rf_do_ocupante(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))
    ParticipanteAtaPaaFactory(ata_paa=ata, membro=False, identificacao='1234567', nome='PEDRO SILVA')
    outro = ParticipanteAtaPaaFactory(ata_paa=ata, membro=False, identificacao='9999999', nome='Convidado')

    _sincroniza(composicao_vacancia)

    nao_membros = ParticipanteAtaPaa.objects.filter(ata_paa=ata, membro=False)
    assert list(nao_membros) == [outro]


def test_remove_nao_membro_com_mesmo_cpf_do_ocupante(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))
    ParticipanteAtaPaaFactory(ata_paa=ata, membro=False, identificacao='111.111.111-11')

    _sincroniza(composicao_vacancia)

    assert not ParticipanteAtaPaa.objects.filter(ata_paa=ata, membro=False).exists()


def test_remove_nao_membro_com_mesmo_nome_do_ocupante(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))
    ParticipanteAtaPaaFactory(ata_paa=ata, membro=False, identificacao='5555555', nome='Pedro Silva')
    outro = ParticipanteAtaPaaFactory(ata_paa=ata, membro=False, identificacao='9999999', nome='Convidado')

    _sincroniza(composicao_vacancia)

    nao_membros = ParticipanteAtaPaa.objects.filter(ata_paa=ata, membro=False)
    assert list(nao_membros) == [outro]


def test_remove_nao_membro_pelo_nome_quando_ocupante_nao_tem_rf_nem_cpf(composicao_vacancia):
    ocupante = OcupanteCargoFactory(nome='Sem Doc', codigo_identificacao='', cpf_responsavel='')
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))
    ParticipanteAtaPaaFactory(ata_paa=ata, membro=False, identificacao='', nome='Sem Doc')

    _sincroniza(composicao_vacancia)

    assert not ParticipanteAtaPaa.objects.filter(ata_paa=ata, membro=False).exists()


def test_nao_remove_membro_de_outro_cargo_com_mesma_identificacao(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))
    ParticipanteAtaPaa.objects.filter(ata_paa=ata, cargo=TESOUREIRO_LABEL).update(identificacao='1234567')

    _sincroniza(composicao_vacancia)

    assert ParticipanteAtaPaa.objects.filter(ata_paa=ata, cargo=TESOUREIRO_LABEL).exists()


def test_cargo_vago_nao_remove_nao_membros(composicao_vacancia):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))
    convidado = ParticipanteAtaPaaFactory(ata_paa=ata, membro=False, identificacao='')

    _sincroniza(composicao_vacancia)

    assert ParticipanteAtaPaa.objects.filter(id=convidado.id).exists()


def test_transfere_presidente_e_secretario_do_nao_membro_removido_para_o_cargo(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))
    nao_membro = ParticipanteAtaPaaFactory(ata_paa=ata, membro=False, identificacao='1234567')
    ata.presidente_da_reuniao = nao_membro
    ata.secretario_da_reuniao = nao_membro
    ata.save()

    _sincroniza(composicao_vacancia)

    ata.refresh_from_db()
    participante = _participante_do_cargo(ata)
    assert ata.presidente_da_reuniao == participante
    assert ata.secretario_da_reuniao == participante


def test_mantem_presidente_quando_nao_era_o_nao_membro_removido(composicao_vacancia, ocupante):
    _registro(composicao_vacancia, INICIO_MANDATO, FIM_MANDATO, ocupante)
    ata = _ata(composicao_vacancia.associacao, date(2026, 5, 10))
    tesoureira = ParticipanteAtaPaa.objects.get(ata_paa=ata, cargo=TESOUREIRO_LABEL)
    ParticipanteAtaPaaFactory(ata_paa=ata, membro=False, identificacao='1234567')
    ata.presidente_da_reuniao = tesoureira
    ata.save()

    _sincroniza(composicao_vacancia)

    ata.refresh_from_db()
    assert ata.presidente_da_reuniao == tesoureira


# --- Integração com as ações do histórico de cargos ------------------------------------

@pytest.fixture
def ocupante_vigente(composicao_vacancia, ocupante):
    """Pedro ocupa o Vogal 4 desde o início do mandato."""
    return ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia,
        ocupante_do_cargo=ocupante,
        cargo_associacao=CARGO,
        data_entrada=INICIO_MANDATO,
    )


@freeze_time(DATA_CONGELADA)
def test_registrar_saida_deixa_vago_apenas_atas_a_partir_da_saida(composicao_vacancia, ocupante_vigente):
    ata_antes = _ata(composicao_vacancia.associacao, date(2026, 5, 9))
    ata_depois = _ata(composicao_vacancia.associacao, date(2026, 5, 10))

    ServicoHistoricoCargoComposicao.registrar_saida(ocupante_vigente, date(2026, 5, 10))

    assert _participante_do_cargo(ata_antes).nome == 'Antigo'
    participante = _participante_do_cargo(ata_depois)
    assert participante.vago is True
    assert participante.data_inicio_no_cargo == date(2026, 5, 10)


@freeze_time(DATA_CONGELADA)
def test_cancelar_saida_restaura_ocupante_nas_atas(composicao_vacancia, ocupante_vigente):
    ata = _ata(composicao_vacancia.associacao, date(2026, 6, 1))
    ServicoHistoricoCargoComposicao.registrar_saida(ocupante_vigente, date(2026, 5, 10))

    ServicoHistoricoCargoComposicao.cancelar_saida(ocupante_vigente)

    participante = _participante_do_cargo(ata)
    assert participante.nome == 'Pedro Silva'
    assert participante.vago is False
    assert participante.data_inicio_no_cargo == INICIO_MANDATO


@freeze_time(DATA_CONGELADA)
def test_corrigir_data_saida_para_depois_da_reuniao_restaura_ocupante(composicao_vacancia, ocupante_vigente):
    ata = _ata(composicao_vacancia.associacao, date(2026, 6, 1))
    ServicoHistoricoCargoComposicao.registrar_saida(ocupante_vigente, date(2026, 5, 10))
    ocupante_vigente.refresh_from_db()

    ServicoHistoricoCargoComposicao.corrigir_data_saida(ocupante_vigente, date(2026, 7, 1))

    assert _participante_do_cargo(ata).nome == 'Pedro Silva'


@freeze_time(DATA_CONGELADA)
def test_registrar_entrada_preenche_cargo_e_remove_ocupante_dos_nao_membros(composicao_vacancia):
    maria = OcupanteCargoFactory(nome='Maria', codigo_identificacao='7654321')
    ata = _ata(composicao_vacancia.associacao, date(2026, 6, 1))
    ParticipanteAtaPaaFactory(ata_paa=ata, membro=False, identificacao='7654321', nome='Maria')

    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia,
        ocupante_do_cargo=maria,
        cargo_associacao=CARGO,
        data_entrada=date(2026, 5, 1),
    )

    assert _participante_do_cargo(ata).nome == 'Maria'
    assert not ParticipanteAtaPaa.objects.filter(ata_paa=ata, membro=False).exists()


@freeze_time(DATA_CONGELADA)
def test_cancelar_entrada_restaura_vago_e_nao_altera_atas_anteriores(composicao_vacancia):
    maria = OcupanteCargoFactory(nome='Maria')
    ata_anterior = _ata(composicao_vacancia.associacao, date(2026, 3, 1))
    ata_posterior = _ata(composicao_vacancia.associacao, date(2026, 6, 1))
    registro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia,
        ocupante_do_cargo=maria,
        cargo_associacao=CARGO,
        data_entrada=date(2026, 5, 1),
    )

    ServicoHistoricoCargoComposicao.cancelar_entrada(registro)

    # ata anterior à entrada cancelada mantém o que o usuário preencheu
    assert _participante_do_cargo(ata_anterior).nome == 'Antigo'
    assert _participante_do_cargo(ata_posterior).vago is True

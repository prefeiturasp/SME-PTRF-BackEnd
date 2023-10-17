import pytest
from freezegun import freeze_time

from sme_ptrf_apps.mandatos.services import ServicoMandatoVigente, ServicoMandato

pytestmark = pytest.mark.django_db


@freeze_time('2023-08-08 13:59:00')
def test_servico_mandato_vigente(
    mandato_2023_a_2025_testes_servicos_01,
    mandato_2023_a_2025_testes_servicos_02,
    jwt_authenticated_client_sme,
    associacao
):
    servico_mandato_vigente = ServicoMandatoVigente()
    mandato_vigente = servico_mandato_vigente.get_mandato_vigente()

    assert mandato_vigente.referencia_mandato == '2023 a 2025'


def test_servico_mandato_mais_recente(
    mandato_2023_a_2025_testes_servicos_01,
    mandato_2026_a_2027_testes_servicos_03,
    jwt_authenticated_client_sme,
):
    servico_mandato = ServicoMandato()
    mandato_mais_recente = servico_mandato.get_mandato_mais_recente()

    assert mandato_mais_recente.referencia_mandato == '2026 a 2027'


def test_servico_mandato_mais_recente_sem_mandatos_existentes(
    jwt_authenticated_client_sme,
):
    servico_mandato = ServicoMandato()
    mandato_mais_recente = servico_mandato.get_mandato_mais_recente()

    assert mandato_mais_recente is None


def test_servico_mandato_anterior_ao_mais_recente(
    mandato_2023_a_2025_testes_servicos_01,
    mandato_2026_a_2027_testes_servicos_03,
    jwt_authenticated_client_sme,
):
    servico_mandato = ServicoMandato()
    mandato_anterior_ao_mais_recente = servico_mandato.get_mandato_anterior_ao_mais_recente()

    assert mandato_anterior_ao_mais_recente.referencia_mandato == '2023 a 2025'


def test_servico_mandato_anterior_ao_mais_recente_sem_mandatos_existentes(
    jwt_authenticated_client_sme,
):
    servico_mandato = ServicoMandato()
    mandato_anterior_ao_mais_recente = servico_mandato.get_mandato_anterior_ao_mais_recente()

    assert mandato_anterior_ao_mais_recente is None


def test_servico_mandato_anterior_ao_mais_recente_sem_mandatos_existentes_apenas_um_mandato_existente(
    jwt_authenticated_client_sme,
    mandato_2026_a_2027_testes_servicos_03,
):
    servico_mandato = ServicoMandato()
    mandato_anterior_ao_mais_recente = servico_mandato.get_mandato_anterior_ao_mais_recente()

    assert mandato_anterior_ao_mais_recente is None

import pytest
from freezegun import freeze_time
from datetime import date

from sme_ptrf_apps.mandatos.models import Composicao
from sme_ptrf_apps.mandatos.services import ServicoComposicaoVigente, ServicoCriaComposicaoVigenteDoMandato

pytestmark = pytest.mark.django_db


@freeze_time('2023-08-08 13:59:00')
def test_servico_composicao_vigente(
    mandato_2023_a_2025_testes_servicos_01,
    mandato_2023_a_2025_testes_servicos_02,
    composicao_01_2023_a_2025_testes_servicos,
    composicao_02_2023_a_2025_testes_servicos,
    jwt_authenticated_client_sme,
    associacao
):
    servico_composicao_vigente = ServicoComposicaoVigente(associacao=associacao, mandato=mandato_2023_a_2025_testes_servicos_01)
    composicao_vigente = servico_composicao_vigente.get_composicao_vigente()

    assert composicao_vigente.data_inicial == date(2023, 1, 1)


@freeze_time('2023-08-08 13:59:00')
def test_servico_cria_composicao_vigente_do_mandato(
    mandato_2023_a_2025_testes_servicos_01,
    jwt_authenticated_client_sme,
    associacao
):

    assert not Composicao.objects.filter(mandato=mandato_2023_a_2025_testes_servicos_01).exists()

    servico_cria_composicao_vigente = ServicoCriaComposicaoVigenteDoMandato(associacao=associacao, mandato=mandato_2023_a_2025_testes_servicos_01)
    composicao_vigente = servico_cria_composicao_vigente.cria_composicao_vigente()

    assert composicao_vigente.data_inicial == date(2023, 8, 8)

    assert Composicao.objects.filter(mandato=mandato_2023_a_2025_testes_servicos_01).exists()


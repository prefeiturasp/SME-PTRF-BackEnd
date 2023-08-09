import pytest
from freezegun import freeze_time

from sme_ptrf_apps.mandatos.services import ServicoMandatoVigente

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

import pytest

from sme_ptrf_apps.mandatos.services import ServicoCargosDaComposicao

pytestmark = pytest.mark.django_db


def test_servico_cargos_da_composicao(
    composicao_01_2023_a_2025_testes_servicos,
    cargo_composicao_01_testes_services,
    ocupante_cargo_01
):
    servico_cargos_da_composicao = ServicoCargosDaComposicao(composicao=composicao_01_2023_a_2025_testes_servicos)
    cargos_da_composicao = servico_cargos_da_composicao.get_cargos_da_composicao_ordenado_por_cargo_associacao()

    assert cargos_da_composicao['diretoria_executiva']
    assert cargos_da_composicao['conselho_fiscal']
    assert cargos_da_composicao['diretoria_executiva'][0]['ocupante_do_cargo']['nome'] == "Ollyver Ottoboni"



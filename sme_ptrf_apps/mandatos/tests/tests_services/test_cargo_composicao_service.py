import pytest

from sme_ptrf_apps.mandatos.services import ServicoCargosDaComposicao, ServicoCargosDaDiretoriaExecutiva, \
    ServicoPendenciaCargosDaComposicaoVigenteDaAssociacao

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


def test_servico_cargos_da_diretoria_executiva():
    servico_cargos_da_diretoria_executiva = ServicoCargosDaDiretoriaExecutiva()
    cargos_da_diretoria_executiva = servico_cargos_da_diretoria_executiva.get_cargos_diretoria_executiva()

    result = [
        {
            "id": "PRESIDENTE_DIRETORIA_EXECUTIVA",
            "nome": "Presidente da diretoria executiva"
        },
        {
            "id": "VICE_PRESIDENTE_DIRETORIA_EXECUTIVA",
            "nome": "Vice-Presidente da diretoria executiva"
        },
        {
            "id": "SECRETARIO",
            "nome": "Secretário"
        },
        {
            "id": "TESOUREIRO",
            "nome": "Tesoureiro"
        },
        {
            "id": "VOGAL_1",
            "nome": "Vogal 1"
        },
        {
            "id": "VOGAL_2",
            "nome": "Vogal 2"
        },
        {
            "id": "VOGAL_3",
            "nome": "Vogal 3"
        },
        {
            "id": "VOGAL_4",
            "nome": "Vogal 4"
        },
        {
            "id": "VOGAL_5",
            "nome": "Vogal 5"
        }
    ]

    assert result == cargos_da_diretoria_executiva


def test_pendencia_cargos_da_composicao_vigente_da_associacao(
    associacao,
    composicao_01_2023_a_2025_testes_servicos,
    cargo_composicao_01_testes_services,
    ocupante_cargo_01
):
    servico_pendencia = ServicoPendenciaCargosDaComposicaoVigenteDaAssociacao(associacao)
    pendencia_membros = servico_pendencia.retorna_se_tem_pendencia()

    assert pendencia_membros


def test_servico_cargos_da_composicao_retorna_tags_substituto_substituido__substituido(
    composicao_01_2023_a_2025_testes_tags,
    cargo_composicao_01_teste_tags,
    ocupante_cargo_01_teste_tags
):
    servico_cargos_da_composicao = ServicoCargosDaComposicao(composicao=composicao_01_2023_a_2025_testes_tags)
    cargos_da_composicao = servico_cargos_da_composicao.get_cargos_da_composicao_ordenado_por_cargo_associacao()

    assert cargos_da_composicao['diretoria_executiva'][0]['substituido']
    assert cargos_da_composicao['diretoria_executiva'][0]['tag_substituido'] == "Substituído em 31/12/2025"
    assert not cargos_da_composicao['diretoria_executiva'][0]['substituto']


def test_servico_cargos_da_composicao_retorna_tags_substituto_substituido__substituto(
    composicao_01_2023_a_2025_testes_tags,
    cargo_composicao_02_teste_tags,
    ocupante_cargo_02_teste_tags
):
    servico_cargos_da_composicao = ServicoCargosDaComposicao(composicao=composicao_01_2023_a_2025_testes_tags)
    cargos_da_composicao = servico_cargos_da_composicao.get_cargos_da_composicao_ordenado_por_cargo_associacao()

    assert not cargos_da_composicao['diretoria_executiva'][0]['substituido']
    assert cargos_da_composicao['diretoria_executiva'][0]['substituto']
    assert cargos_da_composicao['diretoria_executiva'][0]['tag_substituto'] == "Novo membro em 01/01/2024"

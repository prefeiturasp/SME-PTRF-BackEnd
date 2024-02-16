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
    servico_composicao_vigente = ServicoComposicaoVigente(associacao=associacao,
                                                          mandato=mandato_2023_a_2025_testes_servicos_01)
    composicao_vigente = servico_composicao_vigente.get_composicao_vigente()

    assert composicao_vigente.data_inicial == date(2023, 1, 1)


@freeze_time('2023-08-08 13:59:00')
def test_servico_cria_composicao_vigente_do_mandato(
    mandato_2023_a_2025_testes_servicos_01,
    jwt_authenticated_client_sme,
    associacao
):
    assert not Composicao.objects.filter(mandato=mandato_2023_a_2025_testes_servicos_01).exists()

    servico_cria_composicao_vigente = ServicoCriaComposicaoVigenteDoMandato(associacao=associacao,
                                                                            mandato=mandato_2023_a_2025_testes_servicos_01)
    composicao_vigente = servico_cria_composicao_vigente.cria_composicao_vigente()

    assert composicao_vigente.data_inicial == date(2023, 8, 8)

    assert Composicao.objects.filter(mandato=mandato_2023_a_2025_testes_servicos_01).exists()


@freeze_time('2024-02-06 13:59:00')
def test_servico_cria_nova_composicao_atraves_de_alteracao_membro_cria_nova_composicao(
    mandato_2023_a_2025_testes_service_data_saida_do_cargo,
    composicao_01_testes_service_data_saida_do_cargo,
    cargo_composicao_01_testes_service_data_saida_do_cargo,
    ocupante_cargo_01,
    jwt_authenticated_client_sme,
    associacao
):
    assert composicao_01_testes_service_data_saida_do_cargo.cargos_da_composicao_da_composicao.filter(
        ocupante_do_cargo=ocupante_cargo_01
    ).exists()

    assert Composicao.objects.filter(
        mandato=mandato_2023_a_2025_testes_service_data_saida_do_cargo,
        associacao=associacao
    ).count() == 1

    data_saida_do_cargo = '2023-01-10'

    servico_cria_composicao_vigente = ServicoCriaComposicaoVigenteDoMandato(
        associacao=associacao,
        mandato=mandato_2023_a_2025_testes_service_data_saida_do_cargo
    )

    servico_cria_composicao_vigente.cria_nova_composicao_atraves_de_alteracao_membro(
        data_fim_no_cargo=data_saida_do_cargo,
        cargo_composicao_sendo_editado=cargo_composicao_01_testes_service_data_saida_do_cargo
    )

    # Deve criar nova composição com a data posterior a data_saida_do_cargo
    assert Composicao.objects.filter(
        mandato=mandato_2023_a_2025_testes_service_data_saida_do_cargo,
        associacao=associacao
    ).count() == 2

    composicao_criada = Composicao.objects.filter(
        mandato=mandato_2023_a_2025_testes_service_data_saida_do_cargo,
        associacao=associacao,
        data_inicial=date(2023, 1, 11),
        data_final=date(2025, 12, 31)
    ).last()

    assert composicao_criada

    # Remove Cargo Composição da Nova Composição Criada
    assert not composicao_criada.cargos_da_composicao_da_composicao.filter(
        cargo_associacao=cargo_composicao_01_testes_service_data_saida_do_cargo
    ).exists()


@freeze_time('2024-02-06 13:59:00')
def test_servico_cria_nova_composicao_atraves_de_alteracao_membro_nao_cria_nova_composicao(
    mandato_2023_a_2025_testes_service_data_saida_do_cargo,
    composicao_02_testes_service_data_saida_do_cargo_nao_deve_criar_nova_composicao,
    composicao_03_testes_service_data_saida_do_cargo_nao_deve_criar_nova_composicao,
    cargo_composicao_02_testes_service_data_saida_do_cargo_nao_deve_criar_nova_composicao,
    ocupante_cargo_01,
    jwt_authenticated_client_sme,
    associacao
):
    assert composicao_03_testes_service_data_saida_do_cargo_nao_deve_criar_nova_composicao.cargos_da_composicao_da_composicao.filter(
        ocupante_do_cargo=ocupante_cargo_01
    ).exists()

    assert Composicao.objects.filter(
        mandato=mandato_2023_a_2025_testes_service_data_saida_do_cargo,
        associacao=associacao
    ).count() == 2

    data_saida_do_cargo = '2023-01-10'

    servico_cria_composicao_vigente = ServicoCriaComposicaoVigenteDoMandato(
        associacao=associacao,
        mandato=mandato_2023_a_2025_testes_service_data_saida_do_cargo
    )

    servico_cria_composicao_vigente.cria_nova_composicao_atraves_de_alteracao_membro(
        data_fim_no_cargo=data_saida_do_cargo,
        cargo_composicao_sendo_editado=cargo_composicao_02_testes_service_data_saida_do_cargo_nao_deve_criar_nova_composicao
    )

    # Não deve criar nova composição
    assert Composicao.objects.filter(
        mandato=mandato_2023_a_2025_testes_service_data_saida_do_cargo,
        associacao=associacao
    ).count() == 2

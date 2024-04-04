import pytest
from datetime import datetime, timedelta
from sme_ptrf_apps.mandatos.services import ServicoCargosDaComposicao, ServicoCargosDaDiretoriaExecutiva, \
    ServicoPendenciaCargosDaComposicaoVigenteDaAssociacao
from sme_ptrf_apps.mandatos.models.cargo_composicao import CargoComposicao

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


def test_servico_cargos_da_composicao_get_cargos_por_ocupante_e_mandato(
    mandato_factory,
    composicao_factory,
    cargo_composicao_factory,
    ocupante_cargo_factory
):
    mandato_2024 = mandato_factory.create(data_inicial=datetime(2024, 1, 1), data_final=datetime(2024, 12, 31))
    composicao_1 = composicao_factory.create(
        mandato=mandato_2024, data_inicial=mandato_2024.data_inicial, data_final=mandato_2024.data_inicial + timedelta(days=30))
    composicao_2 = composicao_factory.create(
        mandato=mandato_2024, data_inicial=mandato_2024.data_inicial + timedelta(days=31), data_final=mandato_2024.data_inicial + timedelta(days=60))
    composicao_3 = composicao_factory.create(
        mandato=mandato_2024, data_inicial=mandato_2024.data_inicial + timedelta(days=61), data_final=mandato_2024.data_inicial + timedelta(days=90))
    composicao_4 = composicao_factory.create(
        mandato=mandato_2024, data_inicial=mandato_2024.data_inicial + timedelta(days=91), data_final=mandato_2024.data_inicial + timedelta(days=120))

    presidente_executiva = ocupante_cargo_factory.create()

    cargo_1 = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao_1.data_inicial,
        data_fim_no_cargo=composicao_1.data_final,
        composicao=composicao_1,
        ocupante_do_cargo=presidente_executiva,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    )
    cargo_2 = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao_2.data_inicial,
        data_fim_no_cargo=composicao_2.data_final,
        composicao=composicao_2,
        ocupante_do_cargo=presidente_executiva,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    )
    cargo_3 = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao_3.data_inicial,
        data_fim_no_cargo=composicao_3.data_final,
        composicao=composicao_3,
        ocupante_do_cargo=presidente_executiva,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    )
    cargo_4 = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao_4.data_inicial,
        data_fim_no_cargo=composicao_4.data_final,
        composicao=composicao_4,
        ocupante_do_cargo=presidente_executiva,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    )

    servico_cargos_da_composicao = ServicoCargosDaComposicao(composicao=composicao_1)
    cargos = servico_cargos_da_composicao.get_cargos_por_ocupante_e_mandato(cargo_1)

    assert list(cargos.values_list('id', flat=True)) == [cargo_1.id, cargo_2.id, cargo_3.id, cargo_4.id]
    assert cargos.count() == 4


def test_servico_cargos_da_composicao_get_data_fim_no_cargo_composicao_mais_recente(
    mandato_factory,
    composicao_factory,
    cargo_composicao_factory,
    ocupante_cargo_factory
):
    mandato_2024 = mandato_factory.create(data_inicial=datetime.now(
    ) - timedelta(days=91), data_final=datetime.now() + timedelta(days=365))

    finaliza_apos_30_dias = mandato_2024.data_inicial + timedelta(days=30)
    finaliza_apos_60_dias = mandato_2024.data_inicial + timedelta(days=60)
    finaliza_apos_90_dias = mandato_2024.data_inicial + timedelta(days=90)

    composicao_1 = composicao_factory.create(
        mandato=mandato_2024, data_inicial=mandato_2024.data_inicial, data_final=finaliza_apos_30_dias)
    composicao_2 = composicao_factory.create(
        mandato=mandato_2024, data_inicial=finaliza_apos_30_dias + timedelta(days=1), data_final=finaliza_apos_60_dias)
    composicao_3 = composicao_factory.create(
        mandato=mandato_2024, data_inicial=finaliza_apos_60_dias + timedelta(days=1), data_final=finaliza_apos_90_dias)
    composicao_4 = composicao_factory.create(
        mandato=mandato_2024, data_inicial=finaliza_apos_90_dias + timedelta(days=1), data_final=mandato_2024.data_final)

    presidente_executiva = ocupante_cargo_factory.create()

    cargo_1 = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao_1.data_inicial,
        data_fim_no_cargo=composicao_1.data_final,
        composicao=composicao_1,
        ocupante_do_cargo=presidente_executiva,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    )

    cargo_2 = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao_2.data_inicial,
        data_fim_no_cargo=composicao_2.data_final,
        composicao=composicao_2,
        ocupante_do_cargo=presidente_executiva,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    )
    cargo_3 = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao_3.data_inicial,
        data_fim_no_cargo=composicao_3.data_final,
        composicao=composicao_3,
        ocupante_do_cargo=presidente_executiva,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    )

    servico_cargos_da_composicao = ServicoCargosDaComposicao(composicao=composicao_1)
    data_fim = servico_cargos_da_composicao.get_data_fim_no_cargo_composicao_mais_recente(cargo_1)
    assert data_fim == composicao_3.data_final.strftime("%Y-%m-%d")

    servico_cargos_da_composicao = ServicoCargosDaComposicao(composicao=composicao_2)
    data_fim = servico_cargos_da_composicao.get_data_fim_no_cargo_composicao_mais_recente(cargo_2)
    assert data_fim == composicao_3.data_final.strftime("%Y-%m-%d")

    servico_cargos_da_composicao = ServicoCargosDaComposicao(composicao=composicao_3)
    data_fim = servico_cargos_da_composicao.get_data_fim_no_cargo_composicao_mais_recente(cargo_3)
    assert data_fim == composicao_3.data_final.strftime("%Y-%m-%d")

    cargo_4_vigente = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao_4.data_inicial,
        data_fim_no_cargo=composicao_4.data_final,
        composicao=composicao_4,
        ocupante_do_cargo=presidente_executiva,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    )

    servico_cargos_da_composicao = ServicoCargosDaComposicao(composicao=composicao_4)
    data_fim = servico_cargos_da_composicao.get_data_fim_no_cargo_composicao_mais_recente(cargo_4_vigente)
    assert data_fim == None

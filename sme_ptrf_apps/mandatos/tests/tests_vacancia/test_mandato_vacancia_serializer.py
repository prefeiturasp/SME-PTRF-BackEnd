from datetime import date

import pytest
from freezegun import freeze_time

from sme_ptrf_apps.mandatos.api.serializers.mandato_vacancia_serializer import (
    CustomError, MandatoVacanciaSerializer,
)
from sme_ptrf_apps.mandatos.fixtures.factories.mandato_factory import MandatoFactory
from sme_ptrf_apps.mandatos.models import CargoComposicaoVacancia, ComposicaoVacancia, Mandato

pytestmark = pytest.mark.django_db


@pytest.fixture
def associacao_teste(associacao_factory):
    return associacao_factory.create()


# get_editavel

@freeze_time('2026-06-15')
def test_get_editavel_true_para_mandato_vigente():
    mandato = MandatoFactory(data_inicial=date(2026, 1, 1), data_final=date(2026, 12, 31))
    assert MandatoVacanciaSerializer(mandato).data['editavel'] is True


@freeze_time('2026-06-15')
def test_get_editavel_true_para_mandato_futuro():
    mandato = MandatoFactory(data_inicial=date(2027, 1, 1), data_final=date(2027, 12, 31))
    assert MandatoVacanciaSerializer(mandato).data['editavel'] is True


@freeze_time('2026-06-15')
def test_get_editavel_false_para_mandato_encerrado():
    mandato = MandatoFactory(data_inicial=date(2024, 1, 1), data_final=date(2024, 12, 31))
    assert MandatoVacanciaSerializer(mandato).data['editavel'] is False


# get_data_inicial_proximo_mandato

def test_get_data_inicial_proximo_mandato_para_o_mais_recente():
    mandato = MandatoFactory(data_inicial=date(2026, 1, 1), data_final=date(2026, 12, 31))
    data = MandatoVacanciaSerializer(mandato).data
    # SerializerMethodField retorna o valor bruto do getter, sem passar por um DateField
    assert data['data_inicial_proximo_mandato'] == date(2027, 1, 1)


def test_get_data_inicial_proximo_mandato_none_quando_nao_e_o_mais_recente():
    mais_antigo = MandatoFactory(data_inicial=date(2020, 1, 1), data_final=date(2022, 12, 31))
    MandatoFactory(data_inicial=date(2023, 1, 1), data_final=date(2025, 12, 31))

    data = MandatoVacanciaSerializer(mais_antigo).data
    assert data['data_inicial_proximo_mandato'] is None


# get_data_final_mandato_anterior_ao_mais_recente

def test_get_data_final_mandato_anterior_ao_mais_recente_quando_existe():
    MandatoFactory(data_inicial=date(2020, 1, 1), data_final=date(2022, 12, 31))
    mais_recente = MandatoFactory(data_inicial=date(2023, 1, 1), data_final=date(2025, 12, 31))

    data = MandatoVacanciaSerializer(mais_recente).data
    assert data['data_final_mandato_anterior_ao_mais_recente'] == date(2023, 1, 1)


def test_get_data_final_mandato_anterior_ao_mais_recente_none_quando_so_existe_um_mandato():
    unico = MandatoFactory(data_inicial=date(2026, 1, 1), data_final=date(2026, 12, 31))

    data = MandatoVacanciaSerializer(unico).data
    assert data['data_final_mandato_anterior_ao_mais_recente'] is None


# get_limite_min_data_inicial

def test_get_limite_min_data_inicial_quando_existe_mandato_anterior():
    MandatoFactory(data_inicial=date(2020, 1, 1), data_final=date(2022, 12, 31))
    atual = MandatoFactory(data_inicial=date(2023, 1, 1), data_final=date(2025, 12, 31))

    data = MandatoVacanciaSerializer(atual).data
    assert data['limite_min_data_inicial'] == date(2023, 1, 1)


def test_get_limite_min_data_inicial_none_quando_nao_ha_mandato_anterior():
    unico = MandatoFactory(data_inicial=date(2026, 1, 1), data_final=date(2026, 12, 31))

    data = MandatoVacanciaSerializer(unico).data
    assert data['limite_min_data_inicial'] is None


# validate() - criação

def test_validate_bloqueia_criacao_com_data_inicial_anterior_ou_igual_ao_fim_do_mandato_mais_recente():
    MandatoFactory(data_inicial=date(2023, 1, 1), data_final=date(2025, 12, 31))

    payload = {
        'referencia_mandato': '2025 a 2027',
        'data_inicial': '2025-06-01',
        'data_final': '2027-12-31',
    }
    serializer = MandatoVacanciaSerializer(data=payload)

    with pytest.raises(CustomError) as exc_info:
        serializer.is_valid()

    assert 'deve ser maior que a data final do mandato anterior' in str(exc_info.value.detail)


def test_validate_bloqueia_data_final_menor_que_data_inicial():
    payload = {
        'referencia_mandato': 'referencia invalida',
        'data_inicial': '2030-01-01',
        'data_final': '2029-12-31',
    }
    serializer = MandatoVacanciaSerializer(data=payload)

    with pytest.raises(CustomError) as exc_info:
        serializer.is_valid()

    assert 'não pode ser menor que a data inicial' in str(exc_info.value.detail)


def test_validate_bloqueia_data_inicial_dentro_de_outro_mandato_ja_cadastrado():
    """ Cenário só possível com dados inconsistentes no banco: tanto o validate() do
    serializer quanto o clean() do model impedem, em uso normal, cadastrar mandatos
    sobrepostos - usa bulk_create (não passa por clean()) para exercitar a checagem
    isoladamente. """
    Mandato.objects.bulk_create([
        Mandato(referencia_mandato='2020 a 2035', data_inicial=date(2020, 1, 1), data_final=date(2035, 12, 31)),
        Mandato(referencia_mandato='2021', data_inicial=date(2021, 1, 1), data_final=date(2021, 12, 31)),
    ])

    payload = {
        'referencia_mandato': '2025 a 2026',
        'data_inicial': '2025-06-01',
        'data_final': '2026-12-31',
    }
    serializer = MandatoVacanciaSerializer(data=payload)

    with pytest.raises(CustomError) as exc_info:
        serializer.is_valid()

    assert 'vigência de outro mandato cadastrado' in str(exc_info.value.detail)


# validate() - edição (incompatibilidade com cargos já lançados)

def test_validate_bloqueia_edicao_da_data_final_incompativel_com_cargo_ja_lancado(associacao_teste):
    mandato = MandatoFactory(data_inicial=date(2026, 1, 1), data_final=date(2026, 12, 31))
    composicao = ComposicaoVacancia.objects.create(associacao=associacao_teste, mandato=mandato)
    CargoComposicaoVacancia.objects.create(
        composicao=composicao,
        ocupante_do_cargo=None,
        cargo_associacao='VOGAL_1',
        data_inicio_no_cargo=date(2026, 6, 1),
        data_fim_no_cargo=date(2026, 12, 31),
    )

    payload = {
        'referencia_mandato': mandato.referencia_mandato,
        'data_inicial': mandato.data_inicial.isoformat(),
        'data_final': '2026-05-01',
    }
    serializer = MandatoVacanciaSerializer(instance=mandato, data=payload, partial=True)

    with pytest.raises(CustomError) as exc_info:
        serializer.is_valid()

    assert 'editar a data final do mandato' in str(exc_info.value.detail)


def test_validate_bloqueia_edicao_da_data_inicial_incompativel_com_cargo_ja_lancado(associacao_teste):
    mandato = MandatoFactory(data_inicial=date(2026, 1, 1), data_final=date(2026, 12, 31))
    composicao = ComposicaoVacancia.objects.create(associacao=associacao_teste, mandato=mandato)
    CargoComposicaoVacancia.objects.create(
        composicao=composicao,
        ocupante_do_cargo=None,
        cargo_associacao='VOGAL_1',
        data_inicio_no_cargo=date(2026, 1, 1),
        data_fim_no_cargo=date(2026, 6, 30),
    )

    payload = {
        'referencia_mandato': mandato.referencia_mandato,
        'data_inicial': '2026-07-01',
        'data_final': mandato.data_final.isoformat(),
    }
    serializer = MandatoVacanciaSerializer(instance=mandato, data=payload, partial=True)

    with pytest.raises(CustomError) as exc_info:
        serializer.is_valid()

    assert 'editar a data inicial do mandato' in str(exc_info.value.detail)


# validate() - edição (sobreposição com outro mandato)

def test_validate_bloqueia_edicao_com_data_inicial_dentro_de_outro_mandato():
    mandato = MandatoFactory(data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))
    outro = MandatoFactory(data_inicial=date(2030, 1, 1), data_final=date(2030, 6, 30))

    payload = {
        'referencia_mandato': mandato.referencia_mandato,
        'data_inicial': '2030-03-01',
        'data_final': '2030-12-31',
    }
    serializer = MandatoVacanciaSerializer(instance=mandato, data=payload, partial=True)

    with pytest.raises(CustomError) as exc_info:
        serializer.is_valid()

    assert 'vigência de outro mandato cadastrado' in str(exc_info.value.detail)
    assert outro.uuid  # sanity: o outro mandato existe e é o motivo do bloqueio


def test_validate_bloqueia_edicao_com_periodo_que_engloba_outro_mandato():
    mandato = MandatoFactory(data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))
    MandatoFactory(data_inicial=date(2030, 3, 1), data_final=date(2030, 3, 10))

    payload = {
        'referencia_mandato': mandato.referencia_mandato,
        'data_inicial': '2030-01-01',
        'data_final': '2030-12-31',
    }
    serializer = MandatoVacanciaSerializer(instance=mandato, data=payload, partial=True)

    with pytest.raises(CustomError) as exc_info:
        serializer.is_valid()

    assert 'se sobrepõem com outros mandatos já cadastrados' in str(exc_info.value.detail)


# update() - propagação de datas para os cargos já lançados

def test_update_propaga_nova_data_inicial_para_registros_que_acompanhavam_o_inicio_do_mandato(associacao_teste):
    mandato = MandatoFactory(data_inicial=date(2026, 1, 1), data_final=date(2026, 12, 31))
    composicao = ComposicaoVacancia.objects.create(associacao=associacao_teste, mandato=mandato)
    cargo = CargoComposicaoVacancia.objects.create(
        composicao=composicao,
        ocupante_do_cargo=None,
        cargo_associacao='VOGAL_1',
        data_inicio_no_cargo=mandato.data_inicial,
        data_fim_no_cargo=mandato.data_final,
    )

    serializer = MandatoVacanciaSerializer(instance=mandato)
    nova_data_inicial = date(2026, 2, 1)
    serializer.update(mandato, {
        'referencia_mandato': mandato.referencia_mandato,
        'data_inicial': nova_data_inicial,
        'data_final': mandato.data_final,
    })

    mandato.refresh_from_db()
    cargo.refresh_from_db()
    assert mandato.data_inicial == nova_data_inicial
    assert cargo.data_inicio_no_cargo == nova_data_inicial


def test_update_nao_propaga_data_inicial_para_registro_que_nao_acompanhava_o_inicio_do_mandato(associacao_teste):
    mandato = MandatoFactory(data_inicial=date(2026, 1, 1), data_final=date(2026, 12, 31))
    composicao = ComposicaoVacancia.objects.create(associacao=associacao_teste, mandato=mandato)
    data_inicio_historica = date(2026, 3, 1)
    cargo_encerrado = CargoComposicaoVacancia.objects.create(
        composicao=composicao,
        ocupante_do_cargo=None,
        cargo_associacao='VOGAL_1',
        data_inicio_no_cargo=data_inicio_historica,
        data_fim_no_cargo=date(2026, 6, 30),
    )

    serializer = MandatoVacanciaSerializer(instance=mandato)
    serializer.update(mandato, {
        'referencia_mandato': mandato.referencia_mandato,
        'data_inicial': date(2026, 2, 1),
        'data_final': mandato.data_final,
    })

    cargo_encerrado.refresh_from_db()
    assert cargo_encerrado.data_inicio_no_cargo == data_inicio_historica


def test_update_propaga_nova_data_final_para_registros_que_acompanhavam_o_fim_do_mandato(associacao_teste):
    mandato = MandatoFactory(data_inicial=date(2026, 1, 1), data_final=date(2026, 12, 31))
    composicao = ComposicaoVacancia.objects.create(associacao=associacao_teste, mandato=mandato)
    cargo_vigente = CargoComposicaoVacancia.objects.create(
        composicao=composicao,
        ocupante_do_cargo=None,
        cargo_associacao='VOGAL_1',
        data_inicio_no_cargo=mandato.data_inicial,
        data_fim_no_cargo=mandato.data_final,
    )

    serializer = MandatoVacanciaSerializer(instance=mandato)
    nova_data_final = date(2027, 1, 31)
    serializer.update(mandato, {
        'referencia_mandato': mandato.referencia_mandato,
        'data_inicial': mandato.data_inicial,
        'data_final': nova_data_final,
    })

    mandato.refresh_from_db()
    cargo_vigente.refresh_from_db()
    assert mandato.data_final == nova_data_final
    assert cargo_vigente.data_fim_no_cargo == nova_data_final


def test_update_nao_propaga_data_final_para_registro_encerrado_antes_do_fim_do_mandato(associacao_teste):
    mandato = MandatoFactory(data_inicial=date(2026, 1, 1), data_final=date(2026, 12, 31))
    composicao = ComposicaoVacancia.objects.create(associacao=associacao_teste, mandato=mandato)
    data_fim_historica = date(2026, 6, 30)
    cargo_encerrado = CargoComposicaoVacancia.objects.create(
        composicao=composicao,
        ocupante_do_cargo=None,
        cargo_associacao='VOGAL_1',
        data_inicio_no_cargo=mandato.data_inicial,
        data_fim_no_cargo=data_fim_historica,
    )

    serializer = MandatoVacanciaSerializer(instance=mandato)
    serializer.update(mandato, {
        'referencia_mandato': mandato.referencia_mandato,
        'data_inicial': mandato.data_inicial,
        'data_final': date(2027, 1, 31),
    })

    cargo_encerrado.refresh_from_db()
    assert cargo_encerrado.data_fim_no_cargo == data_fim_historica

from datetime import date

import pytest
from django.db import IntegrityError

from sme_ptrf_apps.mandatos.models import ComposicaoVacancia, CargoComposicaoVacancia
from sme_ptrf_apps.mandatos.choices import CargoComposicaoVacanciaChoices as Cargo
from sme_ptrf_apps.mandatos.fixtures.factories.mandato_factory import MandatoFactory
from sme_ptrf_apps.mandatos.fixtures.factories.ocupante_cargo_factory import OcupanteCargoFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def mandato_2026():
    return MandatoFactory(data_inicial=date(2026, 1, 1), data_final=date(2026, 12, 31))


@pytest.fixture
def associacao_teste(associacao_factory):
    return associacao_factory.create()


@pytest.fixture
def composicao_vacancia(mandato_2026, associacao_teste):
    return ComposicaoVacancia.objects.create(
        associacao=associacao_teste,
        mandato=mandato_2026,
    )


def _cargo_composicao_vacancia(composicao, **kwargs):
    """Cria um CargoComposicaoVacancia direto (sem passar pelo service), pra isolar o
    teste de model da lógica de negócio de ServicoHistoricoCargoComposicao."""
    defaults = {
        'composicao': composicao,
        'cargo_associacao': Cargo.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        'data_inicio_no_cargo': date(2026, 1, 1),
        'data_fim_no_cargo': date(2026, 12, 31),
    }
    defaults.update(kwargs)
    return CargoComposicaoVacancia.objects.create(**defaults)


# ComposicaoVacancia

def test_composicao_vacancia_str_combina_associacao_e_mandato(composicao_vacancia):
    """__str__ inclui o nome da associação e a referência do mandato."""
    texto = str(composicao_vacancia)

    assert composicao_vacancia.associacao.nome in texto
    assert composicao_vacancia.mandato.referencia_mandato in texto


def test_composicao_vacancia_unique_constraint_associacao_mandato(mandato_2026, associacao_teste):
    """Não pode existir 2 ComposicaoVacancia para a mesma associação+mandato."""
    ComposicaoVacancia.objects.create(associacao=associacao_teste, mandato=mandato_2026)

    with pytest.raises(IntegrityError):
        ComposicaoVacancia.objects.create(associacao=associacao_teste, mandato=mandato_2026)


def test_composicao_vacancia_permite_mesma_associacao_em_mandatos_diferentes(associacao_teste):
    """A unicidade é pelo par (associacao, mandato) — mandatos diferentes não colidem."""
    mandato_a = MandatoFactory(data_inicial=date(2020, 1, 1), data_final=date(2021, 12, 31))
    mandato_b = MandatoFactory(data_inicial=date(2022, 1, 1), data_final=date(2023, 12, 31))

    composicao_a = ComposicaoVacancia.objects.create(associacao=associacao_teste, mandato=mandato_a)
    composicao_b = ComposicaoVacancia.objects.create(associacao=associacao_teste, mandato=mandato_b)

    assert composicao_a.id != composicao_b.id


# CargoComposicaoVacancia

def test_cargo_composicao_vacancia_str_retorna_cargo_associacao(composicao_vacancia):
    """__str__ retorna o valor bruto de cargo_associacao."""
    cargo = _cargo_composicao_vacancia(composicao_vacancia, ocupante_do_cargo=OcupanteCargoFactory())

    assert str(cargo) == Cargo.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA


def test_cargo_composicao_vacancia_ocupante_nulo_representa_vago(composicao_vacancia):
    """ocupante_do_cargo=None é uma vacância válida (null=True no model)."""
    cargo = _cargo_composicao_vacancia(composicao_vacancia, ocupante_do_cargo=None)

    assert cargo.ocupante_do_cargo is None


def test_substituido_false_quando_substituido_por_nao_preenchido(composicao_vacancia):
    """substituido é False enquanto substituido_por não aponta pra nada."""
    cargo = _cargo_composicao_vacancia(composicao_vacancia, ocupante_do_cargo=OcupanteCargoFactory())

    assert cargo.substituido is False


def test_substituido_true_quando_substituido_por_preenchido(composicao_vacancia):
    """substituido vira True assim que substituido_por é preenchido — sem escrita
    adicional, é a fonte única de verdade."""
    anterior = _cargo_composicao_vacancia(
        composicao_vacancia, ocupante_do_cargo=OcupanteCargoFactory(), data_fim_no_cargo=date(2026, 1, 31),
    )
    posterior = _cargo_composicao_vacancia(
        composicao_vacancia, ocupante_do_cargo=OcupanteCargoFactory(), data_inicio_no_cargo=date(2026, 2, 1),
    )
    anterior.substituido_por = posterior
    anterior.save()

    assert anterior.substituido is True


def test_substituto_false_quando_ninguem_aponta_para_o_registro(composicao_vacancia):
    """substituto é False quando nenhum outro registro tem substituido_por
    apontando pra este (relação reversa substitui vazia)."""
    cargo = _cargo_composicao_vacancia(composicao_vacancia, ocupante_do_cargo=OcupanteCargoFactory())

    assert cargo.substituto is False


def test_substituto_true_quando_algum_registro_aponta_para_ele(composicao_vacancia):
    """substituto vira True quando outro registro liga substituido_por pra este,
    via self.substitui.exists()."""
    anterior = _cargo_composicao_vacancia(
        composicao_vacancia, ocupante_do_cargo=OcupanteCargoFactory(), data_fim_no_cargo=date(2026, 1, 31),
    )
    posterior = _cargo_composicao_vacancia(
        composicao_vacancia, ocupante_do_cargo=OcupanteCargoFactory(), data_inicio_no_cargo=date(2026, 2, 1),
    )
    anterior.substituido_por = posterior
    anterior.save()

    assert posterior.substituto is True


def test_substituto_false_quando_vinculo_existe_mas_datas_nao_sao_adjacentes(composicao_vacancia):
    """substituto valida a adjacência real de datas, não só a existência do vínculo —
    cobre o caso de um mesmo ocupante passar várias vezes pelo mesmo cargo/mandato,
    onde o vínculo poderia acabar apontando pra um registro sem gap zero entre eles."""
    anterior = _cargo_composicao_vacancia(
        composicao_vacancia, ocupante_do_cargo=OcupanteCargoFactory(), data_fim_no_cargo=date(2026, 1, 31),
    )
    posterior = _cargo_composicao_vacancia(
        composicao_vacancia, ocupante_do_cargo=OcupanteCargoFactory(), data_inicio_no_cargo=date(2026, 3, 1),
    )
    anterior.substituido_por = posterior
    anterior.save()

    assert posterior.substituto is False


@pytest.mark.parametrize('cargo_associacao, ordem_esperada', [
    (Cargo.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA, 1),
    (Cargo.CARGO_ASSOCIACAO_VICE_PRESIDENTE_DIRETORIA_EXECUTIVA, 2),
    (Cargo.CARGO_ASSOCIACAO_SECRETARIO, 3),
    (Cargo.CARGO_ASSOCIACAO_TESOUREIRO, 4),
    (Cargo.CARGO_ASSOCIACAO_VOGAL_1, 5),
    (Cargo.CARGO_ASSOCIACAO_VOGAL_5, 9),
    (Cargo.CARGO_ASSOCIACAO_PRESIDENTE_CONSELHO_FISCAL, 10),
    (Cargo.CARGO_ASSOCIACAO_CONSELHEIRO_1, 11),
    (Cargo.CARGO_ASSOCIACAO_CONSELHEIRO_4, 14),
])
def test_ordenar_por_cargo_retorna_a_posicao_esperada(cargo_associacao, ordem_esperada):
    """ordenar_por_cargo mapeia cada cargo (pelo label) pra sua posição de exibição."""
    participante = {'cargo': cargo_associacao.label}

    assert CargoComposicaoVacancia.ordenar_por_cargo(participante) == ordem_esperada


def test_ordenar_por_cargo_retorna_99_para_cargo_desconhecido():
    """Cargo fora do mapa (rótulo não reconhecido) cai no fallback 99."""
    participante = {'cargo': 'Cargo Que Não Existe'}

    assert CargoComposicaoVacancia.ordenar_por_cargo(participante) == 99

""" Testes da cascade/validação da v2 (ComposicaoVacancia/CargoComposicaoVacancia) quando
a data inicial ou final de um Mandato é editada - 8.10. """
from datetime import date

import pytest
from freezegun import freeze_time
from waffle.testutils import override_flag

from sme_ptrf_apps.mandatos.api.serializers.mandato_serializer import CustomError, MandatoSerializer
from sme_ptrf_apps.mandatos.models import CargoComposicao, CargoComposicaoVacancia
from sme_ptrf_apps.mandatos.services import ServicoHistoricoCargoComposicao
from sme_ptrf_apps.mandatos.fixtures.factories.mandato_factory import MandatoFactory
from sme_ptrf_apps.mandatos.fixtures.factories.ocupante_cargo_factory import OcupanteCargoFactory

pytestmark = pytest.mark.django_db

DATA_CONGELADA = '2027-01-15'
FLAG = 'historico-de-membros-v2'


@pytest.fixture
def mandato_2026():
    return MandatoFactory(data_inicial=date(2026, 1, 1), data_final=date(2026, 12, 31))


@pytest.fixture
def associacao_teste(associacao_factory):
    return associacao_factory.create()


@pytest.fixture
def composicao_vacancia(mandato_2026, associacao_teste):
    return ServicoHistoricoCargoComposicao.get_or_create_composicao_vacancia(
        associacao=associacao_teste, mandato=mandato_2026
    )


def _ocupante(nome):
    return OcupanteCargoFactory(nome=nome)


# att_data_fim_composicao_vacancia

@freeze_time(DATA_CONGELADA)
def test_att_data_fim_composicao_vacancia_atualiza_so_quem_esta_vigente(mandato_2026, composicao_vacancia):
    """Registros vigentes (ocupado e vago) acompanham a nova data_final; um registro
    encerrado no meio do mandato mantém sua data histórica real intacta."""
    pedro = _ocupante('Pedro')
    joao = _ocupante('João')

    registro_pedro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )  # fica vigente

    registro_joao = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia,
        ocupante_do_cargo=joao,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro_joao, data_saida=date(2026, 3, 1))
    # registro_joao encerrado (fim real = 2026-02-28), gera vaga aberta vigente pro tesoureiro

    mandato_2026.att_data_fim_composicao_vacancia(data_final_antiga=date(2026, 12, 31), nova_data=date(2027, 6, 30))

    registro_pedro.refresh_from_db()
    registro_joao.refresh_from_db()
    vaga_tesoureiro = CargoComposicaoVacancia.objects.get(
        composicao=composicao_vacancia,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO,
        ocupante_do_cargo__isnull=True,
    )

    assert registro_pedro.data_fim_no_cargo == date(2027, 6, 30)  # vigente, acompanhou
    assert registro_joao.data_fim_no_cargo == date(2026, 2, 28)  # encerrado, intocado
    assert vaga_tesoureiro.data_fim_no_cargo == date(2027, 6, 30)  # vaga vigente, acompanhou


# att_data_inicio_composicao_vacancia

@freeze_time(DATA_CONGELADA)
def test_att_data_inicio_composicao_vacancia_atualiza_so_quem_comecou_com_o_mandato(
    mandato_2026, composicao_vacancia
):
    """Só quem começou junto com a data_inicial antiga do mandato (incluindo um vago
    implícito materializado) acompanha a nova data; quem entrou no meio do mandato
    mantém a data real."""
    pedro = _ocupante('Pedro')
    maria = _ocupante('Maria')

    registro_pedro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),  # fundador
    )
    registro_maria = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia,
        ocupante_do_cargo=maria,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO,
        data_entrada=date(2026, 3, 1),  # entrou no meio do mandato - materializa vago antes
    )

    mandato_2026.att_data_inicio_composicao_vacancia(data_inicial_antiga=date(2026, 1, 1), nova_data=date(2026, 1, 15))

    registro_pedro.refresh_from_db()
    registro_maria.refresh_from_db()
    vaga_tesoureiro = CargoComposicaoVacancia.objects.get(
        composicao=composicao_vacancia,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO,
        ocupante_do_cargo__isnull=True,
    )

    assert registro_pedro.data_inicio_no_cargo == date(2026, 1, 15)  # fundador, acompanhou
    assert registro_maria.data_inicio_no_cargo == date(2026, 3, 1)  # meio do mandato, intocado
    assert vaga_tesoureiro.data_inicio_no_cargo == date(2026, 1, 15)  # vago fundador, acompanhou


# possui_cargo_vacancia_incompativel_com_nova_data_final

@freeze_time(DATA_CONGELADA)
def test_incompativel_com_nova_data_final_bloqueia_saida_historica_fora_do_novo_fim(
    mandato_2026, composicao_vacancia
):
    """Encolher data_final pra antes de uma saída já registrada (fato histórico real) é
    incompatível."""
    pedro = _ocupante('Pedro')

    registro_pedro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro_pedro, data_saida=date(2026, 6, 1))
    # saída real em 2026-05-31

    assert mandato_2026.possui_cargo_vacancia_incompativel_com_nova_data_final(date(2026, 3, 1)) is True
    assert mandato_2026.possui_cargo_vacancia_incompativel_com_nova_data_final(date(2026, 12, 31)) is False


@freeze_time(DATA_CONGELADA)
def test_incompativel_com_nova_data_final_bloqueia_entrada_apos_o_novo_fim(mandato_2026, composicao_vacancia):
    """Encolher data_final pra antes da entrada de alguém (mesmo vigente) é incompatível -
    o cascade não pode mover a entrada de ninguém, só a saída (sentinela)."""
    luis = _ocupante('Luis')

    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia,
        ocupante_do_cargo=luis,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO,
        data_entrada=date(2026, 9, 1),
    )

    assert mandato_2026.possui_cargo_vacancia_incompativel_com_nova_data_final(date(2026, 8, 1)) is True
    assert mandato_2026.possui_cargo_vacancia_incompativel_com_nova_data_final(date(2026, 10, 1)) is False


# possui_cargo_vacancia_incompativel_com_nova_data_inicial

@freeze_time(DATA_CONGELADA)
def test_incompativel_com_nova_data_inicial_bloqueia_entrada_anterior_ao_novo_inicio(
    mandato_2026, composicao_vacancia
):
    """Adiar data_inicial pra depois de uma entrada já registrada é incompatível, mesmo
    quando não é o registro fundador (que o cascade ajustaria automaticamente)."""
    pedro = _ocupante('Pedro')

    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 3, 1),  # não é o dia 1 do mandato
    )

    assert mandato_2026.possui_cargo_vacancia_incompativel_com_nova_data_inicial(date(2026, 4, 1)) is True
    assert mandato_2026.possui_cargo_vacancia_incompativel_com_nova_data_inicial(date(2026, 2, 1)) is False


@freeze_time(DATA_CONGELADA)
def test_incompativel_com_nova_data_inicial_bloqueia_fundador_ja_encerrado(mandato_2026, composicao_vacancia):
    """Um fundador (começou junto com o mandato, seria ajustado pelo cascade) que já saiu
    antes da nova data inicial deixaria início > fim - precisa ser bloqueado, não ajustado."""
    pedro = _ocupante('Pedro')

    registro_pedro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),  # fundador
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro_pedro, data_saida=date(2026, 1, 20))
    # saída real em 2026-01-19

    assert mandato_2026.possui_cargo_vacancia_incompativel_com_nova_data_inicial(date(2026, 2, 1)) is True
    assert mandato_2026.possui_cargo_vacancia_incompativel_com_nova_data_inicial(date(2026, 1, 10)) is False


# Integração via MandatoSerializer (validate + update)

@freeze_time(DATA_CONGELADA)
def test_mandato_serializer_bloqueia_edicao_incompativel_com_v2(mandato_2026, composicao_vacancia, flag_factory):
    """validate() barra a edição da data final quando a v2 tem um registro incompatível."""
    flag_factory.create(name=FLAG, everyone=True)
    pedro = _ocupante('Pedro')

    registro_pedro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro_pedro, data_saida=date(2026, 6, 1))

    serializer = MandatoSerializer(
        instance=mandato_2026,
        data={
            'referencia_mandato': mandato_2026.referencia_mandato,
            'data_inicial': mandato_2026.data_inicial,
            'data_final': date(2026, 3, 1),  # antes da saída real do Pedro (05-31)
        },
    )

    with pytest.raises(CustomError):
        serializer.is_valid()


@freeze_time(DATA_CONGELADA)
def test_mandato_serializer_permite_edicao_compativel_e_aplica_cascade_v2(
    mandato_2026, composicao_vacancia, flag_factory
):
    """update() aplica a cascade v2 quando a edição é compatível e a flag está ativa."""
    flag_factory.create(name=FLAG, everyone=True)
    pedro = _ocupante('Pedro')

    registro_pedro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )

    serializer = MandatoSerializer(
        instance=mandato_2026,
        data={
            'referencia_mandato': mandato_2026.referencia_mandato,
            'data_inicial': mandato_2026.data_inicial,
            'data_final': date(2027, 6, 30),  # estende - sempre compatível
        },
    )

    assert serializer.is_valid(), serializer.errors
    serializer.save()

    registro_pedro.refresh_from_db()
    mandato_2026.refresh_from_db()

    assert mandato_2026.data_final == date(2027, 6, 30)
    assert registro_pedro.data_fim_no_cargo == date(2027, 6, 30)


@freeze_time(DATA_CONGELADA)
@override_flag(FLAG, active=False)
def test_mandato_serializer_nao_aplica_cascade_v2_com_flag_desligada(
    mandato_2026, composicao_vacancia
):
    """Com a flag v2 desligada, update() não deve tocar em CargoComposicaoVacancia, mesmo que
    existam registros - só a v1 (att_..._composicoes_e_cargos_composicoes) roda. O próprio
    `mandato.data_final` muda de qualquer forma (isso não é condicionado à flag).

    Usa @override_flag(..., active=False) em vez de simplesmente não criar a flag: o cache do
    waffle (LocMemCache) não é limpo entre testes pelo pytest-django, então um teste anterior
    que ative essa mesma flag via flag_factory deixaria um valor "ativo" preso no cache.
    """
    pedro = _ocupante('Pedro')

    registro_pedro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )

    serializer = MandatoSerializer(
        instance=mandato_2026,
        data={
            'referencia_mandato': mandato_2026.referencia_mandato,
            'data_inicial': mandato_2026.data_inicial,
            'data_final': date(2027, 6, 30),
        },
    )

    assert serializer.is_valid(), serializer.errors
    serializer.save()

    registro_pedro.refresh_from_db()
    mandato_2026.refresh_from_db()

    assert mandato_2026.data_final == date(2027, 6, 30)  # mandato muda independente da flag
    assert registro_pedro.data_fim_no_cargo == date(2026, 12, 31)  # v2 intocada, flag desligada

from datetime import date

import pytest
from freezegun import freeze_time

from sme_ptrf_apps.mandatos.services import ServicoHistoricoCargoComposicao
from sme_ptrf_apps.mandatos.models import CargoComposicaoVacancia, CargoComposicao
from sme_ptrf_apps.mandatos.exceptions import CargoComposicaoVacanciaValidationError
from sme_ptrf_apps.mandatos.services.validators.validators import ValidatorSemGapNaTimelineDoCargo
from sme_ptrf_apps.mandatos.fixtures.factories.mandato_factory import MandatoFactory
from sme_ptrf_apps.mandatos.fixtures.factories.ocupante_cargo_factory import OcupanteCargoFactory

pytestmark = pytest.mark.django_db

# "Hoje" congelado após o fim do mandato de teste (2026-12-31), pra nenhuma data
# do cenário (01/2026 a 12/2026) nunca ser considerada futura (que comparam
# contra date.today()) - independente de quando o teste realmente rodar.
DATA_CONGELADA = '2027-01-15'


@pytest.fixture
def mandato_2026():
    return MandatoFactory(data_inicial=date(2026, 1, 1), data_final=date(2026, 12, 31))


@pytest.fixture
def composicao_vacancia_2026(mandato_2026, associacao_factory):
    associacao = associacao_factory.create()
    return ServicoHistoricoCargoComposicao.get_or_create_composicao_vacancia(
        associacao=associacao, mandato=mandato_2026
    )


def _ocupante(nome):
    return OcupanteCargoFactory(nome=nome)


@freeze_time(DATA_CONGELADA)
def test_registrar_entrada_primeiro_ocupante_do_cargo_sem_predecessor(composicao_vacancia_2026):
    """Primeira entrada de um cargo (sem nenhum registro anterior) não deve quebrar."""
    pedro = _ocupante('Pedro')

    registro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )

    assert registro.data_fim_no_cargo == composicao_vacancia_2026.mandato.data_final
    assert registro.substituido is False
    assert registro.substituto is False


@freeze_time(DATA_CONGELADA)
def test_registrar_entrada_materializa_vago_implicito_antes_da_primeira_entrada(composicao_vacancia_2026):
    """Primeira entrada de um cargo, 10 dias após o início do mandato, deve materializar
    um registro vago cobrindo esses 10 dias - antes só existia a ausência de registro."""
    pedro = _ocupante('Pedro')
    mandato = composicao_vacancia_2026.mandato

    registro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 11),
    )

    vago = CargoComposicaoVacancia.objects.get(
        composicao=composicao_vacancia_2026,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        ocupante_do_cargo__isnull=True,
    )

    assert vago.data_inicio_no_cargo == mandato.data_inicial
    assert vago.data_fim_no_cargo == date(2026, 1, 10)  # dia anterior à entrada
    assert registro.data_inicio_no_cargo == date(2026, 1, 11)

    timeline = ServicoHistoricoCargoComposicao.get_timeline_do_cargo(
        composicao_vacancia_2026, CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    )
    assert len(timeline) == 2
    assert timeline[0]['id'] == vago.id
    assert timeline[1]['id'] == registro.id


@freeze_time(DATA_CONGELADA)
def test_registrar_entrada_no_dia_inicial_do_mandato_nao_materializa_vago(composicao_vacancia_2026):
    """Entrada exatamente no dia 1 do mandato não deixa nenhum dia pra representar como vago -
    não deve criar registro vazio."""
    pedro = _ocupante('Pedro')

    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),  # == mandato.data_inicial
    )

    total_registros = CargoComposicaoVacancia.objects.filter(
        composicao=composicao_vacancia_2026,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
    ).count()

    assert total_registros == 1  # só o registro do ocupante, nenhum vago


@freeze_time(DATA_CONGELADA)
def test_cenario_completo_substituicao_direta_mesmo_dia(composicao_vacancia_2026):
    """Pedro sai e Luis entra no mesmo dia: D-1 aplicado, substituido_por ligado e
    nenhuma vacância aberta sobra no banco"""
    pedro = _ocupante('Pedro')
    luis = _ocupante('Luis')

    registro_pedro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )

    ServicoHistoricoCargoComposicao.registrar_saida(registro_pedro, data_saida=date(2026, 2, 1))

    registro_luis = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=luis,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 2, 1),
    )

    registro_pedro.refresh_from_db()

    assert registro_pedro.data_fim_no_cargo == date(2026, 1, 31)  # D-1
    assert registro_pedro.substituido is True
    assert registro_pedro.substituido_por_id == registro_luis.id
    assert registro_luis.substituto is True

    # a vacância transitória não deixou rastro
    assert not CargoComposicaoVacancia.objects.filter(
        composicao=composicao_vacancia_2026,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        ocupante_do_cargo__isnull=True,
    ).exists()


@freeze_time(DATA_CONGELADA)
def test_cenario_completo_gap_entre_dois_ocupantes(composicao_vacancia_2026):
    """João sai e ninguém assume de imediato: cargo fica vago até Maria entrar meses
    depois - sem ligação de substituido_por, gap real identificado por get_ocupante_em_data."""
    joao = _ocupante('João')
    maria = _ocupante('Maria')

    registro_joao = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=joao,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_3,
        data_entrada=date(2026, 1, 1),
    )

    ServicoHistoricoCargoComposicao.registrar_saida(registro_joao, data_saida=date(2026, 6, 1))

    registro_joao.refresh_from_db()
    assert registro_joao.data_fim_no_cargo == date(2026, 5, 31)
    assert registro_joao.substituido is False

    # cargo vago em 15/07 - ninguém entrou ainda
    vago = ServicoHistoricoCargoComposicao.get_ocupante_em_data(
        composicao_vacancia_2026, CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_3, date(2026, 7, 15)
    )
    assert vago is not None
    assert vago.ocupante_do_cargo_id is None

    registro_maria = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=maria,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_3,
        data_entrada=date(2026, 9, 1),
    )

    registro_joao.refresh_from_db()
    assert registro_joao.substituido_por is None  # gap real, não é substituição direta
    assert registro_maria.substituto is False

    ocupante_em_15_07 = ServicoHistoricoCargoComposicao.get_ocupante_em_data(
        composicao_vacancia_2026, CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_3, date(2026, 7, 15)
    )
    assert ocupante_em_15_07.ocupante_do_cargo_id is None  # continua vago pra essa data


@freeze_time(DATA_CONGELADA)
def test_get_datas_de_alteracao_da_composicao_retorna_marcos_ordenados(composicao_vacancia_2026):
    """Entrada + saída geram 2 marcos distintos, retornados em ordem cronológica."""
    pedro = _ocupante('Pedro')

    registro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro, data_saida=date(2026, 2, 1))

    datas = ServicoHistoricoCargoComposicao.get_datas_de_alteracao_da_composicao(composicao_vacancia_2026)

    assert datas == [
        (date(2026, 1, 1), date(2026, 1, 31)),
        (date(2026, 2, 1), date(2026, 12, 31)),
    ]


def test_get_datas_de_alteracao_da_composicao_sem_nenhum_registro_retorna_lista_vazia(composicao_vacancia_2026):
    """Composição recém-criada, sem nenhum cargo preenchido: não há marco a montar."""
    datas = ServicoHistoricoCargoComposicao.get_datas_de_alteracao_da_composicao(composicao_vacancia_2026)

    assert datas == []


@freeze_time(DATA_CONGELADA)
def test_get_datas_de_alteracao_da_composicao_mescla_intervalos_sobrepostos_de_cargos_diferentes(
        composicao_vacancia_2026):
    """Cargos diferentes têm vigências independentes que se sobrepõem - os marcos precisam
    ser os cortes cronológicos únicos entre elas, não os pares (início, fim) de cada
    registro isolado."""
    presidente = _ocupante('Pedro')
    tesoureiro_antigo = _ocupante('Luis')
    tesoureiro_novo = _ocupante('Ana')

    # Presidente: um único registro cobrindo o mandato inteiro (01/01 a 31/12)
    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=presidente,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )

    # Tesoureiro: troca no meio do mandato (01/01 a 31/07, depois 01/08 a 31/12) -
    # o corte de 01/08 não existe no registro do presidente.
    registro_tesoureiro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=tesoureiro_antigo,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro_tesoureiro, data_saida=date(2026, 8, 1))
    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=tesoureiro_novo,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO,
        data_entrada=date(2026, 8, 1),
    )

    datas = ServicoHistoricoCargoComposicao.get_datas_de_alteracao_da_composicao(composicao_vacancia_2026)

    assert datas == [
        (date(2026, 1, 1), date(2026, 7, 31)),
        (date(2026, 8, 1), date(2026, 12, 31)),
    ]


@freeze_time('2026-06-15')
def test_registrar_saida_rejeita_data_saida_futura_em_relacao_a_data_informada(composicao_vacancia_2026):
    """ precisa validar a data INFORMADA (data_saida), não a já deslocada
    por D-N (data_fim) - senão uma saída pra amanhã passaria despercebida como 'hoje'."""
    pedro = _ocupante('Pedro')

    registro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )

    with pytest.raises(CargoComposicaoVacanciaValidationError):  # noqa
        ServicoHistoricoCargoComposicao.registrar_saida(registro, data_saida=date(2026, 6, 16))  # amanhã


@freeze_time('2026-06-15')
def test_registrar_saida_rejeita_data_posterior_ao_final_do_mandato(composicao_vacancia_2026):
    """ precisa comparar a data INFORMADA contra mandato.data_final, não a
    já deslocada por D-N (que, deslocada, poderia mascarar uma data além do mandato)."""
    pedro = _ocupante('Pedro')

    registro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )

    data_final_mandato = composicao_vacancia_2026.mandato.data_final  # 31/12/2026
    with pytest.raises(CargoComposicaoVacanciaValidationError):  # noqa
        ServicoHistoricoCargoComposicao.registrar_saida(
            registro, data_saida=date(2027, 1, 1)  # 1 dia além do fim do mandato
        )
    assert data_final_mandato == date(2026, 12, 31)


@freeze_time('2027-01-15')
def test_registrar_entrada_adjacencia_nao_acopla_a_dias_antecedencia_saida(monkeypatch, composicao_vacancia_2026):
    """ Adjacência usa sempre 1 dia de calendário, nunca DIAS_ANTECEDENCIA_SAIDA - com
    D-N diferente de 1, uma entrada no dia seguinte ao fim real do registro anterior
    precisa continuar sendo detectada como substituição direta."""
    monkeypatch.setattr(ServicoHistoricoCargoComposicao, 'DIAS_ANTECEDENCIA_SAIDA', 2)

    pedro = _ocupante('Pedro')
    luis = _ocupante('Luis')

    registro_pedro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro_pedro, data_saida=date(2026, 2, 1))
    registro_pedro.refresh_from_db()
    assert registro_pedro.data_fim_no_cargo == date(2026, 1, 30)  # D-2, não D-1

    # vago cobre exatamente [31/01, fim do mandato] - dia seguinte ao fim real de Pedro
    vago = CargoComposicaoVacancia.objects.get(
        composicao=composicao_vacancia_2026,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        ocupante_do_cargo__isnull=True,
    )
    assert vago.data_inicio_no_cargo == date(2026, 1, 31)

    registro_luis = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=luis,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 31),  # dia seguinte ao fim real de Pedro
    )

    registro_pedro.refresh_from_db()
    assert not CargoComposicaoVacancia.objects.filter(
        composicao=composicao_vacancia_2026,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        ocupante_do_cargo__isnull=True,
    ).exists()
    assert registro_luis.substituto is True
    assert registro_pedro.substituido_por_id == registro_luis.id


@freeze_time('2027-01-15')
def test_registrar_entrada_com_gap_real_apos_saida_d_n_mantem_vago_reduzido(monkeypatch, composicao_vacancia_2026):
    """ Entrada que não é exatamente no dia seguinte ao fim real do registro anterior
    representa um gap real - o vago criado por registrar_saida encolhe (não é
    consumido/deletado), mantendo a timeline contígua. """
    monkeypatch.setattr(ServicoHistoricoCargoComposicao, 'DIAS_ANTECEDENCIA_SAIDA', 2)

    pedro = _ocupante('Pedro')
    luis = _ocupante('Luis')

    registro_pedro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro_pedro, data_saida=date(2026, 2, 1))
    # Pedro termina 30/01 (D-2); vago cobre [31/01, fim do mandato]

    registro_luis = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=luis,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 2, 1),  # não é o dia seguinte ao fim real (31/01)
    )

    registro_pedro.refresh_from_db()

    vago_restante = CargoComposicaoVacancia.objects.get(
        composicao=composicao_vacancia_2026,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        ocupante_do_cargo__isnull=True,
    )
    assert vago_restante.data_inicio_no_cargo == date(2026, 1, 31)
    assert vago_restante.data_fim_no_cargo == date(2026, 1, 31)

    assert registro_luis.substituto is False
    assert registro_pedro.substituido_por is None


def test_get_composicao_vacancia_por_composicao_uuid_encontra_registro(composicao_vacancia_2026):
    """ composicao_uuid encontra a ComposicaoVacancia correta."""
    encontrada = ServicoHistoricoCargoComposicao.get_composicao_vacancia_por_uuid_ou_associacao_e_data(
        composicao_uuid=str(composicao_vacancia_2026.uuid),
    )

    assert encontrada is not None
    assert encontrada.id == composicao_vacancia_2026.id


def test_get_composicao_vacancia_por_composicao_uuid_inexistente_retorna_none():
    """ composicao_uuid inexistente retorna None, não lança exceção."""
    encontrada = ServicoHistoricoCargoComposicao.get_composicao_vacancia_por_uuid_ou_associacao_e_data(
        composicao_uuid='00000000-0000-0000-0000-000000000000',
    )

    assert encontrada is None


def test_get_composicao_vacancia_por_associacao_uuid_e_data_dentro_do_intervalo(composicao_vacancia_2026):
    """ (sem composicao_uuid): associacao_uuid + data dentro do intervalo do mandato encontra a composição."""
    encontrada = ServicoHistoricoCargoComposicao.get_composicao_vacancia_por_uuid_ou_associacao_e_data(
        associacao_uuid=str(composicao_vacancia_2026.associacao.uuid),
        data=date(2026, 6, 15),
    )

    assert encontrada is not None
    assert encontrada.id == composicao_vacancia_2026.id


def test_get_composicao_vacancia_por_associacao_uuid_e_data_respeita_limites_do_intervalo(composicao_vacancia_2026):
    """Os extremos do intervalo (data_inicial/data_final) também casam - filtro é lte/gte, não lt/gt."""
    associacao_uuid = str(composicao_vacancia_2026.associacao.uuid)

    # extremos do intervalo (data_inicial/data_final) devem ser encontrados - filtro é lte/gte
    inicio = ServicoHistoricoCargoComposicao.get_composicao_vacancia_por_uuid_ou_associacao_e_data(
        associacao_uuid=associacao_uuid, data=date(2026, 1, 1),
    )
    fim = ServicoHistoricoCargoComposicao.get_composicao_vacancia_por_uuid_ou_associacao_e_data(
        associacao_uuid=associacao_uuid, data=date(2026, 12, 31),
    )

    assert inicio is not None
    assert inicio.id == composicao_vacancia_2026.id
    assert fim is not None
    assert fim.id == composicao_vacancia_2026.id


def test_get_composicao_vacancia_por_associacao_uuid_e_data_fora_do_intervalo_retorna_none(composicao_vacancia_2026):
    """Data fora do intervalo do mandato (além do fim) não encontra nada."""
    encontrada = ServicoHistoricoCargoComposicao.get_composicao_vacancia_por_uuid_ou_associacao_e_data(
        associacao_uuid=str(composicao_vacancia_2026.associacao.uuid),
        data=date(2027, 1, 1),  # 1 dia além do fim do mandato de teste
    )

    assert encontrada is None


def test_get_composicao_vacancia_por_associacao_uuid_de_outra_associacao_retorna_none(
    composicao_vacancia_2026, associacao_factory
):
    """Data válida, mas de uma associação diferente, não deve cruzar composições."""
    outra_associacao = associacao_factory.create()

    encontrada = ServicoHistoricoCargoComposicao.get_composicao_vacancia_por_uuid_ou_associacao_e_data(
        associacao_uuid=str(outra_associacao.uuid),
        data=date(2026, 6, 15),  # dentro do intervalo do mandato de composicao_vacancia_2026...
    )

    assert encontrada is None


def test_get_composicao_vacancia_composicao_uuid_tem_precedencia_sobre_associacao_e_data(
        composicao_vacancia_2026, mandato_2026, associacao_factory):
    """Se os dois critérios forem informados, composicao_uuid vence como prioridade, associacao_uuid/data
    nem chegam a ser usados."""

    outra_associacao = associacao_factory.create()
    outra_composicao = ServicoHistoricoCargoComposicao.get_or_create_composicao_vacancia(
        associacao=outra_associacao, mandato=mandato_2026
    )

    encontrada = ServicoHistoricoCargoComposicao.get_composicao_vacancia_por_uuid_ou_associacao_e_data(
        composicao_uuid=str(composicao_vacancia_2026.uuid),
        associacao_uuid=str(outra_associacao.uuid),
        data=date(2026, 6, 15),
    )

    assert encontrada.id == composicao_vacancia_2026.id
    assert encontrada.id != outra_composicao.id


def test_get_composicao_vacancia_sem_nenhum_criterio_retorna_none():
    """Sem composicao_uuid nem associacao_uuid/data, não monta query nenhuma - retorna None."""
    encontrada = ServicoHistoricoCargoComposicao.get_composicao_vacancia_por_uuid_ou_associacao_e_data()

    assert encontrada is None


def test_get_composicao_vacancia_associacao_uuid_sem_data_retorna_none(composicao_vacancia_2026):
    """associacao_uuid sozinho, sem data, não é critério suficiente - retorna None."""
    encontrada = ServicoHistoricoCargoComposicao.get_composicao_vacancia_por_uuid_ou_associacao_e_data(
        associacao_uuid=str(composicao_vacancia_2026.associacao.uuid),
    )

    assert encontrada is None


@freeze_time(DATA_CONGELADA)
def test_registrar_entrada_rejeita_sobreposicao_com_ocupante_historico(composicao_vacancia_2026):
    """ mesmo sem vacância aberta cobrindo a data, não pode lançar um novo registro
    cujo período cai dentro de um intervalo já OCUPADO por outra pessoa (histórico,
    não só vigente)."""
    joao = _ocupante('João')
    maria = _ocupante('Maria')

    registro_joao = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=joao,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_1,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro_joao, data_saida=date(2026, 3, 1))
    # João: [01/01, 28/02] (histórico, não vigente) - cargo depois fica vago a partir de 01/03

    with pytest.raises(CargoComposicaoVacanciaValidationError):  # noqa
        ServicoHistoricoCargoComposicao.registrar_entrada(
            composicao_vacancia=composicao_vacancia_2026,
            ocupante_do_cargo=maria,
            cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_1,
            data_entrada=date(2026, 2, 1),  # dentro do período histórico de João, não coberto por vago
        )


@freeze_time(DATA_CONGELADA)
def test_registrar_entrada_permite_preencher_vaga_aberta_sem_conflito(composicao_vacancia_2026):
    """ não deve considerar sobreposição com registro VAGO como conflito - preencher
    um gap é o caso normal."""
    joao = _ocupante('João')
    maria = _ocupante('Maria')

    registro_joao = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=joao,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_2,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro_joao, data_saida=date(2026, 3, 1))
    # cargo vago a partir de 01/03

    registro_maria = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=maria,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_2,
        data_entrada=date(2026, 6, 1),  # dentro do período vago, não conflita
    )

    assert registro_maria.pk is not None


@freeze_time(DATA_CONGELADA)
def test_registrar_entrada_rejeita_mesmo_ocupante_em_cargo_diferente_no_mesmo_periodo(composicao_vacancia_2026):
    """o mesmo ocupante não pode estar, ao mesmo tempo, em dois cargos DIFERENTES
    na mesma composição."""
    pedro = _ocupante('Pedro')

    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )

    with pytest.raises(CargoComposicaoVacanciaValidationError):  # noqa
        ServicoHistoricoCargoComposicao.registrar_entrada(
            composicao_vacancia=composicao_vacancia_2026,
            ocupante_do_cargo=pedro,
            cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO,
            data_entrada=date(2026, 6, 1),  # ainda vigente como Presidente nesse período
        )


@freeze_time(DATA_CONGELADA)
def test_registrar_entrada_permite_mesmo_ocupante_no_mesmo_cargo_em_periodo_diferente(composicao_vacancia_2026):
    """o mesmo ocupante PODE voltar a ocupar o MESMO cargo, em período não
    sobreposto - só bloqueia cargo diferente."""
    joao = _ocupante('João')

    registro_1 = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=joao,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_1,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro_1, data_saida=date(2026, 6, 1))

    registro_2 = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=joao,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_1,  # mesmo cargo
        data_entrada=date(2026, 9, 1),
    )

    assert registro_2.pk is not None
    assert registro_2.ocupante_do_cargo_id == joao.id


@freeze_time(DATA_CONGELADA)
def test_registrar_entrada_permite_ocupantes_diferentes_em_cargos_diferentes_mesmo_periodo(composicao_vacancia_2026):
    """ só entra em cena quando é o MESMO ocupante em cargos diferentes."""
    pedro = _ocupante('Pedro')
    luis = _ocupante('Luis')

    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )

    registro_luis = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=luis,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO,
        data_entrada=date(2026, 1, 1),  # mesmo período, ocupante diferente - ok
    )

    assert registro_luis.pk is not None


@freeze_time(DATA_CONGELADA)
def test_registrar_entrada_rejeita_duplicidade_de_codigo_identificacao_entre_vigentes(composicao_vacancia_2026):
    """ Dois OcupanteCargo DISTINTOS com o mesmo codigo_identificacao não podem estar
    ambos vigentes na mesma composição, mesmo em cargos diferentes. """
    pedro = OcupanteCargoFactory(nome='Pedro', codigo_identificacao='111111')

    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )

    pedro_duplicado = OcupanteCargoFactory(nome='Pedro Duplicado', codigo_identificacao='111111')

    with pytest.raises(CargoComposicaoVacanciaValidationError):  # noqa
        ServicoHistoricoCargoComposicao.registrar_entrada(
            composicao_vacancia=composicao_vacancia_2026,
            ocupante_do_cargo=pedro_duplicado,
            cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO,
            data_entrada=date(2026, 1, 1),
        )


@freeze_time(DATA_CONGELADA)
def test_registrar_entrada_rejeita_duplicidade_de_cpf_responsavel_entre_vigentes(composicao_vacancia_2026):
    """ Dois OcupanteCargo DISTINTOS com o mesmo cpf_responsavel não podem estar
    ambos vigentes na mesma composição, mesmo em cargos diferentes. """
    luis = OcupanteCargoFactory(nome='Luis', cpf_responsavel='99988877766')

    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=luis,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )

    luis_duplicado = OcupanteCargoFactory(nome='Luis Duplicado', cpf_responsavel='99988877766')

    with pytest.raises(CargoComposicaoVacanciaValidationError):  # noqa
        ServicoHistoricoCargoComposicao.registrar_entrada(
            composicao_vacancia=composicao_vacancia_2026,
            ocupante_do_cargo=luis_duplicado,
            cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO,
            data_entrada=date(2026, 1, 1),
        )


@freeze_time(DATA_CONGELADA)
def test_registrar_entrada_permite_duplicidade_contra_registro_historico_encerrado(composicao_vacancia_2026):
    """ Duplicidade de codigo_identificacao/cpf_responsavel só é bloqueada contra registros
    VIGENTES - um registro encerrado do mesmo cargo não deve contar. """
    joao = OcupanteCargoFactory(nome='João', codigo_identificacao='222222', cpf_responsavel='11122233344')

    registro_1 = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=joao,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_1,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro_1, data_saida=date(2026, 6, 1))
    # registro_1 encerrado, cargo vago

    joao_novo_cadastro = OcupanteCargoFactory(
        nome='João', codigo_identificacao='222222', cpf_responsavel='11122233344'
    )

    registro_2 = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=joao_novo_cadastro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO,
        data_entrada=date(2026, 9, 1),
    )

    assert registro_2.pk is not None


@freeze_time(DATA_CONGELADA)
def test_registrar_entrada_ignora_codigo_identificacao_e_cpf_vazios_na_checagem_de_duplicidade(
        composicao_vacancia_2026):
    """ codigo_identificacao/cpf_responsavel vazios (representação padrão do model, '') não
    devem gerar falso-positivo de duplicidade entre dois ocupantes distintos."""
    pedro = OcupanteCargoFactory(nome='Pedro', codigo_identificacao='', cpf_responsavel='')

    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )

    luis = OcupanteCargoFactory(nome='Luis', codigo_identificacao='', cpf_responsavel='')

    registro_luis = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=luis,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO,
        data_entrada=date(2026, 1, 1),
    )

    assert registro_luis.pk is not None


@freeze_time(DATA_CONGELADA)
def test_cancelar_saida_reverte_para_vigente_e_remove_a_vacancia_aberta(composicao_vacancia_2026):
    """ Cenário normal: saída registrada, ninguém assumiu ainda (cargo ficou vago) -
    cancelar deve voltar o registro pra vigente e apagar a vacância criada."""
    pedro = _ocupante('Pedro')

    registro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_SECRETARIO,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro, data_saida=date(2026, 6, 1))
    registro.refresh_from_db()
    assert registro.data_fim_no_cargo == date(2026, 5, 31)

    ServicoHistoricoCargoComposicao.cancelar_saida(registro)
    registro.refresh_from_db()

    assert registro.data_fim_no_cargo == composicao_vacancia_2026.mandato.data_final
    assert not CargoComposicaoVacancia.objects.filter(
        composicao=composicao_vacancia_2026,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_SECRETARIO,
        ocupante_do_cargo__isnull=True,
    ).exists()


@freeze_time(DATA_CONGELADA)
def test_cancelar_saida_bloqueado_se_registro_ja_esta_vigente(composicao_vacancia_2026):
    """ Não há saída pra cancelar num registro que nunca saiu (ainda vigente)."""
    pedro = _ocupante('Pedro')

    registro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_4,
        data_entrada=date(2026, 1, 1),
    )

    with pytest.raises(CargoComposicaoVacanciaValidationError):
        ServicoHistoricoCargoComposicao.cancelar_saida(registro)


@freeze_time(DATA_CONGELADA)
def test_cancelar_saida_bloqueado_se_ja_existe_sucessor(composicao_vacancia_2026):
    """ se alguém já assumiu diretamente (substituido_por preenchido), cancelar
    reativaria dois ocupantes vigentes no mesmo cargo - precisa ser bloqueado. """
    pedro = _ocupante('Pedro')
    luis = _ocupante('Luis')

    registro_pedro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_5,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro_pedro, data_saida=date(2026, 2, 1))
    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=luis,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_5,
        data_entrada=date(2026, 2, 1),  # substituição direta - Pedro.substituido_por = Luis
    )
    registro_pedro.refresh_from_db()
    assert registro_pedro.substituido_por_id is not None

    with pytest.raises(CargoComposicaoVacanciaValidationError):
        ServicoHistoricoCargoComposicao.cancelar_saida(registro_pedro)


# cancelar_entrada

@freeze_time(DATA_CONGELADA)
def test_cancelar_entrada_reverte_substituicao_direta_e_restaura_anterior_como_vigente(composicao_vacancia_2026):
    """ Luis substituiu Pedro diretamente. Cancelar a entrada de Luis deve apagar o
    registro dele e devolver Pedro a vigente, desfazendo o vínculo de substituição."""
    pedro = _ocupante('Pedro')
    luis = _ocupante('Luis')

    registro_pedro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro_pedro, data_saida=date(2026, 4, 1))
    registro_luis = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=luis,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO,
        data_entrada=date(2026, 4, 1),
    )
    registro_pedro.refresh_from_db()
    assert registro_pedro.substituido_por_id == registro_luis.id

    ServicoHistoricoCargoComposicao.cancelar_entrada(registro_luis)

    assert not CargoComposicaoVacancia.objects.filter(pk=registro_luis.pk).exists()
    registro_pedro.refresh_from_db()
    assert registro_pedro.substituido_por_id is None
    assert registro_pedro.data_fim_no_cargo == composicao_vacancia_2026.mandato.data_final


@freeze_time(DATA_CONGELADA)
def test_cancelar_entrada_restaura_vacancia_anterior_estendendo_ate_o_fim_do_mandato(composicao_vacancia_2026):
    """ Pedro saiu, ficou vago um bom tempo, Maria entrou bem depois (sem substituição
    direta). Cancelar a entrada de Maria deve devolver o vago ao estado anterior."""
    pedro = _ocupante('Pedro')
    maria = _ocupante('Maria')

    registro_pedro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VICE_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro_pedro, data_saida=date(2026, 4, 1))
    registro_maria = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=maria,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VICE_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 6, 1),  # bem depois do fim do Pedro (31/03) - vago real no meio
    )

    ServicoHistoricoCargoComposicao.cancelar_entrada(registro_maria)

    assert not CargoComposicaoVacancia.objects.filter(pk=registro_maria.pk).exists()
    vago = CargoComposicaoVacancia.objects.get(
        composicao=composicao_vacancia_2026,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VICE_PRESIDENTE_DIRETORIA_EXECUTIVA,
        ocupante_do_cargo__isnull=True,
    )
    assert vago.data_inicio_no_cargo == date(2026, 4, 1)
    assert vago.data_fim_no_cargo == composicao_vacancia_2026.mandato.data_final


@freeze_time(DATA_CONGELADA)
def test_cancelar_entrada_primeira_entrada_do_cargo_cria_vago_cobrindo_o_mandato_inteiro(composicao_vacancia_2026):
    """ Cargo nunca teve ninguém antes. Cancelar a única entrada existente deve deixar
    o cargo vago do início ao fim do mandato, como se nunca tivesse sido ocupado."""
    pedro = _ocupante('Pedro')

    registro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_1,
        data_entrada=date(2026, 3, 1),
    )

    ServicoHistoricoCargoComposicao.cancelar_entrada(registro)

    assert not CargoComposicaoVacancia.objects.filter(pk=registro.pk).exists()
    vago = CargoComposicaoVacancia.objects.get(
        composicao=composicao_vacancia_2026,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_1,
    )
    assert vago.ocupante_do_cargo_id is None
    assert vago.data_inicio_no_cargo == composicao_vacancia_2026.mandato.data_inicial
    assert vago.data_fim_no_cargo == composicao_vacancia_2026.mandato.data_final


@freeze_time(DATA_CONGELADA)
def test_cancelar_entrada_bloqueado_quando_registro_ja_saiu(composicao_vacancia_2026):
    """ Só o registro vigente (último da timeline) pode ter a entrada cancelada. """
    pedro = _ocupante('Pedro')

    registro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_2,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro, data_saida=date(2026, 6, 1))
    registro.refresh_from_db()

    with pytest.raises(CargoComposicaoVacanciaValidationError):
        ServicoHistoricoCargoComposicao.cancelar_entrada(registro)


@freeze_time(DATA_CONGELADA)
def test_cancelar_entrada_bloqueado_em_cargo_vago(composicao_vacancia_2026):
    """ Não existe entrada nenhuma pra cancelar num registro vago. """
    cargos = ServicoHistoricoCargoComposicao.get_snapshot_da_composicao_em_data(
        composicao_vacancia_2026, date(2026, 6, 1)
    )
    vago = cargos[CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_3]
    assert vago is None  # nunca teve registro nenhum - não há o que cancelar

    registro_vago = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=_ocupante('Pedro'),
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_3,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro_vago, data_saida=date(2026, 2, 1))
    registro_vago.refresh_from_db()
    vago_real = CargoComposicaoVacancia.objects.get(
        composicao=composicao_vacancia_2026,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_3,
        ocupante_do_cargo__isnull=True,
    )

    with pytest.raises(CargoComposicaoVacanciaValidationError):
        ServicoHistoricoCargoComposicao.cancelar_entrada(vago_real)


@freeze_time(DATA_CONGELADA)
def test_registrar_entrada_rejeita_data_futura(composicao_vacancia_2026):
    """ registrar_entrada não pode aceitar data_entrada futura. """
    pedro = _ocupante('Pedro')

    with pytest.raises(CargoComposicaoVacanciaValidationError):  # noqa
        ServicoHistoricoCargoComposicao.registrar_entrada(
            composicao_vacancia=composicao_vacancia_2026,
            ocupante_do_cargo=pedro,
            cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_2,
            data_entrada=date(2027, 6, 1),  # depois de DATA_CONGELADA (15/01/2027)
        )


@freeze_time(DATA_CONGELADA)
def test_registrar_entrada_rejeita_cargo_ja_ocupado_e_vigente(composicao_vacancia_2026):
    """ não pode registrar entrada num cargo que já tem ocupante vigente -
    testado direto no service (antes só era exercitado via serializer)."""
    pedro = _ocupante('Pedro')
    luis = _ocupante('Luis')

    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_3,
        data_entrada=date(2026, 1, 1),
    )

    with pytest.raises(CargoComposicaoVacanciaValidationError):  # noqa
        ServicoHistoricoCargoComposicao.registrar_entrada(
            composicao_vacancia=composicao_vacancia_2026,
            ocupante_do_cargo=luis,
            cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_3,  # mesmo cargo, Pedro ainda vigente
            data_entrada=date(2026, 6, 1),
        )


@freeze_time(DATA_CONGELADA)
def test_registrar_saida_rejeita_data_anterior_ao_inicio_no_cargo(composicao_vacancia_2026):
    """ a data de saída (já com D-1 aplicado) não pode cair antes do início no cargo."""
    pedro = _ocupante('Pedro')

    registro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_4,
        data_entrada=date(2026, 6, 1),
    )

    with pytest.raises(CargoComposicaoVacanciaValidationError):  # noqa
        # D-1 de 01/06 é 31/05, anterior à data_inicio_no_cargo (01/06)
        ServicoHistoricoCargoComposicao.registrar_saida(registro, data_saida=date(2026, 6, 1))


@freeze_time(DATA_CONGELADA)
def test_registrar_saida_rejeita_registro_ja_encerrado(composicao_vacancia_2026):
    """ não dá pra registrar saída de novo num registro que já não está mais
    vigente - testado direto no service (antes só era exercitado via viewset)."""
    pedro = _ocupante('Pedro')

    registro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_CONSELHO_FISCAL,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro, data_saida=date(2026, 6, 1))

    with pytest.raises(CargoComposicaoVacanciaValidationError):  # noqa
        ServicoHistoricoCargoComposicao.registrar_saida(registro, data_saida=date(2026, 8, 1))


@freeze_time(DATA_CONGELADA)
def test_get_snapshot_da_composicao_em_data_cobre_todos_os_cargos(composicao_vacancia_2026):
    """ get_snapshot_da_composicao_em_data retorna todos os cargos do choices, com
    None pra quem nunca teve registro e o CargoComposicaoVacancia pra quem tem."""
    pedro = _ocupante('Pedro')
    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )

    snapshot = ServicoHistoricoCargoComposicao.get_snapshot_da_composicao_em_data(
        composicao_vacancia_2026, date(2026, 6, 1)
    )

    assert len(snapshot) == len(CargoComposicao.CARGO_ASSOCIACAO_CHOICES)
    assert snapshot[CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA].ocupante_do_cargo_id == pedro.id
    assert snapshot[CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO] is None  # nunca teve ninguém


# monta_cargos_da_composicao / _monta_item_do_cargo

@freeze_time(DATA_CONGELADA)
def test_monta_cargos_da_composicao_separa_diretoria_executiva_e_conselho_fiscal(composicao_vacancia_2026):
    """9 cargos em diretoria_executiva, 5 em conselho_fiscal, na ordem de Cargo.choices."""
    cargos = ServicoHistoricoCargoComposicao.monta_cargos_da_composicao(composicao_vacancia_2026, date(2026, 6, 1))

    assert len(cargos['diretoria_executiva']) == 9
    assert len(cargos['conselho_fiscal']) == 5
    assert cargos['diretoria_executiva'][0]['cargo_associacao'] == CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA  # noqa
    assert cargos['conselho_fiscal'][0]['cargo_associacao'] == CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_CONSELHO_FISCAL  # noqa


@freeze_time(DATA_CONGELADA)
def test_monta_cargos_da_composicao_cargo_vazio_nunca_teve_registro(composicao_vacancia_2026):
    """Cargo sem nenhum registro: ocupante_do_cargo todo None, vago, sem uuid/id, sem
    nenhuma ação de cancelamento disponível."""
    cargos = ServicoHistoricoCargoComposicao.monta_cargos_da_composicao(composicao_vacancia_2026, date(2026, 6, 1))

    tesoureiro = (
        next(c for c in cargos['diretoria_executiva']
             if c['cargo_associacao'] == CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO))

    assert tesoureiro['id'] is None
    assert tesoureiro['uuid'] is None
    assert tesoureiro['ocupante_do_cargo']['nome'] is None
    assert tesoureiro['data_inicio_no_cargo'] is None
    assert tesoureiro['cargo_vago'] is True
    assert tesoureiro['cargo_vago_vigente'] is True
    assert tesoureiro['cargo_vigente'] is True
    assert tesoureiro['pode_cancelar_entrada'] is False
    assert tesoureiro['pode_cancelar_saida'] is False


@freeze_time(DATA_CONGELADA)
def test_monta_cargos_da_composicao_cargo_ocupado(composicao_vacancia_2026):
    """Cargo ocupado: dados do ocupante presentes, não vago, com a entrada cancelável
    (ninguém saiu ainda)."""
    pedro = _ocupante('Pedro')
    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )

    cargos = ServicoHistoricoCargoComposicao.monta_cargos_da_composicao(composicao_vacancia_2026, date(2026, 6, 1))
    presidente = cargos['diretoria_executiva'][0]

    assert presidente['ocupante_do_cargo']['nome'] == 'Pedro'
    assert presidente['ocupante_do_cargo']['id'] == pedro.id
    assert presidente['data_inicio_no_cargo'] == date(2026, 1, 1)
    assert presidente['cargo_vago'] is False
    assert presidente['pode_cancelar_entrada'] is True
    assert presidente['pode_cancelar_saida'] is False


@freeze_time(DATA_CONGELADA)
def test_monta_cargos_da_composicao_cargo_vago_apos_saida_tem_registro_mas_e_editavel(composicao_vacancia_2026):
    """Vago com registro real (pós-saída) - diferente de nunca-preenchido, mas continua
    vago (cargo_vago), com id/uuid do registro de vacância preenchidos."""
    pedro = _ocupante('Pedro')
    registro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_SECRETARIO,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro, data_saida=date(2026, 3, 1))

    cargos = ServicoHistoricoCargoComposicao.monta_cargos_da_composicao(composicao_vacancia_2026, date(2026, 6, 1))
    secretario = (
        next(c for c in cargos['diretoria_executiva']
             if c['cargo_associacao'] == CargoComposicao.CARGO_ASSOCIACAO_SECRETARIO))

    assert secretario['id'] is not None
    assert secretario['ocupante_do_cargo']['nome'] is None
    assert secretario['cargo_vago'] is True
    assert secretario['pode_cancelar_entrada'] is False
    assert secretario['pode_cancelar_saida'] is False


@freeze_time('2026-06-15')
def test_monta_cargos_da_composicao_eh_composicao_vigente_true_quando_mandato_e_o_vigente(composicao_vacancia_2026):
    """Mandato dentro do período congelado é o vigente - eh_composicao_vigente True."""
    cargos = ServicoHistoricoCargoComposicao.monta_cargos_da_composicao(composicao_vacancia_2026, date(2026, 6, 1))

    assert cargos['diretoria_executiva'][0]['eh_composicao_vigente'] is True


@freeze_time(DATA_CONGELADA)
def test_monta_cargos_da_composicao_eh_composicao_vigente_false_quando_mandato_ja_passou(composicao_vacancia_2026):
    """DATA_CONGELADA é posterior ao fim do mandato de teste - não é mais o vigente."""
    cargos = ServicoHistoricoCargoComposicao.monta_cargos_da_composicao(composicao_vacancia_2026, date(2026, 6, 1))

    assert cargos['diretoria_executiva'][0]['eh_composicao_vigente'] is False


@freeze_time(DATA_CONGELADA)
def test_monta_cargos_da_composicao_substituto_e_substituido(composicao_vacancia_2026):
    """substituto/substituido só indicam booleanamente se o ocupante entrou no lugar de
    outro ou foi sucedido - os nomes de quem substituiu/foi substituído (ocupante_substitui/
    ocupante_substituido_por) e as tags textuais (tag_substituto/tag_substituido) não fazem
    mais parte do formato v2; o timeline já mostra a sequência de ocupantes por si só."""
    pedro = _ocupante('Pedro')
    luis = _ocupante('Luis')

    registro_pedro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_1,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro_pedro, data_saida=date(2026, 2, 1))
    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=luis,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_1,
        data_entrada=date(2026, 2, 1),
    )

    # snapshot em 01/06: Luis está vigente no cargo, é o substituto
    cargos_luis = ServicoHistoricoCargoComposicao.monta_cargos_da_composicao(composicao_vacancia_2026, date(2026, 6, 1))
    vogal_1_luis = (
        next(c for c in cargos_luis['diretoria_executiva']
             if c['cargo_associacao'] == CargoComposicao.CARGO_ASSOCIACAO_VOGAL_1))

    assert vogal_1_luis['ocupante_do_cargo']['nome'] == 'Luis'
    assert vogal_1_luis['substituto'] is True

    # snapshot em 15/01 (dentro do período do Pedro): Pedro já está marcado como substituido
    cargos_pedro = ServicoHistoricoCargoComposicao.monta_cargos_da_composicao(
        composicao_vacancia_2026,
        date(2026, 1, 15)
    )
    vogal_1_pedro = (
        next(c for c in cargos_pedro['diretoria_executiva']
             if c['cargo_associacao'] == CargoComposicao.CARGO_ASSOCIACAO_VOGAL_1))

    assert vogal_1_pedro['ocupante_do_cargo']['nome'] == 'Pedro'
    assert vogal_1_pedro['substituido'] is True


@freeze_time(DATA_CONGELADA)
def test_monta_cargos_da_composicao_ocupante_vigente_true_quando_ocupado_e_vigente(composicao_vacancia_2026):
    """Ocupante que entrou e nunca saiu: data_fim_no_cargo == mandato.data_final, vigente."""
    pedro = _ocupante('Pedro')
    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )

    cargos = ServicoHistoricoCargoComposicao.monta_cargos_da_composicao(composicao_vacancia_2026, date(2026, 6, 1))
    presidente = cargos['diretoria_executiva'][0]

    assert presidente['ocupante_vigente'] is True


@freeze_time(DATA_CONGELADA)
def test_monta_cargos_da_composicao_ocupante_vigente_false_quando_ja_saiu(composicao_vacancia_2026):
    """Navegando por um marco anterior à saída: o registro aparece como 'ocupado' naquela
    data, mas já não é mais vigente hoje - não deve permitir 'Informar saída' no frontend."""
    pedro = _ocupante('Pedro')
    registro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_SECRETARIO,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro, data_saida=date(2026, 6, 1))

    # snapshot num marco em que Pedro ainda ocupava o cargo, antes da saída
    cargos = ServicoHistoricoCargoComposicao.monta_cargos_da_composicao(composicao_vacancia_2026, date(2026, 3, 1))
    secretario = (
        next(c for c in cargos['diretoria_executiva']
             if c['cargo_associacao'] == CargoComposicao.CARGO_ASSOCIACAO_SECRETARIO))

    assert secretario['ocupante_do_cargo']['nome'] == 'Pedro'
    assert secretario['ocupante_vigente'] is False


@freeze_time(DATA_CONGELADA)
def test_monta_cargos_da_composicao_ocupante_vigente_false_quando_vago(composicao_vacancia_2026):
    """Cargo vago não tem ocupante nenhum, então não pode estar vigente."""
    cargos = ServicoHistoricoCargoComposicao.monta_cargos_da_composicao(composicao_vacancia_2026, date(2026, 6, 1))

    tesoureiro = (
        next(c for c in cargos['diretoria_executiva']
             if c['cargo_associacao'] == CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO)
    )

    assert tesoureiro['ocupante_vigente'] is False


@freeze_time(DATA_CONGELADA)
def test_monta_cargos_da_composicao_eh_primeiro_ocupante_true_para_o_primeiro_e_false_para_o_seguinte(
        composicao_vacancia_2026):
    """Paulo é o primeiro ocupante do cargo; José, que entra depois dele (mesmo com um
    vago no meio), não é - eh_primeiro_ocupante olha pra quem ocupou antes, não pro gap."""
    paulo = _ocupante('Paulo')
    jose = _ocupante('Jose')

    registro_paulo = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=paulo,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_SECRETARIO,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro_paulo, data_saida=date(2026, 1, 30))
    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=jose,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_SECRETARIO,
        data_entrada=date(2026, 3, 5),
    )

    # snapshot num marco em que Paulo ainda ocupava o cargo
    cargos_paulo = ServicoHistoricoCargoComposicao.monta_cargos_da_composicao(
        composicao_vacancia_2026, date(2026, 1, 15)
    )
    secretario_paulo = (
        next(c for c in cargos_paulo['diretoria_executiva']
             if c['cargo_associacao'] == CargoComposicao.CARGO_ASSOCIACAO_SECRETARIO))
    assert secretario_paulo['ocupante_do_cargo']['nome'] == 'Paulo'
    assert secretario_paulo['eh_primeiro_ocupante'] is True

    # snapshot num marco em que José já ocupava o cargo
    cargos_jose = ServicoHistoricoCargoComposicao.monta_cargos_da_composicao(
        composicao_vacancia_2026, date(2026, 3, 10)
    )
    secretario_jose = (
        next(c for c in cargos_jose['diretoria_executiva']
             if c['cargo_associacao'] == CargoComposicao.CARGO_ASSOCIACAO_SECRETARIO))
    assert secretario_jose['ocupante_do_cargo']['nome'] == 'Jose'
    assert secretario_jose['eh_primeiro_ocupante'] is False


@freeze_time(DATA_CONGELADA)
def test_monta_cargos_da_composicao_eh_primeiro_ocupante_true_mesmo_apos_periodo_vago_inicial(
        composicao_vacancia_2026):
    """Paulo entra um mês depois do início do mandato (cargo ficou vago até então) - como
    não houve nenhum OCUPANTE antes dele, ele continua sendo o primeiro."""
    paulo = _ocupante('Paulo')

    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=paulo,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO,
        data_entrada=date(2026, 2, 1),
    )

    cargos = ServicoHistoricoCargoComposicao.monta_cargos_da_composicao(composicao_vacancia_2026, date(2026, 6, 1))
    tesoureiro = (
        next(c for c in cargos['diretoria_executiva']
             if c['cargo_associacao'] == CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO))

    assert tesoureiro['ocupante_do_cargo']['nome'] == 'Paulo'
    assert tesoureiro['eh_primeiro_ocupante'] is True


# get_timeline_consolidada_da_composicao

@freeze_time(DATA_CONGELADA)
def test_get_timeline_consolidada_separa_diretoria_executiva_e_conselho_fiscal(composicao_vacancia_2026):
    """9 cargos em diretoria_executiva, 5 em conselho_fiscal, na ordem de Cargo.choices -
    mesmo agrupamento de monta_cargos_da_composicao, só que com a timeline inteira embutida
    em cada cargo em vez do snapshot de uma única data."""
    resultado = ServicoHistoricoCargoComposicao.get_timeline_consolidada_da_composicao(composicao_vacancia_2026)

    assert len(resultado['diretoria_executiva']) == 9
    assert len(resultado['conselho_fiscal']) == 5
    assert resultado['diretoria_executiva'][0]['cargo_associacao'] == CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA  # noqa
    assert resultado['conselho_fiscal'][0]['cargo_associacao'] == CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_CONSELHO_FISCAL  # noqa


@freeze_time(DATA_CONGELADA)
def test_get_timeline_consolidada_cargo_nunca_tocado_tem_timeline_vazia(composicao_vacancia_2026):
    """Cargo sem nenhum registro no banco: entra no resultado com timeline: [] (o
    placeholder "vago" sintético é responsabilidade só do frontend, igual já acontece
    hoje em get_timeline_do_cargo)."""
    resultado = ServicoHistoricoCargoComposicao.get_timeline_consolidada_da_composicao(composicao_vacancia_2026)

    tesoureiro = next(
        c for c in resultado['diretoria_executiva']
        if c['cargo_associacao'] == CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO
    )

    assert tesoureiro['cargo_associacao_label'] == 'Tesoureiro'
    assert tesoureiro['timeline'] == []


@freeze_time(DATA_CONGELADA)
def test_get_timeline_consolidada_inclui_vago_no_meio_da_timeline_em_ordem_cronologica(composicao_vacancia_2026):
    """Ocupado -> vago (gap real) -> ocupado: os 3 segmentos aparecem, em ordem, na
    timeline consolidada do cargo - mesmo cenário de test_cenario_completo_gap_entre_dois_ocupantes."""
    joao = _ocupante('João')
    maria = _ocupante('Maria')

    registro_joao = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=joao,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_3,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro_joao, data_saida=date(2026, 6, 1))
    ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=maria,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_3,
        data_entrada=date(2026, 9, 1),
    )

    resultado = ServicoHistoricoCargoComposicao.get_timeline_consolidada_da_composicao(composicao_vacancia_2026)
    conselheiro_3 = next(
        c for c in resultado['conselho_fiscal']
        if c['cargo_associacao'] == CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_3
    )

    assert len(conselheiro_3['timeline']) == 3
    assert conselheiro_3['timeline'][0]['ocupante_do_cargo']['nome'] == 'João'
    assert conselheiro_3['timeline'][1]['cargo_vago'] is True
    assert conselheiro_3['timeline'][2]['ocupante_do_cargo']['nome'] == 'Maria'


@freeze_time(DATA_CONGELADA)
def test_get_timeline_consolidada_eh_primeiro_ultimo_ocupante_e_substituto_batem_com_calculo_por_registro(
        composicao_vacancia_2026):
    """Os três campos que a consolidada pré-calcula em memória (eh_primeiro_ocupante,
    eh_ultimo_ocupante, substituto) - pra eliminar o N+1 de _monta_item_do_cargo quando
    chamado por registro - precisam bater com a mesma regra de negócio: Pedro é o
    primeiro ocupante e foi substituído diretamente por Luis, que é o último e o substituto."""
    pedro = _ocupante('Pedro')
    luis = _ocupante('Luis')

    registro_pedro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro_pedro, data_saida=date(2026, 2, 1))
    registro_luis = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=luis,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 2, 1),
    )

    resultado = ServicoHistoricoCargoComposicao.get_timeline_consolidada_da_composicao(composicao_vacancia_2026)
    presidente = next(
        c for c in resultado['diretoria_executiva']
        if c['cargo_associacao'] == CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    )

    assert len(presidente['timeline']) == 2
    item_pedro = next(item for item in presidente['timeline'] if item['uuid'] == str(registro_pedro.uuid))
    item_luis = next(item for item in presidente['timeline'] if item['uuid'] == str(registro_luis.uuid))

    assert item_pedro['eh_primeiro_ocupante'] is True
    assert item_pedro['eh_ultimo_ocupante'] is False
    assert item_pedro['substituto'] is False
    assert item_pedro['substituido'] is True

    assert item_luis['eh_primeiro_ocupante'] is False
    assert item_luis['eh_ultimo_ocupante'] is True
    assert item_luis['substituto'] is True
    assert item_luis['substituido'] is False


@freeze_time(DATA_CONGELADA)
def test_get_timeline_consolidada_numero_de_queries_nao_escala_com_quantidade_de_registros(
        composicao_vacancia_2026, django_assert_max_num_queries):
    """A consolidada precisa rodar em um número fixo de queries pra composição inteira -
    é justamente o que elimina o N+1 que hoje existe (1 request por cargo, e dentro de
    cada uma até 3 queries extras por registro em _monta_item_do_cargo)."""
    for indice, (cargo_associacao, _) in enumerate(CargoComposicao.CARGO_ASSOCIACAO_CHOICES):
        registro = ServicoHistoricoCargoComposicao.registrar_entrada(
            composicao_vacancia=composicao_vacancia_2026,
            ocupante_do_cargo=_ocupante(f'Ocupante {indice}'),
            cargo_associacao=cargo_associacao,
            data_entrada=date(2026, 1, 1),
        )
        ServicoHistoricoCargoComposicao.registrar_saida(registro, data_saida=date(2026, 6, 1))
        ServicoHistoricoCargoComposicao.registrar_entrada(
            composicao_vacancia=composicao_vacancia_2026,
            ocupante_do_cargo=_ocupante(f'Ocupante {indice} substituto'),
            cargo_associacao=cargo_associacao,
            data_entrada=date(2026, 9, 1),
        )

    # 14 cargos x 2 registros cada (28 no total) - se escalasse por registro (N+1)
    # seriam dezenas de queries; deve continuar num número fixo e pequeno.
    with django_assert_max_num_queries(6):
        ServicoHistoricoCargoComposicao.get_timeline_consolidada_da_composicao(composicao_vacancia_2026)


# editar_ocupante

@freeze_time(DATA_CONGELADA)
def test_editar_ocupante_atualiza_dados_do_ocupante(composicao_vacancia_2026):
    """Edita nome/telefone do ocupante de um registro ocupado, sem tocar em cargo/datas."""
    pedro = _ocupante('Pedro')
    registro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )

    ServicoHistoricoCargoComposicao.editar_ocupante(
        cargo_composicao_vacancia=registro,
        dados_ocupante={'nome': 'Pedro Alterado', 'telefone': '11999998888'},
    )

    pedro.refresh_from_db()
    registro.refresh_from_db()
    assert pedro.nome == 'Pedro Alterado'
    assert pedro.telefone == '11999998888'
    assert registro.cargo_associacao == CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    assert registro.data_inicio_no_cargo == date(2026, 1, 1)  # datas intocadas


@freeze_time(DATA_CONGELADA)
def test_editar_ocupante_bloqueado_em_cargo_vago(composicao_vacancia_2026):
    """Não é possível editar um registro vago (sem ocupante)."""
    pedro = _ocupante('Pedro')
    registro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_SECRETARIO,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro, data_saida=date(2026, 3, 1))

    vago = CargoComposicaoVacancia.objects.get(
        composicao=composicao_vacancia_2026,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_SECRETARIO,
        ocupante_do_cargo__isnull=True,
    )

    with pytest.raises(CargoComposicaoVacanciaValidationError):  # noqa
        ServicoHistoricoCargoComposicao.editar_ocupante(
            cargo_composicao_vacancia=vago,
            dados_ocupante={'nome': 'Outro Nome'},
        )


# ValidatorSemGapNaTimelineDoCargo

@freeze_time(DATA_CONGELADA)
def test_validator_sem_gap_passa_quando_timeline_esta_contigua(composicao_vacancia_2026):
    """Timeline coberta do início ao fim do mandato, sem buraco - não levanta erro."""
    pedro = _ocupante('Pedro')
    registro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia_2026,
        ocupante_do_cargo=pedro,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(registro, data_saida=date(2026, 6, 1))

    ValidatorSemGapNaTimelineDoCargo.validar(
        composicao_vacancia=composicao_vacancia_2026,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_TESOUREIRO,
        mandato=composicao_vacancia_2026.mandato,
    )  # não levanta


@freeze_time(DATA_CONGELADA)
def test_validator_sem_gap_ignora_cargo_sem_nenhum_registro(composicao_vacancia_2026):
    """Cargo que nunca teve nenhum registro não é considerado inconsistente."""
    ValidatorSemGapNaTimelineDoCargo.validar(
        composicao_vacancia=composicao_vacancia_2026,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_2,
        mandato=composicao_vacancia_2026.mandato,
    )  # não levanta


@freeze_time(DATA_CONGELADA)
def test_validator_sem_gap_detecta_primeiro_registro_fora_do_inicio_do_mandato(composicao_vacancia_2026):
    """Primeiro registro do cargo não começa em mandato.data_inicial - inconsistência."""
    CargoComposicaoVacancia.objects.create(
        composicao=composicao_vacancia_2026,
        ocupante_do_cargo=_ocupante('Pedro'),
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_3,
        data_inicio_no_cargo=date(2026, 1, 10),  # deveria ser 01/01
        data_fim_no_cargo=date(2026, 12, 31),
    )

    with pytest.raises(CargoComposicaoVacanciaValidationError):  # noqa
        ValidatorSemGapNaTimelineDoCargo.validar(
            composicao_vacancia=composicao_vacancia_2026,
            cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_3,
            mandato=composicao_vacancia_2026.mandato,
        )


@freeze_time(DATA_CONGELADA)
def test_validator_sem_gap_detecta_buraco_entre_dois_registros(composicao_vacancia_2026):
    """Dois registros do mesmo cargo com um dia sem cobertura entre eles - inconsistência."""
    composicao = composicao_vacancia_2026
    CargoComposicaoVacancia.objects.create(
        composicao=composicao,
        ocupante_do_cargo=_ocupante('Pedro'),
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_4,
        data_inicio_no_cargo=date(2026, 1, 1),
        data_fim_no_cargo=date(2026, 6, 1),
    )
    CargoComposicaoVacancia.objects.create(
        composicao=composicao,
        ocupante_do_cargo=None,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_4,
        data_inicio_no_cargo=date(2026, 6, 3),  # falta o dia 02/06
        data_fim_no_cargo=date(2026, 12, 31),
    )

    with pytest.raises(CargoComposicaoVacanciaValidationError):  # noqa
        ValidatorSemGapNaTimelineDoCargo.validar(
            composicao_vacancia=composicao,
            cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_4,
            mandato=composicao.mandato,
        )


@freeze_time(DATA_CONGELADA)
def test_validator_sem_gap_detecta_sobreposicao_entre_dois_registros(composicao_vacancia_2026):
    """Dois registros do mesmo cargo com datas sobrepostas - também é inconsistência."""
    composicao = composicao_vacancia_2026
    CargoComposicaoVacancia.objects.create(
        composicao=composicao,
        ocupante_do_cargo=_ocupante('Pedro'),
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_5,
        data_inicio_no_cargo=date(2026, 1, 1),
        data_fim_no_cargo=date(2026, 6, 5),
    )
    CargoComposicaoVacancia.objects.create(
        composicao=composicao,
        ocupante_do_cargo=None,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_5,
        data_inicio_no_cargo=date(2026, 6, 1),  # sobrepõe 01 a 05/06 com o registro anterior
        data_fim_no_cargo=date(2026, 12, 31),
    )

    with pytest.raises(CargoComposicaoVacanciaValidationError):  # noqa
        ValidatorSemGapNaTimelineDoCargo.validar(
            composicao_vacancia=composicao,
            cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_VOGAL_5,
            mandato=composicao.mandato,
        )


@freeze_time(DATA_CONGELADA)
def test_validator_sem_gap_detecta_ultimo_registro_fora_do_fim_do_mandato(composicao_vacancia_2026):
    """Último registro do cargo não termina em mandato.data_final - inconsistência."""
    CargoComposicaoVacancia.objects.create(
        composicao=composicao_vacancia_2026,
        ocupante_do_cargo=_ocupante('Pedro'),
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_1,
        data_inicio_no_cargo=date(2026, 1, 1),
        data_fim_no_cargo=date(2026, 12, 20),  # deveria ser 31/12
    )

    with pytest.raises(CargoComposicaoVacanciaValidationError):  # noqa
        ValidatorSemGapNaTimelineDoCargo.validar(
            composicao_vacancia=composicao_vacancia_2026,
            cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_CONSELHEIRO_1,
            mandato=composicao_vacancia_2026.mandato,
        )

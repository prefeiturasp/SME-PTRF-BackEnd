from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from model_bakery import baker
from waffle import get_waffle_flag_model

from sme_ptrf_apps.core.services.associacoes_service import assinatura_membros_v2

pytestmark = pytest.mark.django_db


def test_assinatura_membros_v2_usa_ocupante_do_cargo_substituto(associacao):
    get_waffle_flag_model().objects.update_or_create(
        name='historico-de-membros-v2',
        defaults={'everyone': True},
    )
    hoje = date.today()
    mandato = baker.make(
        'mandatos.Mandato',
        referencia_mandato='mandato teste assinatura',
        data_inicial=hoje - timedelta(days=10),
        data_final=hoje + timedelta(days=10),
    )
    composicao = baker.make(
        'mandatos.ComposicaoVacancia',
        associacao=associacao,
        mandato=mandato,
    )
    ocupante = baker.make('mandatos.OcupanteCargo', nome='Helena Vogal')
    baker.make(
        'mandatos.CargoComposicaoVacancia',
        composicao=composicao,
        ocupante_do_cargo=ocupante,
        cargo_associacao='VOGAL_2',
        data_inicio_no_cargo=hoje - timedelta(days=5),
        data_fim_no_cargo=hoje + timedelta(days=5),
    )
    associacao.status_presidente = 'PRESENTE'
    associacao.cargo_substituto_presidente_ausente = None
    associacao.save()
    prestacao = SimpleNamespace(
        status_presidente='AUSENTE',
        cargo_substituto_presidente_ausente='VOGAL_2',
        cargo_conselheiro_assinatura=None,
    )

    assinatura = assinatura_membros_v2(associacao, prestacao)

    assert assinatura['presidente_diretoria_executiva'] == 'Helena Vogal'
    assert assinatura['cargo_substituto_presidente_ausente'] == 'Vogal'


def test_assinatura_membros_v2_usa_nome_e_cargo_do_conselheiro_selecionado(associacao):
    get_waffle_flag_model().objects.update_or_create(
        name='historico-de-membros-v2',
        defaults={'everyone': True},
    )
    hoje = date.today()
    mandato = baker.make(
        'mandatos.Mandato',
        referencia_mandato='mandato teste conselheiro',
        data_inicial=hoje - timedelta(days=10),
        data_final=hoje + timedelta(days=10),
    )
    composicao = baker.make(
        'mandatos.ComposicaoVacancia',
        associacao=associacao,
        mandato=mandato,
    )
    tesoureiro = baker.make('mandatos.OcupanteCargo', nome='Carlos Tesoureiro')
    conselheiro = baker.make('mandatos.OcupanteCargo', nome='Maria Conselheira')
    baker.make(
        'mandatos.CargoComposicaoVacancia',
        composicao=composicao,
        ocupante_do_cargo=tesoureiro,
        cargo_associacao='TESOUREIRO',
        data_inicio_no_cargo=hoje - timedelta(days=5),
        data_fim_no_cargo=hoje + timedelta(days=5),
    )
    baker.make(
        'mandatos.CargoComposicaoVacancia',
        composicao=composicao,
        ocupante_do_cargo=conselheiro,
        cargo_associacao='CONSELHEIRO_1',
        data_inicio_no_cargo=hoje - timedelta(days=5),
        data_fim_no_cargo=hoje + timedelta(days=5),
    )
    associacao.status_presidente = 'PRESENTE'
    associacao.cargo_substituto_presidente_ausente = None
    associacao.cargo_conselheiro_assinatura = None
    associacao.save()
    prestacao = SimpleNamespace(
        status_presidente='AUSENTE',
        cargo_substituto_presidente_ausente='TESOUREIRO',
        cargo_conselheiro_assinatura='CONSELHEIRO_1',
    )

    assinatura = assinatura_membros_v2(associacao, prestacao)

    assert assinatura['presidente_diretoria_executiva'] == 'Carlos Tesoureiro'
    assert assinatura['cargo_substituto_presidente_ausente'] == 'Tesoureiro'
    assert assinatura['presidente_conselho_fiscal'] == 'Maria Conselheira'
    assert assinatura['cargo_conselheiro_assinatura'] == 'Conselheiro'


def test_assinatura_membros_v2_sem_prestacao_usa_presidente_e_ignora_associacao(associacao):
    get_waffle_flag_model().objects.update_or_create(
        name='historico-de-membros-v2',
        defaults={'everyone': True},
    )
    associacao.status_presidente = 'AUSENTE'
    associacao.cargo_substituto_presidente_ausente = 'VOGAL_2'
    associacao.cargo_conselheiro_assinatura = 'CONSELHEIRO_1'
    associacao.save()

    assinatura = assinatura_membros_v2(associacao)

    assert assinatura['cargo_substituto_presidente_ausente'] == 'Presidente da Diretoria Executiva'
    assert assinatura['cargo_conselheiro_assinatura'] == 'Presidente do Conselho Fiscal'


def test_assinatura_membros_v2_retorna_none_sem_flag(associacao):
    get_waffle_flag_model().objects.filter(name='historico-de-membros-v2').delete()

    assert assinatura_membros_v2(associacao) is None

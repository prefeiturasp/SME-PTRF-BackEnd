from datetime import date, timedelta

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
    associacao.status_presidente = 'AUSENTE'
    associacao.cargo_substituto_presidente_ausente = 'VOGAL_2'
    associacao.save()

    assinatura = assinatura_membros_v2(associacao)

    assert assinatura['presidente_diretoria_executiva'] == 'Helena Vogal'
    assert assinatura['cargo_substituto_presidente_ausente'] == 'Vogal 2'


def test_assinatura_membros_v2_retorna_none_sem_flag(associacao):
    get_waffle_flag_model().objects.filter(name='historico-de-membros-v2').delete()

    assert assinatura_membros_v2(associacao) is None

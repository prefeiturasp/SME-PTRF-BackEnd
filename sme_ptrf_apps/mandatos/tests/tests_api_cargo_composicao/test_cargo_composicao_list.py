import json
import pytest
from datetime import datetime, timedelta
from rest_framework import status
from waffle.testutils import override_flag
from sme_ptrf_apps.mandatos.models.cargo_composicao import CargoComposicao

pytestmark = pytest.mark.django_db


@override_flag('historico-de-membros', active=True)
def teste_get_cargos_composicao(
    cargo_composicao_01,
    cargo_composicao_02,
    jwt_authenticated_client_sme,
):
    response = jwt_authenticated_client_sme.get(
        f'/api/cargos-composicao/',
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    # ['results'] por causa da paginação na viewset
    assert len(result['results']) == 2


@override_flag('historico-de-membros', active=True)
def teste_get_cargo_composicao(
    cargo_composicao_01,
    cargo_composicao_02,
    ocupante_cargo_01,
    jwt_authenticated_client_sme,
):
    response = jwt_authenticated_client_sme.get(
        f'/api/cargos-composicao/{cargo_composicao_01.uuid}/',
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result['cargo_associacao'] == 'Presidente da diretoria executiva'
    assert result['ocupante_do_cargo']['nome'] == 'Ollyver Ottoboni'


@override_flag('historico-de-membros', active=True)
def teste_get_cargos_composicao_data_fim_no_cargo_composicao_mais_recente(
    cargo_composicao_01,
    cargo_composicao_02,
    jwt_authenticated_client_sme,
):
    response = jwt_authenticated_client_sme.get(
        f'/api/cargos-composicao/',
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    # ['results'] por causa da paginação na viewset
    assert len(result['results']) == 2


@override_flag('historico-de-membros', active=True)
def teste_get_cargos_composicao_cargos_da_composicao_data_fim_no_cargo_composicao_mais_recente(
    mandato_factory,
    composicao_factory,
    cargo_composicao_factory,
    ocupante_cargo_factory,
    jwt_authenticated_client_sme,
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

    cargo_4_vigente = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao_4.data_inicial,
        data_fim_no_cargo=composicao_4.data_final,
        composicao=composicao_4,
        ocupante_do_cargo=presidente_executiva,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    )
    response = jwt_authenticated_client_sme.get(
        f'/api/cargos-composicao/cargos-da-composicao/?composicao_uuid={composicao_2.uuid}',
        content_type='application/json'
    )

    assert response.json()[
        'diretoria_executiva'][0]['data_fim_no_cargo_composicao_mais_recente'] == composicao_4.data_final.strftime("%Y-%m-%d")

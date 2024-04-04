import json
import pytest
from datetime import datetime, timedelta
from rest_framework import status
from waffle.testutils import override_flag
from freezegun import freeze_time
from sme_ptrf_apps.mandatos.models.composicao import Composicao
from sme_ptrf_apps.mandatos.models.cargo_composicao import CargoComposicao

pytestmark = pytest.mark.django_db


@override_flag('historico-de-membros', active=True)
def teste_cargos_composicao_update(
    composicao_01_2023_a_2025,
    cargo_composicao_01,
    ocupante_cargo_01,
    payload_create_cargo_composicao_01_deve_passar,
    jwt_authenticated_client_sme,
):
    uuid_cargo_composicao = f'{cargo_composicao_01.uuid}'

    response = jwt_authenticated_client_sme.put(
        f'/api/cargos-composicao/{uuid_cargo_composicao}/',
        data=json.dumps(payload_create_cargo_composicao_01_deve_passar),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK


@override_flag('historico-de-membros', active=True)
def teste_cargos_composicao_update_encerrar_primeiro_cargo_antes_do_fim_do_mandato(
    jwt_authenticated_client_sme,
    mandato_factory,
    composicao_factory,
    cargo_composicao_factory,
    ocupante_cargo_factory
):
    mandato_2024 = mandato_factory.create(data_inicial=datetime(2024, 1, 1))
    composicao = composicao_factory.create(mandato=mandato_2024,
                                           data_inicial=mandato_2024.data_inicial,
                                           data_final=mandato_2024.data_final)
    presidente_executiva = ocupante_cargo_factory.create()
    presidente_fiscal = ocupante_cargo_factory.create()

    cargo_composicao = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao.data_inicial,
        data_fim_no_cargo=composicao.data_final,
        composicao=composicao,
        ocupante_do_cargo=presidente_executiva,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    )

    cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao.data_inicial,
        data_fim_no_cargo=composicao.data_final,
        composicao=composicao,
        ocupante_do_cargo=presidente_fiscal,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_CONSELHO_FISCAL
    )

    uuid_cargo_composicao = f'{cargo_composicao.uuid}'
    data_fim_no_cargo = cargo_composicao.data_inicio_no_cargo + timedelta(days=30)

    payload = {
        "composicao": f"{composicao.uuid}",
        "ocupante_do_cargo": {
            "nome": f"{presidente_executiva.nome}",
            "codigo_identificacao": f"{presidente_executiva.codigo_identificacao}",
            "cargo_educacao": f"{presidente_executiva.cargo_educacao}",
            "representacao": "SERVIDOR",
            "representacao_label": "Servidor",
            "email": f"{presidente_executiva.email}",
            "cpf_responsavel": f"{presidente_executiva.cpf_responsavel}",
            "telefone": f"{presidente_executiva.telefone}",
            "cep": f"{presidente_executiva.cep}",
            "bairro": f"{presidente_executiva.bairro}",
            "endereco": f"{presidente_executiva.endereco}",
        },

        "cargo_associacao": cargo_composicao.cargo_associacao,
        "substituto": False,
        "substituido": False,
        "data_inicio_no_cargo": cargo_composicao.data_inicio_no_cargo.strftime("%Y-%m-%d"),
        "data_fim_no_cargo": cargo_composicao.data_fim_no_cargo.strftime("%Y-%m-%d"),
        "data_saida_do_cargo": data_fim_no_cargo.strftime("%Y-%m-%d"),
    }

    response = jwt_authenticated_client_sme.put(
        f'/api/cargos-composicao/{uuid_cargo_composicao}/',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK

    composicao_finalizada = Composicao.objects.filter(associacao=composicao.associacao,
                                                      data_final=data_fim_no_cargo).first()
    assert composicao_finalizada is not None

    for item in composicao_finalizada.cargos_da_composicao_da_composicao.all():
        assert item.data_fim_no_cargo.strftime("%Y-%m-%d") == composicao_finalizada.data_final.strftime("%Y-%m-%d")


@override_flag('historico-de-membros', active=True)
def teste_cargos_composicao_update_encerrar_segundo_cargo_antes_do_fim_do_mandato(
    jwt_authenticated_client_sme,
    mandato_factory,
    composicao_factory,
    cargo_composicao_factory,
    ocupante_cargo_factory
):
    mandato_2024 = mandato_factory.create(data_inicial=datetime(2024, 1, 1))
    composicao_encerrada = composicao_factory.create(
        mandato=mandato_2024, data_inicial=mandato_2024.data_inicial, data_final=mandato_2024.data_inicial + timedelta(days=30))

    composicao = composicao_factory.create(mandato=mandato_2024,
                                           data_inicial=composicao_encerrada.data_final + timedelta(days=1),
                                           data_final=mandato_2024.data_final)

    presidente_executiva = ocupante_cargo_factory.create()
    presidente_fiscal = ocupante_cargo_factory.create()

    cargo_composicao_encerrado = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao_encerrada.data_inicial,
        data_fim_no_cargo=composicao_encerrada.data_final,
        composicao=composicao_encerrada,
        ocupante_do_cargo=presidente_executiva,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    )

    cargo_composicao = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao.data_inicial,
        data_fim_no_cargo=composicao.data_final,
        composicao=composicao,
        ocupante_do_cargo=presidente_fiscal,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_CONSELHO_FISCAL
    )

    uuid_cargo_composicao = f'{cargo_composicao.uuid}'
    data_fim_no_cargo = cargo_composicao_encerrado.data_fim_no_cargo

    payload = {
        "composicao": f"{composicao.uuid}",
        "ocupante_do_cargo": {
            "nome": f"{presidente_executiva.nome}",
            "codigo_identificacao": f"{presidente_executiva.codigo_identificacao}",
            "cargo_educacao": f"{presidente_executiva.cargo_educacao}",
            "representacao": "SERVIDOR",
            "representacao_label": "Servidor",
            "email": f"{presidente_executiva.email}",
            "cpf_responsavel": f"{presidente_executiva.cpf_responsavel}",
            "telefone": f"{presidente_executiva.telefone}",
            "cep": f"{presidente_executiva.cep}",
            "bairro": f"{presidente_executiva.bairro}",
            "endereco": f"{presidente_executiva.endereco}",
        },

        "cargo_associacao": cargo_composicao.cargo_associacao,
        "substituto": False,
        "substituido": False,
        "data_inicio_no_cargo": cargo_composicao.data_inicio_no_cargo.strftime("%Y-%m-%d"),
        "data_fim_no_cargo": cargo_composicao.data_fim_no_cargo.strftime("%Y-%m-%d"),
        "data_saida_do_cargo": data_fim_no_cargo.strftime("%Y-%m-%d"),
    }

    response = jwt_authenticated_client_sme.put(
        f'/api/cargos-composicao/{uuid_cargo_composicao}/',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK

    assert Composicao.objects.all().count() == 2

    assert not CargoComposicao.objects.filter(uuid=uuid_cargo_composicao).exists()


@override_flag('historico-de-membros', active=True)
def teste_cargos_composicao_update_deve_retornar_erro_data_inicio_no_cargo_menor_que_data_inicio_composicao(
    composicao_01_2023_a_2025,
    cargo_composicao_01,
    ocupante_cargo_01,
    payload_create_cargo_composicao_01_deve_passar,
    jwt_authenticated_client_sme,
):
    payload_create_cargo_composicao_01_deve_passar['data_inicio_no_cargo'] = "2022-01-01"
    payload_create_cargo_composicao_01_deve_passar['data_fim_no_cargo'] = "2025-12-31"

    uuid_cargo_composicao = f'{cargo_composicao_01.uuid}'

    response = jwt_authenticated_client_sme.put(
        f'/api/cargos-composicao/{uuid_cargo_composicao}/',
        data=json.dumps(payload_create_cargo_composicao_01_deve_passar),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == {
        'non_field_errors': ['Não é permitido informar período inicial de ocupação '
                             'anterior ao período inicial do mandato'],
    }


@override_flag('historico-de-membros', active=True)
def teste_cargos_composicao_update_deve_retornar_erro_data_inicio_no_cargo_maior_que_data_fim_composicao(
    composicao_01_2023_a_2025,
    cargo_composicao_01,
    ocupante_cargo_01,
    payload_create_cargo_composicao_01_deve_passar,
    jwt_authenticated_client_sme,
):
    payload_create_cargo_composicao_01_deve_passar['data_inicio_no_cargo'] = "2026-01-01"
    payload_create_cargo_composicao_01_deve_passar['data_fim_no_cargo'] = "2025-12-31"

    uuid_cargo_composicao = f'{cargo_composicao_01.uuid}'

    response = jwt_authenticated_client_sme.put(
        f'/api/cargos-composicao/{uuid_cargo_composicao}/',
        data=json.dumps(payload_create_cargo_composicao_01_deve_passar),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == {
        'non_field_errors': ['Não é permitido informar período inicial de ocupação '
                             'posterior ao período final do mandato.'],
    }


@override_flag('historico-de-membros', active=True)
def teste_cargos_composicao_update_deve_retornar_erro_data_inicio_no_cargo_maior_que_data_fim_no_cargo(
    composicao_01_2023_a_2025,
    cargo_composicao_01,
    ocupante_cargo_01,
    payload_create_cargo_composicao_01_deve_passar,
    jwt_authenticated_client_sme,
):
    payload_create_cargo_composicao_01_deve_passar['data_inicio_no_cargo'] = "2025-12-31"
    payload_create_cargo_composicao_01_deve_passar['data_fim_no_cargo'] = "2025-12-30"

    uuid_cargo_composicao = f'{cargo_composicao_01.uuid}'

    response = jwt_authenticated_client_sme.put(
        f'/api/cargos-composicao/{uuid_cargo_composicao}/',
        data=json.dumps(payload_create_cargo_composicao_01_deve_passar),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == {
        'non_field_errors': ['Não é permitido informar período inicial de ocupação '
                             'posterior ao período final de ocupação'],
    }


@override_flag('historico-de-membros', active=True)
def teste_cargos_composicao_update_deve_retornar_erro_duplicidade_codigo_identificacao(
    composicao_01_2023_a_2025,
    ocupante_cargo_01,
    ocupante_cargo_02,
    cargo_composicao_01,
    cargo_composicao_02,
    payload_create_cargo_composicao_01_deve_passar,
    jwt_authenticated_client_sme,
):
    uuid_cargo_composicao = f'{cargo_composicao_02.uuid}'

    response = jwt_authenticated_client_sme.put(
        f'/api/cargos-composicao/{uuid_cargo_composicao}/',
        data=json.dumps(payload_create_cargo_composicao_01_deve_passar),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == {
        'non_field_errors': [
            'Já existe um Membro cadastrado nessa composição com o mesmo Codigo de identificação. Verifique por favor.']
    }


@override_flag('historico-de-membros', active=True)
def teste_cargos_composicao_update_deve_retornar_erro_duplicidade_cpf_responsavel(
    composicao_01_2023_a_2025,
    ocupante_cargo_01,
    ocupante_cargo_02,
    cargo_composicao_01,
    cargo_composicao_02,
    payload_create_cargo_composicao_01_deve_passar,
    jwt_authenticated_client_sme,
):
    payload_create_cargo_composicao_01_deve_passar['ocupante_do_cargo']['codigo_identificacao'] = "7777777"

    uuid_cargo_composicao = f'{cargo_composicao_01.uuid}'

    response = jwt_authenticated_client_sme.put(
        f'/api/cargos-composicao/{uuid_cargo_composicao}/',
        data=json.dumps(payload_create_cargo_composicao_01_deve_passar),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == {
        'non_field_errors': [
            'Já existe um Membro cadastrado nessa composição com o mesmo CPF. Verifique por favor.']
    }


@override_flag('historico-de-membros', active=True)
@freeze_time('2024-02-06 10:11:12')
def teste_cargos_composicao_update_deve_retornar_erro_data_saida_do_cargo_maior_que_data_atual(
    composicao_01_2023_a_2025,
    ocupante_cargo_01,
    ocupante_cargo_02,
    cargo_composicao_01,
    cargo_composicao_02,
    payload_update_cargo_composicao_data_saida_do_cargo_maior_que_data_atual,
    jwt_authenticated_client_sme,
):
    payload_update_cargo_composicao_data_saida_do_cargo_maior_que_data_atual[
        'ocupante_do_cargo']['codigo_identificacao'] = "7777777"

    uuid_cargo_composicao = f'{cargo_composicao_01.uuid}'

    response = jwt_authenticated_client_sme.put(
        f'/api/cargos-composicao/{uuid_cargo_composicao}/',
        data=json.dumps(payload_update_cargo_composicao_data_saida_do_cargo_maior_que_data_atual),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == {
        'non_field_errors': [
            'Não é permitido informar a data de saída do cargo posterior a data atual']
    }


@override_flag('historico-de-membros', active=True)
@freeze_time('2024-02-06 10:11:12')
def teste_cargos_composicao_update_deve_retornar_erro_data_saida_do_cargo_maior_que_data_final_mandato(
    composicao_01_2023_a_2025,
    ocupante_cargo_01,
    ocupante_cargo_02,
    cargo_composicao_01,
    cargo_composicao_02,
    payload_update_cargo_composicao_data_saida_do_cargo_maior_ou_igual_que_data_final_mandato,
    jwt_authenticated_client_sme,
):
    payload_update_cargo_composicao_data_saida_do_cargo_maior_ou_igual_que_data_final_mandato[
        'ocupante_do_cargo']['codigo_identificacao'] = "7777777"

    uuid_cargo_composicao = f'{cargo_composicao_01.uuid}'

    response = jwt_authenticated_client_sme.put(
        f'/api/cargos-composicao/{uuid_cargo_composicao}/',
        data=json.dumps(payload_update_cargo_composicao_data_saida_do_cargo_maior_ou_igual_que_data_final_mandato),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == {
        'non_field_errors': [
            'A data de saída do cargo deve ser anterior a data final do mandato.']
    }


@override_flag('historico-de-membros', active=True)
@freeze_time('2024-02-06 10:11:12')
def teste_cargos_composicao_update_deve_retornar_erro_data_saida_do_cargo_anterior_data_final_da_composicao_anterior(
    composicao_01_testes_data_saida_do_cargo,
    composicao_02_testes_data_saida_do_cargo,
    ocupante_cargo_01,
    cargo_composicao_01_testes_data_saida_do_cargo,
    payload_update_cargo_composicao_data_saida_do_cargo_anterior_data_final_da_composicao_anterior,
    jwt_authenticated_client_sme,
):
    payload_update_cargo_composicao_data_saida_do_cargo_anterior_data_final_da_composicao_anterior[
        'ocupante_do_cargo']['codigo_identificacao'] = "7777777"

    uuid_cargo_composicao = f'{cargo_composicao_01_testes_data_saida_do_cargo.uuid}'

    response = jwt_authenticated_client_sme.put(
        f'/api/cargos-composicao/{uuid_cargo_composicao}/',
        data=json.dumps(payload_update_cargo_composicao_data_saida_do_cargo_anterior_data_final_da_composicao_anterior),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == {
        'non_field_errors': [
            'Não é permitido informar a data de saída do cargo anterior a data final da composição anterior']
    }

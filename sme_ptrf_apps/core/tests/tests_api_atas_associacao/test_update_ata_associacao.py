import datetime
import json

import pytest
from rest_framework import status

from ...models import Ata, PrestacaoConta

pytestmark = pytest.mark.django_db


def _payload_edicao_ata():
    return {
        "tipo_reuniao": "EXTRAORDINARIA",
        "convocacao": "SEGUNDA",
        "data_reuniao": "2020-06-20",
        "local_reuniao": "Sala XXX",
        "presidente_reuniao": "PedroXXX",
        "cargo_presidente_reuniao": "PresidenteXXX",
        "secretario_reuniao": "MariaXXX",
        "cargo_secretaria_reuniao": "SecretáriaXXX",
        "parecer_conselho": "REJEITADA",
        "comentarios": "TesteXXX",
        'presentes_na_ata': [],
    }


def test_api_update_ata_associacao(jwt_authenticated_client_a, ata_apresentacao):

    payload = _payload_edicao_ata()

    response = jwt_authenticated_client_a.patch(
        f'/api/atas-associacao/{ata_apresentacao.uuid}/',
        data=json.dumps(payload),
        content_type='application/json',
    )

    registro_alterado = Ata.by_uuid(uuid=ata_apresentacao.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert registro_alterado.tipo_reuniao == 'EXTRAORDINARIA'
    assert registro_alterado.convocacao == "SEGUNDA"
    assert registro_alterado.data_reuniao == datetime.date(2020, 6, 20)
    assert registro_alterado.local_reuniao == "Sala XXX"
    assert registro_alterado.presidente_reuniao == "PedroXXX"
    assert registro_alterado.cargo_presidente_reuniao == "PresidenteXXX"
    assert registro_alterado.secretario_reuniao == "MariaXXX"
    assert registro_alterado.cargo_secretaria_reuniao == "SecretáriaXXX"
    assert registro_alterado.parecer_conselho == "REJEITADA"
    assert registro_alterado.comentarios == "TesteXXX"


def test_api_update_ata_apresentacao_bloqueada_quando_pdf_gerado_e_pc_recebida(
    jwt_authenticated_client_a, ata_apresentacao,
):
    ata_apresentacao.prestacao_conta.status = PrestacaoConta.STATUS_RECEBIDA
    ata_apresentacao.prestacao_conta.save()
    ata_apresentacao.status_geracao_pdf = Ata.STATUS_CONCLUIDO
    ata_apresentacao.save()

    response = jwt_authenticated_client_a.patch(
        f'/api/atas-associacao/{ata_apresentacao.uuid}/',
        data=json.dumps(_payload_edicao_ata()),
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'retificação' in response.json()['mensagem'].lower()

    registro = Ata.by_uuid(uuid=ata_apresentacao.uuid)
    assert registro.presidente_reuniao == 'José'


def test_api_update_ata_apresentacao_bloqueada_quando_pdf_gerado_previamente_e_pc_em_analise(
    jwt_authenticated_client_a, ata_apresentacao,
):
    ata_apresentacao.prestacao_conta.status = PrestacaoConta.STATUS_EM_ANALISE
    ata_apresentacao.prestacao_conta.save()
    ata_apresentacao.status_geracao_pdf = Ata.STATUS_NAO_GERADO
    ata_apresentacao.pdf_gerado_previamente = True
    ata_apresentacao.save()

    response = jwt_authenticated_client_a.patch(
        f'/api/atas-associacao/{ata_apresentacao.uuid}/',
        data=json.dumps(_payload_edicao_ata()),
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'retificação' in response.json()['mensagem'].lower()


def test_api_update_ata_apresentacao_permitida_quando_pdf_gerado_e_pc_nao_recebida(
    jwt_authenticated_client_a, ata_apresentacao,
):
    ata_apresentacao.prestacao_conta.status = PrestacaoConta.STATUS_NAO_RECEBIDA
    ata_apresentacao.prestacao_conta.save()
    ata_apresentacao.status_geracao_pdf = Ata.STATUS_CONCLUIDO
    ata_apresentacao.save()

    response = jwt_authenticated_client_a.patch(
        f'/api/atas-associacao/{ata_apresentacao.uuid}/',
        data=json.dumps(_payload_edicao_ata()),
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert Ata.by_uuid(uuid=ata_apresentacao.uuid).presidente_reuniao == 'PedroXXX'

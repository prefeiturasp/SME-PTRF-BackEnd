import datetime
import json

import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import PrestacaoConta, Ata

from model_bakery import baker

from datetime import date

from freezegun import freeze_time

from django.core.files.uploadedfile import SimpleUploadedFile

pytestmark = pytest.mark.django_db


@pytest.fixture
def periodo_anterior_01():
    return baker.make(
        'Periodo',
        referencia='2019.1',
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 8, 31),
    )


@pytest.fixture
def periodo_01(periodo_anterior_01):
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 9, 1),
        data_fim_realizacao_despesas=date(2019, 11, 30),
        data_prevista_repasse=date(2019, 10, 1),
        data_inicio_prestacao_contas=date(2019, 12, 1),
        data_fim_prestacao_contas=date(2019, 12, 5),
        periodo_anterior=periodo_anterior_01,
    )


@pytest.fixture
def prestacao_conta_01(periodo_01, associacao, motivo_aprovacao_ressalva_x, motivo_reprovacao_x):
    return baker.make(
        'PrestacaoConta',
        id=1,
        periodo=periodo_01,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        data_ultima_analise=date(2020, 10, 1),
        motivos_reprovacao=[motivo_reprovacao_x, ],
        outros_motivos_reprovacao="Outros motivos reprovacao",
        motivos_aprovacao_ressalva=[motivo_aprovacao_ressalva_x, ],
        outros_motivos_aprovacao_ressalva="Outros motivos")


@pytest.fixture
def prestacao_conta_02(periodo, associacao, motivo_aprovacao_ressalva_x, motivo_reprovacao_x):
    return baker.make(
        'PrestacaoConta',
        id=2,
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 2),
        data_ultima_analise=date(2020, 10, 2),
        motivos_reprovacao=[motivo_reprovacao_x, ],
        outros_motivos_reprovacao="Outros motivos reprovacao",
        motivos_aprovacao_ressalva=[motivo_aprovacao_ressalva_x, ],
        outros_motivos_aprovacao_ressalva="Outros motivos")


@pytest.fixture
@freeze_time('2022-06-25 13:59:00')
def arquivo_gerado_ata_apresentacao_pc():
    return SimpleUploadedFile(f'arquivo.txt', bytes(f'CONTEUDO TESTE TESTE TESTE', encoding="utf-8"))


@pytest.fixture
def ata_teste_reabrir_pc_nao_apaga_ata(
    prestacao_conta_01,
    arquivo_gerado_ata_apresentacao_pc
):
    return baker.make(
        'Ata',
        arquivo_pdf=arquivo_gerado_ata_apresentacao_pc,
        prestacao_conta=prestacao_conta_01,
        periodo=prestacao_conta_01.periodo,
        associacao=prestacao_conta_01.associacao,
        tipo_ata='APRESENTACAO',
        tipo_reuniao='ORDINARIA',
        convocacao='PRIMEIRA',
        status_geracao_pdf='CONCLUIDO',
        data_reuniao=datetime.date(2020, 7, 1),
        local_reuniao='Escola Teste',
        presidente_reuniao='José',
        cargo_presidente_reuniao='Presidente',
        secretario_reuniao='Ana',
        cargo_secretaria_reuniao='Secretária',
        comentarios='Teste',
        parecer_conselho='APROVADA',
        previa=False,
    )


def test_api_reabre_prestacao_conta_e_nao_apaga_ata(
    jwt_authenticated_client_a,
    prestacao_conta_01,
    ata_teste_reabrir_pc_nao_apaga_ata,
    arquivo_gerado_ata_apresentacao_pc,
):
    uuid_pc = prestacao_conta_01.uuid

    uuid_ata = ata_teste_reabrir_pc_nao_apaga_ata.uuid

    ata = Ata.by_uuid(uuid_ata)

    assert ata.prestacao_conta == prestacao_conta_01
    assert not ata.previa
    assert ata.arquivo_pdf == arquivo_gerado_ata_apresentacao_pc
    assert ata.status_geracao_pdf == 'CONCLUIDO'

    url = f'/api/prestacoes-contas/{uuid_pc}/reabrir/'

    response = jwt_authenticated_client_a.delete(url, content_type='application/json')

    ata = Ata.by_uuid(uuid_ata)

    assert not ata.prestacao_conta
    assert ata.previa
    assert not ata.arquivo_pdf
    assert ata.status_geracao_pdf == 'NAO_GERADO'

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not PrestacaoConta.objects.filter(uuid=uuid_pc).exists(), 'Não apagou a PC'


def test_api_reabre_prestacao_conta(jwt_authenticated_client_a, prestacao_conta):
    url = f'/api/prestacoes-contas/{prestacao_conta.uuid}/reabrir/'

    response = jwt_authenticated_client_a.delete(url, content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not PrestacaoConta.objects.filter(uuid=prestacao_conta.uuid).exists(), 'Não apagou a PC'


def test_api_nao_reabre_prestacao_conta_pc_posterior(jwt_authenticated_client_a, prestacao_conta_01,
                                                     prestacao_conta_02):
    url = f'/api/prestacoes-contas/{prestacao_conta_01.uuid}/reabrir/'

    response = jwt_authenticated_client_a.delete(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{prestacao_conta_01.uuid}',
        'erro': 'prestacao_de_contas_posteriores',
        'operacao': 'reabrir',
        'mensagem': 'Essa prestação de contas não pode ser devolvida, ou reaberta porque há prestação de contas dessa associação de um período posterior. Se necessário, reabra ou devolva primeiro a prestação de contas mais recente.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == result_esperado

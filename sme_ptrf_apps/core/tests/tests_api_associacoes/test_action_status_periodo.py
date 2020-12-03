import json
import pytest

from datetime import date

from freezegun import freeze_time
from model_bakery import baker
from rest_framework import status

from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db


@freeze_time('2020-01-10 10:11:12')
def test_status_periodo_em_andamento(jwt_authenticated_client_a, associacao, periodo_fim_em_aberto):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/status-periodo/?data=2020-01-10',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'periodo_referencia': periodo_fim_em_aberto.referencia,
        'aceita_alteracoes': True,
        'prestacao_contas_status': {
            'documentos_gerados': None,
            'legenda_cor': 1,
            'periodo_bloqueado': False,
            'periodo_encerrado': None,
            'status_prestacao': 'NAO_APRESENTADA',
            'texto_status': 'Período em andamento. ',
        },
        'prestacao_conta': '',

    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


@freeze_time('2020-07-10 10:20:00')
def test_status_periodo_pendente(jwt_authenticated_client_a, associacao, periodo_fim_em_2020_06_30):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/status-periodo/?data=2020-01-10',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'periodo_referencia': periodo_fim_em_2020_06_30.referencia,
        'aceita_alteracoes': True,
        'prestacao_contas_status': {
            'documentos_gerados': None,
            'legenda_cor': 3,
            'periodo_bloqueado': False,
            'periodo_encerrado': True,
            'status_prestacao': 'NAO_APRESENTADA',
            'texto_status': 'Período finalizado. Documentos pendentes de geração.',
        },
        'prestacao_conta': '',

    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_chamada_sem_passar_data(jwt_authenticated_client_a, associacao, periodo_2020_1, prestacao_conta_2020_1_conciliada):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/status-periodo/',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'erro': 'parametros_requerido',
        'mensagem': 'É necessário enviar a data que você quer consultar o status.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado


def test_chamada_data_sem_periodo(jwt_authenticated_client_a, associacao, periodo_2020_1):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/status-periodo/?data=2000-01-10',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'periodo_referencia': '',
        'aceita_alteracoes': True,
        'prestacao_contas_status': {},
        'prestacao_conta': '',
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


@freeze_time('2020-07-10 10:20:00')
def test_status_periodo_finalizado(jwt_authenticated_client_a, associacao, prestacao_conta_2020_1_conciliada):
    periodo = prestacao_conta_2020_1_conciliada.periodo

    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/status-periodo/?data={periodo.data_inicio_realizacao_despesas}',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'periodo_referencia': periodo.referencia,
        'aceita_alteracoes': False,
        'prestacao_contas_status': {
            'documentos_gerados': True,
            'legenda_cor': 2,
            'periodo_bloqueado': True,
            'periodo_encerrado': True,
            'status_prestacao': 'NAO_RECEBIDA',
            'texto_status': 'Período finalizado. Prestação de contas ainda não recebida pela DRE.',
        },
        'prestacao_conta': f'{prestacao_conta_2020_1_conciliada.uuid}',

    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado



@pytest.fixture
def _prestacao_conta_devolvida(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        data_ultima_analise=date(2020, 10, 1),
        status=PrestacaoConta.STATUS_DEVOLVIDA
    )


@freeze_time('2020-07-10 10:20:00')
def test_status_periodo_devolvido_para_acertos(jwt_authenticated_client_a, associacao, _prestacao_conta_devolvida):
    periodo = _prestacao_conta_devolvida.periodo

    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/status-periodo/?data={periodo.data_inicio_realizacao_despesas}',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'periodo_referencia': periodo.referencia,
        'aceita_alteracoes': True,
        'prestacao_contas_status': {
            'documentos_gerados': False,
            'legenda_cor': 3,
            'periodo_bloqueado': False,
            'periodo_encerrado': True,
            'status_prestacao': 'DEVOLVIDA',
            'texto_status': 'Período finalizado. Prestação de contas devolvida para ajustes.',
        },
        'prestacao_conta': f'{_prestacao_conta_devolvida.uuid}',

    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado

import json

import pytest
from model_bakery import baker
from rest_framework import status
from ...models import RelatorioConsolidadoDRE
from ...services import gera_relatorio_dre

pytestmark = pytest.mark.django_db


@pytest.fixture
def ano_analise_regularidade_2019():
    return baker.make('AnoAnaliseRegularidade', ano=2019)

def test_api_geracao_relatorio_final(jwt_authenticated_client_relatorio_consolidado, periodo, dre, tipo_conta):
    payload = {
        'dre_uuid': str(dre.uuid),
        'periodo_uuid': str(periodo.uuid),
        'tipo_conta_uuid': str(tipo_conta.uuid),
        'parcial': False
    }

    response = jwt_authenticated_client_relatorio_consolidado.post(
        '/api/relatorios-consolidados-dre/gerar-relatorio/',
        data=json.dumps(payload),
        content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED


def test_api_geracao_relatorio_sem_dre_uuid(jwt_authenticated_client_relatorio_consolidado, periodo, dre, tipo_conta):
    payload = {
        'dre_uuid': '',
        'periodo_uuid': str(periodo.uuid),
        'tipo_conta_uuid': str(tipo_conta.uuid),
        'parcial': False
    }

    response = jwt_authenticated_client_relatorio_consolidado.post(
        f'/api/relatorios-consolidados-dre/gerar-relatorio/',
        data=json.dumps(payload),
        content_type='application/json')

    result = json.loads(response.content)
    esperado = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário enviar os uuids da dre, período, conta e parcial.'
    }

    assert result == esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_api_geracao_relatorio_sem_periodo_uuid(jwt_authenticated_client_relatorio_consolidado, periodo, dre, tipo_conta):
    payload = {
        'dre_uuid': str(dre.uuid),
        'periodo_uuid': '',
        'tipo_conta_uuid': str(tipo_conta.uuid),
        'parcial': False
    }

    response = jwt_authenticated_client_relatorio_consolidado.post(
        f'/api/relatorios-consolidados-dre/gerar-relatorio/',
        data=json.dumps(payload),
        content_type='application/json')

    result = json.loads(response.content)
    esperado = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário enviar os uuids da dre, período, conta e parcial.'
    }

    assert result == esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_api_geracao_relatorio_objeto_nao_encontrado(jwt_authenticated_client_relatorio_consolidado, periodo, dre, tipo_conta):
    import uuid
    uuid_objeto = str(uuid.uuid4())
    payload = {
        'dre_uuid': str(dre.uuid),
        'periodo_uuid': uuid_objeto,
        'tipo_conta_uuid': str(tipo_conta.uuid),
        'parcial': False
    }

    response = jwt_authenticated_client_relatorio_consolidado.post(
        f'/api/relatorios-consolidados-dre/gerar-relatorio/',
        data=json.dumps(payload),
        content_type='application/json')

    result = json.loads(response.content)
    esperado = {
        'erro': 'Objeto não encontrado.',
        'mensagem': 'O objeto período para o uuid '
                    f'{uuid_objeto} não foi encontrado na base.',
    }

    assert result == esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_api_geracao_relatorio_parcial(jwt_authenticated_client_relatorio_consolidado, periodo, dre, tipo_conta):
    payload = {
        'dre_uuid': str(dre.uuid),
        'periodo_uuid': str(periodo.uuid),
        'tipo_conta_uuid': str(tipo_conta.uuid),
        'parcial': True
    }

    response = jwt_authenticated_client_relatorio_consolidado.post(
        f'/api/relatorios-consolidados-dre/gerar-relatorio/',
        data=json.dumps(payload),
        content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED


def test_api_geracao_previa_relatorio_sem_dre_uuid(jwt_authenticated_client_relatorio_consolidado, periodo, dre, tipo_conta):
    payload = {
        'dre_uuid': '',
        'periodo_uuid': str(periodo.uuid),
        'tipo_conta_uuid': str(tipo_conta.uuid),
        'parcial': False
    }

    response = jwt_authenticated_client_relatorio_consolidado.post(
        f'/api/relatorios-consolidados-dre/gerar-relatorio/',
        data=json.dumps(payload),
        content_type='application/json')

    result = json.loads(response.content)
    esperado = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário enviar os uuids da dre, período, conta e parcial.'
    }

    assert result == esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_api_geracao_previa_relatorio_sem_periodo_uuid(jwt_authenticated_client_relatorio_consolidado, periodo, dre, tipo_conta):
    payload = {
        'dre_uuid': str(dre.uuid),
        'periodo_uuid': '',
        'tipo_conta_uuid': str(tipo_conta.uuid),
        'parcial': False
    }

    response = jwt_authenticated_client_relatorio_consolidado.post(
        f'/api/relatorios-consolidados-dre/gerar-relatorio/',
        data=json.dumps(payload),
        content_type='application/json')

    result = json.loads(response.content)
    esperado = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário enviar os uuids da dre, período, conta e parcial.'
    }

    assert result == esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_api_geracao_previa_relatorio_objeto_nao_encontrado(jwt_authenticated_client_relatorio_consolidado, periodo, dre, tipo_conta):
    import uuid
    uuid_objeto = str(uuid.uuid4())
    payload = {
        'dre_uuid': str(dre.uuid),
        'periodo_uuid': uuid_objeto,
        'tipo_conta_uuid': str(tipo_conta.uuid),
        'parcial': False
    }

    response = jwt_authenticated_client_relatorio_consolidado.post(
        f'/api/relatorios-consolidados-dre/gerar-relatorio/',
        data=json.dumps(payload),
        content_type='application/json')

    result = json.loads(response.content)
    esperado = {
        'erro': 'Objeto não encontrado.',
        'mensagem': 'O objeto período para o uuid '
                    f'{uuid_objeto} não foi encontrado na base.',
    }

    assert result == esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_gerar_relatorio_final(periodo, dre, tipo_conta, ano_analise_regularidade_2019):
    gera_relatorio_dre(dre, periodo, tipo_conta)

    assert RelatorioConsolidadoDRE.objects.exists()
    assert RelatorioConsolidadoDRE.objects.first().status == RelatorioConsolidadoDRE.STATUS_GERADO_TOTAL


def test_gerar_relatorio_parcial(periodo, dre, tipo_conta, ano_analise_regularidade_2019):
    gera_relatorio_dre(dre, periodo, tipo_conta, True)

    assert RelatorioConsolidadoDRE.objects.exists()
    assert RelatorioConsolidadoDRE.objects.first().status == RelatorioConsolidadoDRE.STATUS_GERADO_PARCIAL

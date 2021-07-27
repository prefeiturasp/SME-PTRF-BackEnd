import json

import pytest

from freezegun import freeze_time
from django.core.files.uploadedfile import SimpleUploadedFile

from datetime import date
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_status_relatorio_analise_completa_rel_nao_gerado(jwt_authenticated_client_relatorio_consolidado, dre,
                                                                  periodo, tipo_conta):
    response = jwt_authenticated_client_relatorio_consolidado.get(
        f'/api/relatorios-consolidados-dre/status-relatorio/?dre={dre.uuid}&periodo={periodo.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'pcs_em_analise': False,
        'status_geracao': 'NAO_GERADO',
        'status_txt': 'Análise de prestações de contas das associações completa. Relatório não gerado.',
        'cor_idx': 2,
        'status_arquivo': 'Documento pendente de geração',
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


@pytest.fixture
def prestacao_conta_em_analise(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        status='EM_ANALISE'
    )


def test_api_get_status_relatorio_analise_pendente_rel_nao_gerado(jwt_authenticated_client_relatorio_consolidado, dre,
                                                                  periodo, tipo_conta,
                                                                  prestacao_conta_em_analise):
    response = jwt_authenticated_client_relatorio_consolidado.get(
        f'/api/relatorios-consolidados-dre/status-relatorio/?dre={dre.uuid}&periodo={periodo.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'pcs_em_analise': True,
        'status_geracao': 'NAO_GERADO',
        'status_txt': 'Ainda constam prestações de contas das associações em análise. Relatório não gerado.',
        'cor_idx': 0,
        'status_arquivo': 'Documento pendente de geração'
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


@pytest.fixture
@freeze_time('2020-10-27 13:59:00')
def arquivo_gerado_em_2020_10_27_13_59_00():
    return SimpleUploadedFile(f'arquivo.txt', bytes(f'CONTEUDO TESTE TESTE TESTE', encoding="utf-8"))


@pytest.fixture
@freeze_time('2020-10-27 13:59:00')
def relatorio_dre_consolidado_gerado_parcial_em_2020_10_27_13_59_00(periodo, dre, tipo_conta,
                                                                    arquivo_gerado_em_2020_10_27_13_59_00):
    return baker.make(
        'RelatorioConsolidadoDre',
        dre=dre,
        tipo_conta=tipo_conta,
        periodo=periodo,
        arquivo=arquivo_gerado_em_2020_10_27_13_59_00,
        status='GERADO_PARCIAL'
    )


def test_api_get_status_relatorio_analise_pendente_rel_parcial_gerado(jwt_authenticated_client_relatorio_consolidado,
                                                                      dre, periodo,
                                                                      tipo_conta,
                                                                      prestacao_conta_em_analise,
                                                                      relatorio_dre_consolidado_gerado_parcial_em_2020_10_27_13_59_00):
    response = jwt_authenticated_client_relatorio_consolidado.get(
        f'/api/relatorios-consolidados-dre/status-relatorio/?dre={dre.uuid}&periodo={periodo.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'pcs_em_analise': True,
        'status_geracao': 'GERADO_PARCIAL',
        'status_txt': 'Ainda constam prestações de contas das associações em análise. Relatório parcial gerado.',
        'cor_idx': 1,
        'status_arquivo': 'Documento parcial gerado dia 27/10/2020 13:59'
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_get_status_relatorio_analise_completa_rel_parcial_gerado(jwt_authenticated_client_relatorio_consolidado,
                                                                      dre, periodo,
                                                                      tipo_conta,
                                                                      relatorio_dre_consolidado_gerado_parcial_em_2020_10_27_13_59_00):
    response = jwt_authenticated_client_relatorio_consolidado.get(
        f'/api/relatorios-consolidados-dre/status-relatorio/?dre={dre.uuid}&periodo={periodo.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'pcs_em_analise': False,
        'status_geracao': 'GERADO_PARCIAL',
        'status_txt': 'Análise de prestações de contas das associações completa. Relatório parcial gerado.',
        'cor_idx': 2,
        'status_arquivo': 'Documento parcial gerado dia 27/10/2020 13:59'
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


@pytest.fixture
@freeze_time('2020-10-27 13:59:00')
def relatorio_dre_consolidado_gerado_total_em_2020_10_27_13_59_00(periodo, dre, tipo_conta,
                                                                  arquivo_gerado_em_2020_10_27_13_59_00):
    return baker.make(
        'RelatorioConsolidadoDre',
        dre=dre,
        tipo_conta=tipo_conta,
        periodo=periodo,
        arquivo=arquivo_gerado_em_2020_10_27_13_59_00,
        status='GERADO_TOTAL'
    )


def test_api_get_status_relatorio_analise_completa_rel_final_gerado(jwt_authenticated_client_relatorio_consolidado, dre,
                                                                    periodo,
                                                                    tipo_conta,
                                                                    relatorio_dre_consolidado_gerado_total_em_2020_10_27_13_59_00):
    response = jwt_authenticated_client_relatorio_consolidado.get(
        f'/api/relatorios-consolidados-dre/status-relatorio/?dre={dre.uuid}&periodo={periodo.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'pcs_em_analise': False,
        'status_geracao': 'GERADO_TOTAL',
        'status_txt': 'Análise de prestações de contas das associações completa. Relatório final gerado.',
        'cor_idx': 3,
        'status_arquivo': 'Documento final gerado dia 27/10/2020 13:59'
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_get_status_relatorio_sem_passa_dre(jwt_authenticated_client_relatorio_consolidado, dre, periodo,
                                                tipo_conta):
    response = jwt_authenticated_client_relatorio_consolidado.get(
        f'/api/relatorios-consolidados-dre/status-relatorio/?periodo={periodo.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre',
        'operacao': 'status-relatorio'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado


def test_api_get_status_relatorio_sem_passa_periodo(jwt_authenticated_client_relatorio_consolidado, dre, periodo,
                                                    tipo_conta):
    response = jwt_authenticated_client_relatorio_consolidado.get(
        f'/api/relatorios-consolidados-dre/status-relatorio/?dre={dre.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo',
        'operacao': 'status-relatorio'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado


def test_api_get_status_relatorio_sem_passar_tipo_conta(jwt_authenticated_client_relatorio_consolidado, dre, periodo,
                                                        tipo_conta):
    response = jwt_authenticated_client_relatorio_consolidado.get(
        f'/api/relatorios-consolidados-dre/status-relatorio/?dre={dre.uuid}&periodo={periodo.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'mensagem': 'Faltou informar o uuid do tipo de conta. ?tipo_conta=uuid_do_tipo_conta',
        'operacao': 'status-relatorio'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado


@pytest.fixture
def relatorio_dre_consolidado_em_processamento(periodo, dre, tipo_conta):
    return baker.make(
        'RelatorioConsolidadoDre',
        dre=dre,
        tipo_conta=tipo_conta,
        periodo=periodo,
        arquivo=None,
        status='EM_PROCESSAMENTO'
    )


def test_api_get_status_relatorio_em_processamento(jwt_authenticated_client_relatorio_consolidado, dre, periodo,
                                                   tipo_conta,
                                                   relatorio_dre_consolidado_em_processamento):
    response = jwt_authenticated_client_relatorio_consolidado.get(
        f'/api/relatorios-consolidados-dre/status-relatorio/?dre={dre.uuid}&periodo={periodo.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'pcs_em_analise': False,
        'status_geracao': 'EM_PROCESSAMENTO',
        'status_txt': 'Análise de prestações de contas das associações completa. Relatório em processamento.',
        'cor_idx': 3,
        'status_arquivo': 'Relatório sendo gerado. Aguarde.'
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

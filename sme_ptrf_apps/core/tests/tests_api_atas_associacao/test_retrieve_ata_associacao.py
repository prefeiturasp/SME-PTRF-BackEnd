import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_retrieve_ata_associacao(jwt_authenticated_client_a, associacao, ata_2020_1_cheque_aprovada):
    response = jwt_authenticated_client_a.get(f'/api/atas-associacao/{ata_2020_1_cheque_aprovada.uuid}/', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = {
        'arquivo_pdf': None,
        'associacao': {'cnpj': '52.302.275/0001-83',
                       'nome': 'Escola Teste',
                       'unidade': {'nome': 'Escola Teste', 'tipo_unidade': 'CEU'},
                       'uuid': f'{ata_2020_1_cheque_aprovada.associacao.uuid}'},
        'cargo_presidente_reuniao': 'Presidente',
        'cargo_secretaria_reuniao': 'Secretária',
        'comentarios': 'Teste',
        'convocacao': 'PRIMEIRA',
        'data_reuniao': '2020-07-01',
        'local_reuniao': 'Escola Teste',
        'nome': 'Ata de Apresentação da prestação de contas',
        'parecer_conselho': 'APROVADA',
        'periodo': {'data_fim_realizacao_despesas': '2020-06-30',
                    'data_inicio_realizacao_despesas': '2020-01-01',
                    'referencia': '2020.1',
                    'referencia_por_extenso': '1° repasse de 2020',
                    'uuid': f'{ata_2020_1_cheque_aprovada.periodo.uuid}'},
        'presidente_reuniao': 'José',
        'prestacao_conta': f'{ata_2020_1_cheque_aprovada.prestacao_conta.uuid}',
        'secretario_reuniao': 'Ana',
        'status_geracao_pdf': 'NAO_GERADO',
        'tipo_ata': 'APRESENTACAO',
        'tipo_reuniao': 'ORDINARIA',
        'uuid': f'{ata_2020_1_cheque_aprovada.uuid}',
        'retificacoes': ''
    }
    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_retrieve_ata_retificacao_associacao(jwt_authenticated_client_a, associacao, ata_2020_1_retificacao):
    response = jwt_authenticated_client_a.get(f'/api/atas-associacao/{ata_2020_1_retificacao.uuid}/', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = {
        'arquivo_pdf': None,
        'associacao': {'cnpj': '52.302.275/0001-83',
                       'nome': 'Escola Teste',
                       'unidade': {'nome': 'Escola Teste', 'tipo_unidade': 'CEU'},
                       'uuid': f'{ata_2020_1_retificacao.associacao.uuid}'},
        'cargo_presidente_reuniao': 'Presidente',
        'cargo_secretaria_reuniao': 'Secretária',
        'comentarios': 'Teste',
        'convocacao': 'PRIMEIRA',
        'data_reuniao': '2020-07-01',
        'local_reuniao': 'Escola Teste',
        'nome': 'Ata de Retificação da prestação de contas',
        'parecer_conselho': 'APROVADA',
        'periodo': {'data_fim_realizacao_despesas': '2020-06-30',
                    'data_inicio_realizacao_despesas': '2020-01-01',
                    'referencia': '2020.1',
                    'referencia_por_extenso': '1° repasse de 2020',
                    'uuid': f'{ata_2020_1_retificacao.periodo.uuid}'},
        'presidente_reuniao': 'José',
        'prestacao_conta': f'{ata_2020_1_retificacao.prestacao_conta.uuid}',
        'secretario_reuniao': 'Ana',
        'status_geracao_pdf': 'NAO_GERADO',
        'tipo_ata': 'RETIFICACAO',
        'tipo_reuniao': 'ORDINARIA',
        'uuid': f'{ata_2020_1_retificacao.uuid}',
        'retificacoes': 'Teste'
    }
    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado

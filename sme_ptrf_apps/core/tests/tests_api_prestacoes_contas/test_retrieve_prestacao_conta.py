import json

import pytest
from model_bakery import baker
from rest_framework import status

from ...api.serializers import PrestacaoContaLookUpSerializer
from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db


def test_api_retrieve_prestacao_conta_por_periodo_e_associacao(client, prestacao_conta, prestacao_conta_anterior):
    associacao_uuid = prestacao_conta.associacao.uuid
    periodo_uuid = prestacao_conta.periodo.uuid

    url = f'/api/prestacoes-contas/por-associacao-e-periodo/?associacao_uuid={associacao_uuid}&periodo_uuid={periodo_uuid}'

    response = client.get(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = PrestacaoContaLookUpSerializer(PrestacaoConta.objects.get(uuid=prestacao_conta.uuid),
                                                     many=False).data

    # Converto os campos UUIDs em strings para que a comparação funcione
    result_esperado['periodo_uuid'] = f'{result_esperado["periodo_uuid"]}'

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


@pytest.fixture
def _tecnico_dre(dre):
    return baker.make(
        'TecnicoDre',
        dre=dre,
        nome='José Testando',
        rf='271170',
    )


@pytest.fixture
def _atribuicao(_tecnico_dre, unidade, periodo):
    return baker.make(
        'Atribuicao',
        tecnico=_tecnico_dre,
        unidade=unidade,
        periodo=periodo,
    )


def test_api_retrieve_prestacao_conta_por_uuid(client, prestacao_conta, prestacao_conta_anterior, _atribuicao):
    url = f'/api/prestacoes-contas/{prestacao_conta.uuid}/'

    response = client.get(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'associacao': {
            'ccm': '0.000.00-0',
            'cnpj': '52.302.275/0001-83',
            'email': 'ollyverottoboni@gmail.com',
            'nome': 'Escola Teste',
            'presidente_associacao': {
                'cargo_educacao': '',
                'email': '',
                'nome': ''
            },
            'presidente_conselho_fiscal': {
                'cargo_educacao': '',
                'email': '',
                'nome': ''
            },
            'processo_regularidade': '123456',
            'status_regularidade': 'PENDENTE',
            'unidade': {
                'bairro': 'COHAB INSTITUTO ADVENTISTA',
                'cep': '5868120',
                'codigo_eol': '123456',
                'complemento': 'fundos',
                'diretor_nome': 'Pedro Amaro',
                'dre': {
                    'codigo_eol': '99999',
                    'nome': 'DRE teste',
                    'sigla': '',
                    'tipo_unidade': 'DRE',
                    'uuid': f'{prestacao_conta.associacao.unidade.dre.uuid}'
                },
                'dre_cnpj': '63.058.286/0001-86',
                'dre_designacao_ano': '2017',
                'dre_designacao_portaria': 'Portaria nº 0.000',
                'dre_diretor_regional_nome': 'Anthony Edward Stark',
                'dre_diretor_regional_rf': '1234567',
                'email': 'emefjopfilho@sme.prefeitura.sp.gov.br',
                'logradouro': 'dos Testes',
                'nome': 'Escola Teste',
                'numero': '200',
                'qtd_alunos': 1000,
                'sigla': 'ET',
                'telefone': '58212627',
                'tipo_logradouro': 'Travessa',
                'tipo_unidade': 'CEU',
                'uuid': f'{prestacao_conta.associacao.unidade.uuid}'
            },
            'uuid': f'{prestacao_conta.associacao.uuid}'
        },
        'periodo_uuid': f'{prestacao_conta.periodo.uuid}',
        'status': 'DOCS_PENDENTES',
        'uuid': f'{prestacao_conta.uuid}',
        'tecnico_responsavel': {
            'nome': 'José Testando',
            'rf': '271170',
            'uuid': f'{_atribuicao.tecnico.uuid}'
        },
        'data_recebimento': '2020-10-01'
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado

import json
import pytest

from datetime import date

from model_bakery import baker
from rest_framework import status

from ...api.serializers import PrestacaoContaLookUpSerializer
from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db


def test_api_retrieve_prestacao_conta_por_periodo_e_associacao(jwt_authenticated_client_a, prestacao_conta, prestacao_conta_anterior):
    associacao_uuid = prestacao_conta.associacao.uuid
    periodo_uuid = prestacao_conta.periodo.uuid

    url = f'/api/prestacoes-contas/por-associacao-e-periodo/?associacao_uuid={associacao_uuid}&periodo_uuid={periodo_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

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


@pytest.fixture
def _devolucao_prestacao_conta(prestacao_conta):
    return baker.make(
        'DevolucaoPrestacaoConta',
        prestacao_conta=prestacao_conta,
        data=date(2020, 7, 1),
        data_limite_ue=date(2020, 8, 1),
    )


@pytest.fixture
def _cobranca_prestacao_devolucao(prestacao_conta, _devolucao_prestacao_conta):
    return baker.make(
        'CobrancaPrestacaoConta',
        prestacao_conta=prestacao_conta,
        tipo='DEVOLUCAO',
        data=date(2020, 7, 1),
        devolucao_prestacao=_devolucao_prestacao_conta
    )


@pytest.fixture
def _processo_associacao_prestacao_conta(associacao):
    return baker.make(
        'ProcessoAssociacao',
        associacao=associacao,
        numero_processo='123456',
        ano='2019'
    )


@pytest.fixture
def _analise_conta_prestacao_conta_2020_1(prestacao_conta, conta_associacao_cheque):
    return baker.make(
        'AnaliseContaPrestacaoConta',
        prestacao_conta=prestacao_conta,
        conta_associacao=conta_associacao_cheque,
        data_extrato=date(2020, 7, 1),
        saldo_extrato=100.00,
    )


@pytest.fixture
def despesa(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=date(2020, 3, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=date(2020, 3, 10),
        valor_total=100.00,
    )


@pytest.fixture
def tipo_devolucao_ao_tesouro():
    return baker.make('TipoDevolucaoAoTesouro', nome='Teste')


@pytest.fixture
def devolucao_ao_tesouro(prestacao_conta, tipo_devolucao_ao_tesouro, despesa):
    return baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=prestacao_conta,
        tipo=tipo_devolucao_ao_tesouro,
        data=date(2020, 7, 1),
        despesa=despesa,
        devolucao_total=True,
        valor=100.00,
        motivo='teste'
    )


def test_api_retrieve_prestacao_conta_por_uuid(jwt_authenticated_client_a, prestacao_conta, prestacao_conta_anterior,
                                               _atribuicao,
                                               _devolucao_prestacao_conta, _cobranca_prestacao_devolucao,
                                               _processo_associacao_prestacao_conta,
                                               _analise_conta_prestacao_conta_2020_1, conta_associacao_cheque,
                                               devolucao_ao_tesouro):
    url = f'/api/prestacoes-contas/{prestacao_conta.uuid}/'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

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
                    'sigla': 'TT',
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
                'qtd_alunos': 0,
                'sigla': 'ET',
                'telefone': '58212627',
                'tipo_logradouro': 'Travessa',
                'tipo_unidade': 'CEU',
                'uuid': f'{prestacao_conta.associacao.unidade.uuid}'
            },
            'uuid': f'{prestacao_conta.associacao.uuid}'
        },
        'periodo_uuid': f'{prestacao_conta.periodo.uuid}',
        'status': 'NAO_APRESENTADA',
        'uuid': f'{prestacao_conta.uuid}',
        'tecnico_responsavel': {
            'nome': 'José Testando',
            'rf': '271170',
            'uuid': f'{_atribuicao.tecnico.uuid}'
        },
        'data_recebimento': '2020-10-01',
        'devolucoes_da_prestacao': [
            {
                'cobrancas_da_devolucao': [
                    {
                        'data': '2020-07-01',
                        'prestacao_conta': f'{prestacao_conta.uuid}',
                        'tipo': 'DEVOLUCAO',
                        'uuid': f'{_cobranca_prestacao_devolucao.uuid}',
                        'associacao': f'{_cobranca_prestacao_devolucao.associacao.uuid}',
                        'periodo': f'{_cobranca_prestacao_devolucao.periodo.uuid}',
                    }
                ],
                'data': '2020-07-01',
                'data_limite_ue': '2020-08-01',
                'prestacao_conta': f'{prestacao_conta.uuid}',
                'uuid': f'{_devolucao_prestacao_conta.uuid}'
            }
        ],
        'processo_sei': '123456',
        'data_ultima_analise': f'{prestacao_conta.data_ultima_analise}',
        'devolucao_ao_tesouro': '100,00',
        'analises_de_conta_da_prestacao': [
            {
                'conta_associacao': {
                    'agencia': '67945',
                    'banco_nome': 'Banco do Inter',
                    'numero_conta': '935556-x',
                    'tipo_conta': {
                        'uuid': f'{conta_associacao_cheque.tipo_conta.uuid}',
                        'id': conta_associacao_cheque.tipo_conta.id,
                        'nome': 'Cheque',
                        'apenas_leitura': False
                    },
                    'uuid': f'{_analise_conta_prestacao_conta_2020_1.conta_associacao.uuid}'
                },
                'data_extrato': '2020-07-01',
                'prestacao_conta': f'{prestacao_conta.uuid}',
                'saldo_extrato': '100.00',
                'uuid': f'{_analise_conta_prestacao_conta_2020_1.uuid}'
            }
        ],
        'ressalvas_aprovacao': 'Texto ressalva',
        'motivos_reprovacao': 'Motivo reprovação',
        'devolucoes_ao_tesouro_da_prestacao': [
            {
                'data': '2020-07-01',
                'despesa': {
                    'associacao': f'{prestacao_conta.associacao.uuid}',
                    'cpf_cnpj_fornecedor': '11.478.276/0001-04',
                    'data_documento': '2020-03-10',
                    'nome_fornecedor': 'Fornecedor '
                                       'SA',
                    'numero_documento': '123456',
                    'tipo_documento': {
                        'id': devolucao_ao_tesouro.despesa.tipo_documento.id,
                        'nome': 'NFe'
                    },
                    'uuid': f'{devolucao_ao_tesouro.despesa.uuid}',
                    'valor_ptrf': 100.0,
                    'valor_total': '100.00'
                },
                'devolucao_total': True,
                'motivo': 'teste',
                'prestacao_conta': f'{prestacao_conta.uuid}',
                'tipo': {
                    'id': devolucao_ao_tesouro.tipo.id,
                    'nome': 'Teste',
                    'uuid': f'{devolucao_ao_tesouro.tipo.uuid}',
                },
                'uuid': f'{devolucao_ao_tesouro.uuid}',
                'valor': '100.00',
                'visao_criacao': 'DRE'
            }
        ],
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado

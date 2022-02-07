import json
import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_previa_prestacao_conta_por_periodo_e_associacao(jwt_authenticated_client_a, associacao, periodo_2020_1):
    associacao_uuid = associacao.uuid
    periodo_uuid = periodo_2020_1.uuid
    periodo = periodo_2020_1

    url = f'/api/prestacoes-contas/previa/?associacao={associacao_uuid}&periodo={periodo_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'associacao': {
            'ccm': '0.000.00-0',
            'cnpj': '52.302.275/0001-83',
            'email': 'ollyverottoboni@gmail.com',
            'nome': 'Escola Teste',
            'presidente_associacao': {
                'bairro': '',
                'cargo_educacao': '',
                'cep': '',
                'email': '',
                'endereco': '',
                'nome': '',
                'telefone': ''
            },
            'presidente_conselho_fiscal': {
                'cargo_educacao': '',
                'email': '',
                'nome': ''
            },
            'processo_regularidade': '123456',
            'periodo_inicial': {
                'data_fim_realizacao_despesas': '2019-08-31',
                'data_inicio_realizacao_despesas': '2019-01-01',
                'referencia': '2019.1',
                'referencia_por_extenso': '1° repasse de 2019',
                'uuid': f'{associacao.periodo_inicial.uuid}'
            },
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
                    'uuid': f'{associacao.unidade.dre.uuid}'
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
                'uuid': f'{associacao.unidade.uuid}'
            },
            'uuid': f'{associacao.uuid}',
            'id': associacao.id,
        },
        'periodo_uuid': f'{periodo.uuid}',
        'status': 'NAO_APRESENTADA',
        'uuid': None,
        'tecnico_responsavel': None,
        'data_recebimento': None,
        'data_recebimento_apos_acertos': None,
        'devolucoes_da_prestacao': [],
        'processo_sei': '',
        'data_ultima_analise': None,
        'devolucao_ao_tesouro': '',
        'analises_de_conta_da_prestacao': [],
        'permite_analise_valores_reprogramados': None,
        'motivos_aprovacao_ressalva': [],
        'outros_motivos_aprovacao_ressalva': '',
        'motivos_reprovacao': [],
        'outros_motivos_reprovacao': '',
        'devolucoes_ao_tesouro_da_prestacao': [],
        'arquivos_referencia': [],
        'analise_atual': None,
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado



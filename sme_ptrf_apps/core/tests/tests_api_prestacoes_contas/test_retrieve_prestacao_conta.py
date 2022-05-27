import json
import pytest
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile

from model_bakery import baker
from rest_framework import status

from ...api.serializers import PrestacaoContaLookUpSerializer
from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db


def test_api_retrieve_prestacao_conta_por_periodo_e_associacao(jwt_authenticated_client_a, prestacao_conta,
                                                               prestacao_conta_anterior):
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


@pytest.fixture
def arquivo_relacao_bens():
    return SimpleUploadedFile(
        f'relacao_bens.pdf',
        bytes(f"""Arquivo teste""", encoding="utf-8"))


@pytest.fixture
def relacao_bens_cheque(arquivo_relacao_bens, prestacao_conta, conta_associacao_cheque):
    return baker.make(
        'RelacaoBens',
        arquivo=arquivo_relacao_bens,
        arquivo_pdf=arquivo_relacao_bens,
        conta_associacao=conta_associacao_cheque,
        prestacao_conta=prestacao_conta,
        status='CONCLUIDO'
    )


@pytest.fixture
def arquivo_demonstrativo():
    return SimpleUploadedFile(
        f'demonstrativo.pdf',
        bytes(f"""Arquivo teste""", encoding="utf-8"))


@pytest.fixture
def demonstrativo_financeiro_cheque(arquivo_demonstrativo, prestacao_conta, conta_associacao_cheque):
    return baker.make(
        'DemonstrativoFinanceiro',
        arquivo=arquivo_demonstrativo,
        arquivo_pdf=arquivo_demonstrativo,
        conta_associacao=conta_associacao_cheque,
        prestacao_conta=prestacao_conta,
        status='CONCLUIDO'
    )


@pytest.fixture
def arquivo_extrato():
    return SimpleUploadedFile(
        f'extrato.pdf',
        bytes(f"""Arquivo teste""", encoding="utf-8"))


@pytest.fixture
def extrato_cheque(arquivo_extrato, prestacao_conta, conta_associacao_cheque):
    return baker.make(
        'ObservacaoConciliacao',
        periodo=prestacao_conta.periodo,
        associacao=prestacao_conta.associacao,
        conta_associacao=conta_associacao_cheque,
        texto="teste",
        data_extrato=prestacao_conta.periodo.data_fim_realizacao_despesas,
        saldo_extrato=1000,
        comprovante_extrato=arquivo_extrato,
        data_atualizacao_comprovante_extrato=prestacao_conta.periodo.data_fim_realizacao_despesas,
    )


@pytest.fixture
def _analise_prestacao_conta(prestacao_conta):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta,
    )


@pytest.fixture
def _prestacao_de_contas_com_analise_corrente(prestacao_conta, _analise_prestacao_conta):
    prestacao_conta.analise_atual = _analise_prestacao_conta
    prestacao_conta.save()
    return prestacao_conta


def test_api_retrieve_prestacao_conta_por_uuid(
    jwt_authenticated_client_a,
    _prestacao_de_contas_com_analise_corrente,
    _atribuicao,
    _devolucao_prestacao_conta,
    _cobranca_prestacao_devolucao,
    _processo_associacao_prestacao_conta,
    _analise_conta_prestacao_conta_2020_1,
    conta_associacao_cheque,
    conta_associacao_cartao,
    devolucao_ao_tesouro,
    motivo_aprovacao_ressalva_x,
    relacao_bens_cheque,
    demonstrativo_financeiro_cheque,
    extrato_cheque,
    motivo_reprovacao_x
):
    prestacao_conta = _prestacao_de_contas_com_analise_corrente

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
                'uuid': f'{prestacao_conta.associacao.periodo_inicial.uuid}'
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
            'uuid': f'{prestacao_conta.associacao.uuid}',
            'id': prestacao_conta.associacao.id,
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
        'data_recebimento_apos_acertos': '2020-10-01',
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
                'data_retorno_ue': None,
                'prestacao_conta': f'{prestacao_conta.uuid}',
                'uuid': f'{_devolucao_prestacao_conta.uuid}'
            }
        ],
        'pode_reabrir': True,
        'processo_sei': '123456',
        'data_ultima_analise': f'{prestacao_conta.data_ultima_analise}',
        'devolucao_ao_tesouro': '100,00',
        'analises_de_conta_da_prestacao': [],
        'permite_analise_valores_reprogramados': {
            'permite_analise': True,
            'erro': '',
            'mensagem': 'O período atual da PC é igual ao periodo_inicial.proximo_periodo da associacao'
        },
        'informacoes_conciliacao_ue': [
            {
                'conta_uuid': f'{prestacao_conta.associacao.observacoes_conciliacao_da_associacao.first().conta_associacao.uuid}',
                'data_extrato': '2019-11-30',
                'saldo_extrato': 1000.0,
                'periodo_uuid': f'{prestacao_conta.associacao.observacoes_conciliacao_da_associacao.first().periodo.uuid}'
            }
        ],
        'motivos_aprovacao_ressalva': [
            {
                'uuid': f'{motivo_aprovacao_ressalva_x.uuid}',
                'motivo': f'{motivo_aprovacao_ressalva_x.motivo}'
            },
        ],
        'outros_motivos_aprovacao_ressalva': 'Outros motivos',
        'motivos_reprovacao': [
            {
                'uuid': f'{motivo_reprovacao_x.uuid}',
                'motivo': f'{motivo_reprovacao_x.motivo}'
            }
        ],
        'outros_motivos_reprovacao': 'Outros motivos reprovacao',
        'recomendacoes': 'recomendacao',
        'devolucoes_ao_tesouro_da_prestacao': [
            {
                'data': '2020-07-01',
                'despesa': {
                    'associacao': f'{prestacao_conta.associacao.uuid}',
                    'cpf_cnpj_fornecedor': '11.478.276/0001-04',
                    'data_documento': '2020-03-10',
                    'data_transacao': '2020-03-10',
                    'documento_transacao': '',
                    'nome_fornecedor': 'Fornecedor '
                                       'SA',
                    'numero_documento': '123456',
                    'tipo_documento': {
                        'id': devolucao_ao_tesouro.despesa.tipo_documento.id,
                        'nome': 'NFe'
                    },
                    'tipo_transacao': {
                        'id': devolucao_ao_tesouro.despesa.tipo_transacao.id,
                        'nome': devolucao_ao_tesouro.despesa.tipo_transacao.nome,
                        'tem_documento': devolucao_ao_tesouro.despesa.tipo_transacao.tem_documento
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
        'arquivos_referencia': [
            {
                'tipo': 'DF',
                'nome': 'Demonstrativo Financeiro da Conta Cheque',
                'uuid': f'{demonstrativo_financeiro_cheque.uuid}',
                'conta_uuid': f'{conta_associacao_cheque.uuid}'
            },
            {
                'tipo': 'RB',
                'nome': 'Relação de Bens da Conta Cheque',
                'uuid': f'{relacao_bens_cheque.uuid}',
                'conta_uuid': f'{conta_associacao_cheque.uuid}'
            },
            {
                'tipo': 'EB',
                'nome': 'Extrato Bancário da Conta Cheque',
                'uuid': f'{extrato_cheque.uuid}',
                'conta_uuid': f'{conta_associacao_cheque.uuid}'
            }
        ],
        'analise_atual': {
            'uuid': f'{prestacao_conta.analise_atual.uuid}',
            'id': prestacao_conta.analise_atual.id,
            'devolucao_prestacao_conta': None,
            'status': 'EM_ANALISE',
            'criado_em': prestacao_conta.analise_atual.criado_em.isoformat("T")
        },
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado

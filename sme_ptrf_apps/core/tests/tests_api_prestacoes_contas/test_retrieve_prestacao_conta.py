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

    assert response.status_code == status.HTTP_200_OK
    assert result['uuid'] == str(prestacao_conta.uuid)

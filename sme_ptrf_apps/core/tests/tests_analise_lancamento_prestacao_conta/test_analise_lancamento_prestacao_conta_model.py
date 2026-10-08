import pytest
from django.contrib import admin

from ...models import (
    AnalisePrestacaoConta,
    AnaliseLancamentoPrestacaoConta,
    DevolucaoAoTesouro,
    SolicitacaoDevolucaoAoTesouro,
    TipoAcertoLancamento,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def _analise_lancamento_despesa_com_solicitacao_devolucao(
    analise_lancamento_prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    tipo_acerto_lancamento_factory,
    despesa_factory,
):
    analise_lancamento = analise_lancamento_prestacao_conta_factory.create(despesa=despesa_factory.create())
    solicitacao_acerto_lancamento_factory.create(
        analise_lancamento=analise_lancamento,
        tipo_acerto=tipo_acerto_lancamento_factory.create(categoria=TipoAcertoLancamento.CATEGORIA_DEVOLUCAO),
    )
    return analise_lancamento


def _devolucao_ao_tesouro_da_resposta(analise_lancamento):
    resultado = analise_lancamento.solicitacoes_de_acertos_agrupado_por_categoria()
    categoria_devolucao = next(
        categoria for categoria in resultado['solicitacoes_acerto_por_categoria']
        if categoria['categoria'] == TipoAcertoLancamento.CATEGORIA_DEVOLUCAO
    )
    return categoria_devolucao['acertos'][0]['devolucao_ao_tesouro']


def test_instance_model(analise_lancamento_receita_prestacao_conta_2020_1):
    model = analise_lancamento_receita_prestacao_conta_2020_1
    assert isinstance(model, AnaliseLancamentoPrestacaoConta)
    assert isinstance(model.analise_prestacao_conta, AnalisePrestacaoConta)
    assert model.tipo_lancamento == AnaliseLancamentoPrestacaoConta.TIPO_LANCAMENTO_CREDITO
    assert model.receita is not None
    assert model.despesa is None
    assert model.resultado == AnaliseLancamentoPrestacaoConta.RESULTADO_CORRETO
    assert model.status_realizacao == AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE


def test_srt_model(analise_lancamento_receita_prestacao_conta_2020_1):
    assert analise_lancamento_receita_prestacao_conta_2020_1.__str__() == f'#{analise_lancamento_receita_prestacao_conta_2020_1.id} - Resultado:CORRETO'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[AnaliseLancamentoPrestacaoConta]


def test_audit_log(analise_lancamento_receita_prestacao_conta_2020_1):
    assert analise_lancamento_receita_prestacao_conta_2020_1.history.count() == 1  # Um log de inclusão
    assert analise_lancamento_receita_prestacao_conta_2020_1.history.latest().action == 0  # 0-Inclusão

    analise_lancamento_receita_prestacao_conta_2020_1.resultado = "AJUSTE"
    analise_lancamento_receita_prestacao_conta_2020_1.save()
    assert analise_lancamento_receita_prestacao_conta_2020_1.history.count() == 2  # Um log de inclusão e outro de edição
    assert analise_lancamento_receita_prestacao_conta_2020_1.history.latest().action == 1  # 1-Edição


def test_solicitacoes_agrupadas_devolucao_com_solicitacao_devolucao_vinculada(
    _analise_lancamento_despesa_com_solicitacao_devolucao,
    tipo_devolucao_ao_tesouro_factory,
):
    analise_lancamento = _analise_lancamento_despesa_com_solicitacao_devolucao
    solicitacao_devolucao = SolicitacaoDevolucaoAoTesouro.objects.create(
        solicitacao_acerto_lancamento=analise_lancamento.solicitacoes_de_ajuste_da_analise.first(),
        tipo=tipo_devolucao_ao_tesouro_factory.create(),
        devolucao_total=False,
        valor=100,
    )

    devolucao_ao_tesouro = _devolucao_ao_tesouro_da_resposta(analise_lancamento)

    assert devolucao_ao_tesouro['uuid'] == f"{solicitacao_devolucao.uuid}"
    assert devolucao_ao_tesouro['valor'] == '100.00'
    assert devolucao_ao_tesouro['uuid_registro_devolucao'] is None


def test_solicitacoes_agrupadas_devolucao_sem_solicitacao_devolucao_usa_devolucao_registrada(
    _analise_lancamento_despesa_com_solicitacao_devolucao,
    tipo_devolucao_ao_tesouro_factory,
):
    analise_lancamento = _analise_lancamento_despesa_com_solicitacao_devolucao
    devolucao = DevolucaoAoTesouro.objects.create(
        prestacao_conta=analise_lancamento.analise_prestacao_conta.prestacao_conta,
        despesa=analise_lancamento.despesa,
        tipo=tipo_devolucao_ao_tesouro_factory.create(),
        devolucao_total=False,
        valor=200,
    )

    devolucao_ao_tesouro = _devolucao_ao_tesouro_da_resposta(analise_lancamento)

    assert devolucao_ao_tesouro['uuid'] == f"{devolucao.uuid}"
    assert devolucao_ao_tesouro['uuid_registro_devolucao'] == f"{devolucao.uuid}"
    assert devolucao_ao_tesouro['valor'] == '200.00'


def test_solicitacoes_agrupadas_devolucao_sem_solicitacao_e_sem_devolucao_registrada(
    _analise_lancamento_despesa_com_solicitacao_devolucao,
):
    devolucao_ao_tesouro = _devolucao_ao_tesouro_da_resposta(_analise_lancamento_despesa_com_solicitacao_devolucao)

    assert devolucao_ao_tesouro is None


def test_get_tags_informacoes_conferencialist():
    tags = AnaliseLancamentoPrestacaoConta.get_tags_informacoes_de_conferencia_list()
    assert tags == [
        {
            'id': '1',
            'nome': 'AJUSTE',
            'descricao': 'O lançamento possui acertos para serem conferidos.',
        },
        {
            'id': '2',
            'nome': 'CORRETO',
            'descricao': 'O lançamento está correto e/ou os acertos foram conferidos.',
        },
        {
            'id': '3',
            'nome': 'CONFERENCIA_AUTOMATICA',
            'descricao': 'O lançamento possui acerto(s) que foram conferidos '
                         'automaticamente pelo sistema.',
        },
        {
            'id': '4',
            'nome': 'NAO_CONFERIDO',
            'descricao': 'Não conferido.',
        }
    ]

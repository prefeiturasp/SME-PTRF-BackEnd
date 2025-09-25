import pytest
from datetime import datetime, date
from django.contrib import admin

from ...models import PrestacaoConta, AnalisePrestacaoConta, DevolucaoPrestacaoConta

pytestmark = pytest.mark.django_db


@pytest.fixture
def periodo_2023_1(periodo_factory):
    return periodo_factory.create(data_inicio_realizacao_despesas=datetime(2023, 1, 1),
                                  data_fim_realizacao_despesas=datetime(2023, 5, 30))


def test_instance_model(analise_prestacao_conta_2020_1):
    model = analise_prestacao_conta_2020_1
    assert isinstance(model, AnalisePrestacaoConta)
    assert isinstance(model.prestacao_conta, PrestacaoConta)
    assert isinstance(model.devolucao_prestacao_conta, DevolucaoPrestacaoConta)
    assert model.status == AnalisePrestacaoConta.STATUS_EM_ANALISE


def test_srt_model(analise_prestacao_conta_2020_1):
    assert analise_prestacao_conta_2020_1.__str__(
    ) == f'2020.1 - 2020-01-01 a 2020-06-30 - Análise #{analise_prestacao_conta_2020_1.id}'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[AnalisePrestacaoConta]


def test_audit_log(analise_prestacao_conta_2020_1):
    assert analise_prestacao_conta_2020_1.history.count() == 1  # Um log de inclusão
    assert analise_prestacao_conta_2020_1.history.latest().action == 0  # 0-Inclusão

    analise_prestacao_conta_2020_1.versao = "RASCUNHO"
    analise_prestacao_conta_2020_1.save()
    assert analise_prestacao_conta_2020_1.history.count() == 2  # Um log de inclusão e outro de edição
    assert analise_prestacao_conta_2020_1.history.latest().action == 1  # 1-Edição


@pytest.mark.parametrize(
    "tem_documento, doc_pode_alterar, tem_lancamento, lanc_pode_alterar, esperado",
    [
        (True, True, False, False, True),   # documento_pode_alterar
        (True, False, False, False, False),  # documento_nao_altera

        (False, False, True, True, True),   # lancamento_pode_alterar
        (False, False, True, False, False),  # lancamento_nao_altera

        (True, True, True, False, True),   # doc_altera_lanc_nao
        (True, False, True, True, True),   # doc_nao_lanc_altera
        (True, False, True, False, False),  # doc_nao_lanc_nao

        (False, False, False, False, False),  # nenhum
    ],
    ids=[
        "documento_pode_alterar",
        "documento_nao_altera",
        "lancamento_pode_alterar",
        "lancamento_nao_altera",
        "doc_altera_lanc_nao",
        "doc_nao_lanc_altera",
        "doc_nao_lanc_nao",
        "nenhum",
    ],
)
def test_tem_acertos_que_podem_alterar_saldo_conciliacao(
    tem_documento,
    doc_pode_alterar,
    tem_lancamento,
    lanc_pode_alterar,
    esperado,
    analise_prestacao_conta_factory,
    analise_documento_prestacao_conta_factory,
    analise_lancamento_prestacao_conta_factory,
    tipo_acerto_documento_factory,
    tipo_acerto_lancamento_factory,
    solicitacao_acerto_documento_factory,
    solicitacao_acerto_lancamento_factory,
):
    analise = analise_prestacao_conta_factory(status="EM_ANALISE")

    if tem_documento:
        analise_documento = analise_documento_prestacao_conta_factory(
            analise_prestacao_conta=analise
        )
        tipo_doc = tipo_acerto_documento_factory(
            pode_alterar_saldo_conciliacao=doc_pode_alterar
        )
        solicitacao_acerto_documento_factory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_doc,
            status_realizacao='PENDENTE'
        )

    if tem_lancamento:
        analise_lancamento = analise_lancamento_prestacao_conta_factory(
            analise_prestacao_conta=analise
        )
        tipo_lanc = tipo_acerto_lancamento_factory(
            pode_alterar_saldo_conciliacao=lanc_pode_alterar
        )
        solicitacao_acerto_lancamento_factory(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_lanc,
            status_realizacao='PENDENTE'
        )

    assert analise.tem_acertos_que_podem_alterar_saldo_conciliacao() is esperado


@pytest.mark.parametrize(
    "com_pendencia, com_solicitacao_de_acerto_em_conta, esperado",
    [
        (True, False, True),   # tem_pendencia_sem_solicitacao
        (True, True, False),   # tem_pendencia_com_solicitacao
        (False, False, False),   # nao_tem_pendencia
    ],
    ids=["tem_pendencia_sem_solicitacao", "tem_pendencia_com_solicitacao", "nao_tem_pendencia"],
)
def test_tem_pendencia_conciliacao_sem_solicitacao_de_acerto_em_conta(
    com_pendencia,
    com_solicitacao_de_acerto_em_conta,
    esperado,
    periodo_2023_1,
    prestacao_conta_factory,
    analise_prestacao_conta_factory,
    observacao_conciliacao_factory,
    conta_associacao_factory,
    analise_conta_prestacao_conta_factory,
    pdf_factory
):

    pc = prestacao_conta_factory(periodo=periodo_2023_1, status="EM_ANALISE")
    analise = analise_prestacao_conta_factory(status="EM_ANALISE", prestacao_conta=pc)
    pc.analise_atual = analise
    pc.save()

    conta_associacao = conta_associacao_factory.create(
        associacao=analise.prestacao_conta.associacao,
        data_inicio=date(2019, 2, 2)
    )
    if com_pendencia:
        observacao_conciliacao_factory(
            conta_associacao=conta_associacao,
            associacao=analise.prestacao_conta.associacao,
            periodo=analise.prestacao_conta.periodo,
        )
    else:
        observacao_conciliacao_factory(
            data_extrato=analise.prestacao_conta.periodo.data_fim_realizacao_despesas,
            saldo_extrato=1000,
            periodo=analise.prestacao_conta.periodo,
            associacao=analise.prestacao_conta.associacao,
            conta_associacao=conta_associacao,
            comprovante_extrato=pdf_factory())

    if com_solicitacao_de_acerto_em_conta:
        analise_conta_prestacao_conta_factory(
            analise_prestacao_conta=analise,
            prestacao_conta=analise.prestacao_conta,
            conta_associacao=conta_associacao,
        )

    assert analise.tem_pendencia_conciliacao_sem_solicitacao_de_acerto_em_conta() is esperado


def test_contas_pendencia_conciliacao_sem_solicitacao_de_acerto_em_conta(
    periodo_2023_1,
    prestacao_conta_factory,
    analise_prestacao_conta_factory,
    observacao_conciliacao_factory,
    conta_associacao_factory
):
    pc = prestacao_conta_factory(periodo=periodo_2023_1, status="EM_ANALISE")
    analise = analise_prestacao_conta_factory(status="EM_ANALISE", prestacao_conta=pc)
    pc.analise_atual = analise
    pc.save()

    conta_associacao = conta_associacao_factory.create(
        associacao=analise.prestacao_conta.associacao,
        data_inicio=date(2019, 2, 2)
    )

    observacao_conciliacao_factory(
        conta_associacao=conta_associacao,
        associacao=analise.prestacao_conta.associacao,
        periodo=analise.prestacao_conta.periodo,
    )

    assert analise.contas_pendencia_conciliacao_sem_solicitacao_de_acerto_em_conta()[0].uuid == conta_associacao.uuid


def test_contas_pendencia_conciliacao_sem_solicitacao_de_acerto_em_conta_sem_pendencias(
    periodo_2023_1,
    prestacao_conta_factory,
    analise_prestacao_conta_factory,
    analise_conta_prestacao_conta_factory,
    observacao_conciliacao_factory,
    conta_associacao_factory
):

    pc = prestacao_conta_factory(periodo=periodo_2023_1, status="EM_ANALISE")
    analise = analise_prestacao_conta_factory(status="EM_ANALISE", prestacao_conta=pc)
    pc.analise_atual = analise
    pc.save()

    conta_associacao = conta_associacao_factory.create(
        associacao=analise.prestacao_conta.associacao,
        data_inicio=date(2019, 2, 2)
    )
    observacao_conciliacao_factory(
        conta_associacao=conta_associacao,
        associacao=analise.prestacao_conta.associacao,
        periodo=analise.prestacao_conta.periodo,
    )

    analise_conta_prestacao_conta_factory(
        analise_prestacao_conta=analise,
        prestacao_conta=analise.prestacao_conta,
        conta_associacao=conta_associacao,
    )

    assert analise.contas_pendencia_conciliacao_sem_solicitacao_de_acerto_em_conta() == []

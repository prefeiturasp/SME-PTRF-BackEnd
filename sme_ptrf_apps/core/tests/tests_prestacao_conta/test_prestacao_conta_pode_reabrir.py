import pytest
from datetime import date
from model_bakery import baker

from sme_ptrf_apps.core.models.fechamento_periodo import STATUS_IMPLANTACAO, STATUS_FECHADO

pytestmark = pytest.mark.django_db


@pytest.fixture
def periodo_implantacao_2019_1():
    return baker.make(
        'Periodo',
        referencia='2019.1',
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 6, 30),
        periodo_anterior=None
    )


@pytest.fixture
def periodo_fechamento_2019_2(periodo_implantacao_2019_1):
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 7, 1),
        data_fim_realizacao_despesas=date(2019, 12, 31),
        periodo_anterior=periodo_implantacao_2019_1
    )


@pytest.fixture
def periodo_fechamento_2020_1(periodo_fechamento_2019_2):
    return baker.make(
        'Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=date(2020, 1, 1),
        data_fim_realizacao_despesas=date(2020, 6, 30),
        periodo_anterior=periodo_fechamento_2019_2
    )


@pytest.fixture
def fechamento_implantacao_2019_1(periodo_implantacao_2019_1, associacao, conta_associacao, acao_associacao):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_implantacao_2019_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        status=STATUS_IMPLANTACAO,
    )

@pytest.fixture
def prestacao_conta_2019_2(periodo_fechamento_2019_2, associacao):
    return baker.make(
        'PrestacaoConta',
        id=1000,
        periodo=periodo_fechamento_2019_2,
        associacao=associacao,
        status="EM_ANALISE",
    )

# DOCUMENTO: INCLUSAO_CREDITO.
@pytest.fixture
def tipo_acerto_documento_inclusao_credito():
    return baker.make(
        'TipoAcertoDocumento', categoria="INCLUSAO_CREDITO"
    )
@pytest.fixture
def solicitacao_acerto_documento_inclusao_credito(
    analise_documento,
    tipo_acerto_documento_inclusao_credito,
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento,
        tipo_acerto=tipo_acerto_documento_inclusao_credito
    )

# DOCUMENTO: INCLUSAO_GASTO.
@pytest.fixture
def tipo_acerto_documento_inclusao_gasto():
    return baker.make(
        'TipoAcertoDocumento', categoria="INCLUSAO_GASTO"
    )
@pytest.fixture
def solicitacao_acerto_documento_inclusao_gasto(
    analise_documento,
    tipo_acerto_documento_inclusao_gasto,
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento,
        tipo_acerto=tipo_acerto_documento_inclusao_gasto
    )

# DOCUMENTO: EDICAO_INFORMACAO.
@pytest.fixture
def tipo_acerto_documento_edicao_informacao():
    return baker.make(
        'TipoAcertoDocumento', categoria="EDICAO_INFORMACAO"
    )
@pytest.fixture
def solicitacao_acerto_documento_edicao_informacao(
    analise_documento,
    tipo_acerto_documento_edicao_informacao,
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento,
        tipo_acerto=tipo_acerto_documento_edicao_informacao
    )

# DOCUMENTO: AJUSTES_EXTERNOS. (Não demanda exclusão de documentos e fechamentos)
@pytest.fixture
def tipo_acerto_documento_ajustes_externos():
    return baker.make(
        'TipoAcertoDocumento', categoria="AJUSTES_EXTERNOS"
    )
@pytest.fixture
def solicitacao_acerto_documento_ajustes_externos(
    analise_documento,
    tipo_acerto_documento_ajustes_externos,
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento,
        tipo_acerto=tipo_acerto_documento_ajustes_externos
    )

# DOCUMENTO: SOLICITACAO_ESCLARECIMENTO. (Não demanda exclusão de documentos e fechamentos)
@pytest.fixture
def tipo_acerto_documento_solicitacao_esclarecimento():
    return baker.make(
        'TipoAcertoDocumento', categoria="SOLICITACAO_ESCLARECIMENTO"
    )
@pytest.fixture
def solicitacao_acerto_documento_solicitacao_esclarecimento(
    analise_documento,
    tipo_acerto_documento_solicitacao_esclarecimento,
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento,
        tipo_acerto=tipo_acerto_documento_solicitacao_esclarecimento
    )

# LANCAMENTO: DEVOLUCAO (Não demanda exclusão de documentos e fechamentos)
@pytest.fixture
def tipo_acerto_lancamento_devolucao():
    return baker.make(
        'TipoAcertoLancamento', categoria="DEVOLUCAO"
    )
@pytest.fixture
def solicitacao_acerto_lancamento_devolucao(
    analise_lancamento,
    tipo_acerto_lancamento_devolucao,
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento,
        tipo_acerto=tipo_acerto_lancamento_devolucao
    )

# LANCAMENTO: EDICAO_LANCAMENTO
@pytest.fixture
def tipo_acerto_lancamento_edicao_lancamento():
    return baker.make(
        'TipoAcertoLancamento', categoria="EDICAO_LANCAMENTO"
    )
@pytest.fixture
def solicitacao_acerto_lancamento_edicao_lancamento(
    analise_lancamento,
    tipo_acerto_lancamento_edicao_lancamento,
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento,
        tipo_acerto=tipo_acerto_lancamento_edicao_lancamento
    )

# LANCAMENTO: CONCILIACAO_LANCAMENTO
@pytest.fixture
def tipo_acerto_lancamento_conciliacao_lancamento():
    return baker.make(
        'TipoAcertoLancamento', categoria="CONCILIACAO_LANCAMENTO"
    )
@pytest.fixture
def solicitacao_acerto_lancamento_conciliacao_lancamento(
    analise_lancamento,
    tipo_acerto_lancamento_conciliacao_lancamento,
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento,
        tipo_acerto=tipo_acerto_lancamento_conciliacao_lancamento,
        devolucao_ao_tesouro=None,
        detalhamento="teste"
    )

# LANCAMENTO: DESCONCILIACAO_LANCAMENTO
@pytest.fixture
def tipo_acerto_lancamento_desconciliacao_lancamento():
    return baker.make(
        'TipoAcertoLancamento', categoria="DESCONCILIACAO_LANCAMENTO"
    )
@pytest.fixture
def solicitacao_acerto_lancamento_desconciliacao_lancamento(
    analise_lancamento,
    tipo_acerto_lancamento_desconciliacao_lancamento,
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento,
        tipo_acerto=tipo_acerto_lancamento_desconciliacao_lancamento
    )

# LANCAMENTO: EXCLUSAO_LANCAMENTO
@pytest.fixture
def tipo_acerto_lancamento_exclusao_lancamento():
    return baker.make(
        'TipoAcertoLancamento', categoria="EXCLUSAO_LANCAMENTO"
    )
@pytest.fixture
def solicitacao_acerto_lancamento_exclusao_lancamento(
    analise_lancamento,
    tipo_acerto_lancamento_exclusao_lancamento,
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento,
        tipo_acerto=tipo_acerto_lancamento_exclusao_lancamento
    )

# LANCAMENTO: AJUSTES_EXTERNOS (Não demanda exclusão de documentos e fechamentos)
@pytest.fixture
def tipo_acerto_lancamento_ajustes_externos():
    return baker.make(
        'TipoAcertoLancamento', categoria="AJUSTES_EXTERNOS"
    )
@pytest.fixture
def solicitacao_acerto_lancamento_ajustes_externos(
    analise_lancamento,
    tipo_acerto_lancamento_ajustes_externos,
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento,
        tipo_acerto=tipo_acerto_lancamento_ajustes_externos
    )

# LANCAMENTO: SOLICITACAO_ESCLARECIMENTO (Não demanda exclusão de documentos e fechamentos)
@pytest.fixture
def tipo_acerto_lancamento_solicitacao_esclarecimento():
    return baker.make(
        'TipoAcertoLancamento', categoria="SOLICITACAO_ESCLARECIMENTO"
    )
@pytest.fixture
def solicitacao_acerto_lancamento_solicitacao_esclarecimento(
    analise_lancamento,
    tipo_acerto_lancamento_solicitacao_esclarecimento,
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento,
        tipo_acerto=tipo_acerto_lancamento_solicitacao_esclarecimento
    )

@pytest.fixture
def analise_prestacao_conta_2019_2(prestacao_conta_2019_2):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_2019_2
    )

@pytest.fixture
def prestacao_conta_2019_2_em_analise(periodo_fechamento_2019_2, associacao, analise_prestacao_conta_2019_2):
    return baker.make(
        'PrestacaoConta',
        id=1000,
        periodo=periodo_fechamento_2019_2,
        associacao=associacao,
        data_recebimento=date(2019, 8, 1),
        status="EM_ANALISE",
        analise_atual=analise_prestacao_conta_2019_2,
        criado_em=date(2019, 8, 1)
    )

@pytest.fixture
def analise_documento(analise_prestacao_conta_2019_2):
    return baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2019_2,
        resultado='AJUSTE'
    )

@pytest.fixture
def analise_lancamento(analise_prestacao_conta_2019_2):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2019_2,
    )


@pytest.fixture
def fechamento_2019_2(
    periodo_fechamento_2019_2,
    associacao,
    conta_associacao,
    acao_associacao,
    fechamento_implantacao_2019_1,
    prestacao_conta_2019_2
):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_fechamento_2019_2,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=fechamento_implantacao_2019_1,
        status=STATUS_FECHADO,
        prestacao_conta=prestacao_conta_2019_2
    )


@pytest.fixture
def prestacao_conta_2020_1_em_analise(periodo_fechamento_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        id=1001,
        periodo=periodo_fechamento_2020_1,
        associacao=associacao,
        status="EM_ANALISE"
    )


@pytest.fixture
def fechamento_2020_1(
    periodo_fechamento_2020_1,
    associacao,
    conta_associacao,
    acao_associacao,
    fechamento_2019_2,
    prestacao_conta_2020_1_em_analise
):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_fechamento_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=fechamento_2019_2,
        status=STATUS_FECHADO,
        prestacao_conta=prestacao_conta_2020_1_em_analise
    )


@pytest.fixture
def prestacao_conta_2020_1_devolvida(periodo_fechamento_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        id=1002,
        periodo=periodo_fechamento_2020_1,
        associacao=associacao,
        status="DEVOLVIDA"
    )

def test_pode_devolver_se_os_acertos_nao_demandam_exclusao_de_documentos_e_fechamentos(
    prestacao_conta_2020_1_em_analise,
    fechamento_2020_1,
    prestacao_conta_2019_2_em_analise,
    fechamento_2019_2,
    fechamento_implantacao_2019_1,
    solicitacao_acerto_documento_ajustes_externos,
    solicitacao_acerto_documento_solicitacao_esclarecimento,
    solicitacao_acerto_lancamento_devolucao,
    solicitacao_acerto_lancamento_ajustes_externos,
    solicitacao_acerto_lancamento_solicitacao_esclarecimento
):
    assert prestacao_conta_2019_2_em_analise.pode_devolver()

def test_nao_pode_devolver_se_tiver_acerto_documento_inclusao_credito(
    prestacao_conta_2020_1_em_analise,
    fechamento_2020_1,
    prestacao_conta_2019_2_em_analise,
    fechamento_2019_2,
    fechamento_implantacao_2019_1,
    solicitacao_acerto_documento_inclusao_credito
):
    assert not prestacao_conta_2019_2_em_analise.pode_devolver()

def test_nao_pode_devolver_se_tiver_acerto_documento_inclusao_gasto(
    prestacao_conta_2020_1_em_analise,
    fechamento_2020_1,
    prestacao_conta_2019_2_em_analise,
    fechamento_2019_2,
    fechamento_implantacao_2019_1,
    solicitacao_acerto_documento_inclusao_gasto
):
    assert not prestacao_conta_2019_2_em_analise.pode_devolver()

def test_nao_pode_devolver_se_tiver_acerto_documento_edicao_informacao(
    prestacao_conta_2020_1_em_analise,
    fechamento_2020_1,
    prestacao_conta_2019_2_em_analise,
    fechamento_2019_2,
    fechamento_implantacao_2019_1,
    solicitacao_acerto_documento_edicao_informacao
):
    assert not prestacao_conta_2019_2_em_analise.pode_devolver()

def test_nao_pode_devolver_se_tiver_acerto_lancamento_edicao_lancamento(
    prestacao_conta_2020_1_em_analise,
    fechamento_2020_1,
    prestacao_conta_2019_2_em_analise,
    fechamento_2019_2,
    fechamento_implantacao_2019_1,
    solicitacao_acerto_lancamento_edicao_lancamento
):
    assert not prestacao_conta_2019_2_em_analise.pode_devolver() 

def test_nao_pode_devolver_se_tiver_acerto_lancamento_conciliacao_lancamento(
    prestacao_conta_2020_1_em_analise,
    fechamento_2020_1,
    prestacao_conta_2019_2_em_analise,
    fechamento_2019_2,
    fechamento_implantacao_2019_1,
    solicitacao_acerto_lancamento_conciliacao_lancamento
):
    assert not prestacao_conta_2019_2_em_analise.pode_devolver() 

def test_nao_pode_devolver_se_tiver_acerto_lancamento_desconciliacao_lancamento(
    prestacao_conta_2020_1_em_analise,
    fechamento_2020_1,
    prestacao_conta_2019_2_em_analise,
    fechamento_2019_2,
    fechamento_implantacao_2019_1,
    solicitacao_acerto_lancamento_desconciliacao_lancamento
):
    assert not prestacao_conta_2019_2_em_analise.pode_devolver()

def test_nao_pode_devolver_se_tiver_acerto_lancamento_exclusao_lancamento(
    prestacao_conta_2020_1_em_analise,
    fechamento_2020_1,
    prestacao_conta_2019_2_em_analise,
    fechamento_2019_2,
    fechamento_implantacao_2019_1,
    solicitacao_acerto_lancamento_exclusao_lancamento
):
    assert not prestacao_conta_2019_2_em_analise.pode_devolver() 

def test_pode_devolver_se_nao_houver_fechamentos_posteriores(
    prestacao_conta_2019_2,
    fechamento_2019_2,
    fechamento_implantacao_2019_1,
):
    assert prestacao_conta_2019_2.pode_devolver()


def test_pode_devolver_quando_proxima_pc_esta_devolvida(
    prestacao_conta_2020_1_devolvida,
    prestacao_conta_2019_2,
    fechamento_implantacao_2019_1,
    fechamento_2019_2
):
    assert prestacao_conta_2019_2.pode_devolver()

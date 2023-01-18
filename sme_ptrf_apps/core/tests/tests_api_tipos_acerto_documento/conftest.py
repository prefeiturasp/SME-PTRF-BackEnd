import pytest
from model_bakery import baker
import datetime


@pytest.fixture
def tipo_acerto_documento_create(tipo_documento_prestacao_conta_relacao_bens):
    tipo_acerto = baker.make(
        'TipoAcertoDocumento',
        nome='Teste nome igual',
        categoria='INCLUSAO_CREDITO',
    )
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_relacao_bens)
    tipo_acerto.save()
    return tipo_acerto


@pytest.fixture
def tipo_acerto_documento_01(tipo_documento_prestacao_conta_relacao_bens):
    tipo_acerto = baker.make(
        'TipoAcertoDocumento',
        nome='teste',
        categoria='INCLUSAO_CREDITO',
    )
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_relacao_bens)
    tipo_acerto.save()
    return tipo_acerto


@pytest.fixture
def tipo_acerto_documento_02(tipo_documento_prestacao_conta_relacao_bens):
    tipo_acerto = baker.make(
        'TipoAcertoDocumento',
        nome='lan',
        categoria='INCLUSAO_GASTO',
    )
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_relacao_bens)
    tipo_acerto.save()
    return tipo_acerto


@pytest.fixture
def tipo_acerto_documento_03(tipo_documento_prestacao_conta_ata):
    tipo_acerto = baker.make(
        'TipoAcertoDocumento',
        nome='teste 1',
        categoria='INCLUSAO_CREDITO',
        ativo=False
    )
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_ata)
    tipo_acerto.save()
    return tipo_acerto


@pytest.fixture
def tipo_acerto_documento_delete():
    return baker.make('TipoAcertoDocumento', nome='Teste', categoria='INCLUSAO_CREDITO')


@pytest.fixture
def tipo_acerto_documento_delete_02():
    return baker.make('TipoAcertoDocumento', nome='Teste 2', categoria='INCLUSAO_CREDITO')


@pytest.fixture
def solicitacao_acerto_documento_delete(
    analise_documento_delete,
    tipo_acerto_documento_delete_02,
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_delete,
        tipo_acerto=tipo_acerto_documento_delete_02,
        detalhamento="teste"
    )


@pytest.fixture
def analise_documento_delete(
    analise_prestacao_conta_documento_delete,
):
    return baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_documento_delete,
        # tipo_lancamento='GASTO',
        resultado='AJUSTE'
    )


@pytest.fixture
def analise_prestacao_conta_documento_delete(
    prestacao_conta_documento_delete,
):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_documento_delete,
    )


@pytest.fixture
def prestacao_conta_documento_delete(periodo_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
        data_recebimento=datetime.date(2020, 10, 1),
        status="EM_ANALISE"
    )


@pytest.fixture
def tipo_documento_prestacao_conta_relacao_bens():
    return baker.make('TipoDocumentoPrestacaoConta', nome='Relação de bens da conta')


@pytest.fixture
def tipo_documento_prestacao_conta_ata():
    return baker.make('TipoDocumentoPrestacaoConta', nome='Cópia da ata da prestação de contas')


@pytest.fixture
def tipo_acerto_documento_assinatura(tipo_documento_prestacao_conta_ata):
    tipo_acerto = baker.make('TipoAcertoDocumento', nome='Enviar com assinatura')
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_ata)
    tipo_acerto.save()
    return tipo_acerto


@pytest.fixture
def tipo_acerto_documento_enviar(tipo_documento_prestacao_conta_ata, tipo_documento_prestacao_conta_relacao_bens):
    tipo_acerto = baker.make('TipoAcertoDocumento', nome='Enviar o documento')
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_ata)
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_relacao_bens)
    tipo_acerto.save()
    return tipo_acerto

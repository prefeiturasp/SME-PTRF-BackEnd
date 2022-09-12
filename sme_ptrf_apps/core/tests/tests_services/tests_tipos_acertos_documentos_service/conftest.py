import pytest
from model_bakery import baker


@pytest.fixture
def tipo_acerto_documento_agrupa_categoria_01():
    return baker.make('TipoAcertoDocumento', nome='Teste', categoria='INCLUSAO_CREDITO')


@pytest.fixture
def tipo_acerto_documento_agrupa_categoria_02():
    return baker.make('TipoAcertoDocumento', nome='Teste 2', categoria='INCLUSAO_CREDITO')


@pytest.fixture
def tipo_acerto_documento_agrupa_categoria_03():
    return baker.make('TipoAcertoDocumento', nome='Teste 3', categoria='INCLUSAO_CREDITO')


@pytest.fixture
def tipo_acerto_documento_agrupa_categoria_04():
    return baker.make('TipoAcertoDocumento', nome='Teste 4', categoria='INCLUSAO_GASTO')


@pytest.fixture
def tipo_acerto_documento_agrupa_categoria_05():
    return baker.make('TipoAcertoDocumento', nome='Teste 4', categoria='INCLUSAO_GASTO', ativo=False)


@pytest.fixture
def tipo_documento_prestacao_conta_relacao_bens_01():
    return baker.make('TipoDocumentoPrestacaoConta', nome='Relação de bens da conta')

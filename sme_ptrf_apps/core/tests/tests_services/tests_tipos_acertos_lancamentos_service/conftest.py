import pytest
from model_bakery import baker


@pytest.fixture
def tipo_acerto_lancamento_agrupa_categoria_01():
    return baker.make('TipoAcertoLancamento', nome='Teste', categoria='DEVOLUCAO')


@pytest.fixture
def tipo_acerto_lancamento_agrupa_categoria_02():
    return baker.make('TipoAcertoLancamento', nome='Teste 2', categoria='DEVOLUCAO')


@pytest.fixture
def tipo_acerto_lancamento_agrupa_categoria_03():
    return baker.make('TipoAcertoLancamento', nome='Teste 3', categoria='DEVOLUCAO')


@pytest.fixture
def tipo_acerto_lancamento_agrupa_categoria_04():
    return baker.make('TipoAcertoLancamento', nome='Teste 4', categoria='EDICAO_LANCAMENTO')

@pytest.fixture
def tipo_acerto_lancamento_agrupa_categoria_05():
    return baker.make('TipoAcertoLancamento', nome='Teste 4', categoria='EDICAO_LANCAMENTO', ativo=False)

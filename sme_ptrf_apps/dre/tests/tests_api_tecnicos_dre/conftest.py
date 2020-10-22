import pytest
from model_bakery import baker


@pytest.fixture
def dre_butantan():
    return baker.make(
        'core.Unidade',
        codigo_eol='108100',
        tipo_unidade='DRE',
        nome='BUTANTAN',
        sigla='BT'
    )

@pytest.fixture
def dre_ipiranga():
    return baker.make(
        'core.Unidade',
        codigo_eol='108600',
        tipo_unidade='DRE',
        nome='IPIRANGA',
        sigla='IP'
    )


@pytest.fixture
def tecnico_jose_dre_ipiranga(dre_ipiranga):
    return baker.make(
        'TecnicoDre',
        dre=dre_ipiranga,
        nome='José',
        rf='271170',
        email='tecnico.sobrenome@sme.prefeitura.sp.gov.br',
    )

@pytest.fixture
def tecnico_maria_dre_butantan(dre_butantan):
    return baker.make(
        'TecnicoDre',
        dre=dre_butantan,
        nome='Maria',
        rf='190889',
        email='tecnico.sobrenome@sme.prefeitura.sp.gov.br',
    )

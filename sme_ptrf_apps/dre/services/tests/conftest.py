import pytest

from model_bakery import baker


@pytest.fixture
def membro_service_dre():
    return baker.make(
        'Unidade',
        codigo_eol='712345',
        tipo_unidade='DRE',
        nome='DRE Service',
        sigla='DS',
    )


@pytest.fixture
def membro_service_comissao():
    return baker.make('Comissao', nome='Comissao Service')


@pytest.fixture
def membro_service_comissao_responsavel():
    return baker.make(
        'Comissao',
        nome='Comissao Responsavel',
        responsavel_analise_pc=True,
    )


@pytest.fixture
def membro_service_ata(membro_service_dre):
    return baker.make(
        'AtaParecerTecnico',
        dre=membro_service_dre,
        status_geracao_pdf='NAO_GERADO',
    )


@pytest.fixture
def membro_service():
    return baker.make(
        'MembroComissao',
        rf='7654321',
        nome='Membro Service',
        email='membro.service@teste.com',
        cargo='Professor',
    )


@pytest.fixture
def membro_service_com_dre(membro_service, membro_service_dre):
    membro_service.dre = membro_service_dre
    membro_service.save(update_fields=['dre'])
    return membro_service


@pytest.fixture
def presente_ata_membro_service(membro_service_com_dre, membro_service_ata):
    return baker.make(
        'PresenteAtaDre',
        ata=membro_service_ata,
        rf=membro_service_com_dre.rf,
        nome=membro_service_com_dre.nome,
        cargo=membro_service_com_dre.cargo,
    )


@pytest.fixture
def ata_parecer_tecnico_gerada(membro_service_dre):
    return baker.make(
        'AtaParecerTecnico',
        dre=membro_service_dre,
        status_geracao_pdf='CONCLUIDO',
    )


@pytest.fixture
def presente_ata_nao_gerada(membro_service_com_dre, presente_ata_membro_service):
    return presente_ata_membro_service


@pytest.fixture
def presente_ata_gerada(membro_service_com_dre, ata_parecer_tecnico_gerada):
    return baker.make(
        'PresenteAtaDre',
        ata=ata_parecer_tecnico_gerada,
        rf=membro_service_com_dre.rf,
        nome=membro_service_com_dre.nome,
        cargo=membro_service_com_dre.cargo,
    )

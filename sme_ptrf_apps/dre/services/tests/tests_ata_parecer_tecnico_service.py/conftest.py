from datetime import date
import pytest
from model_bakery import baker

from sme_ptrf_apps.core.models import PrestacaoConta
from sme_ptrf_apps.dre.models import ConsolidadoDRE

pytestmark = pytest.mark.django_db


@pytest.fixture
def unidade_01(dre):
    return baker.make(
        'Unidade',
        criado_em=date(2021, 6, 16),
        nome='Unidade Bcd',
        tipo_unidade='CEU',
        codigo_eol='100000',
        dre=dre,
        sigla='UT1',
        cep='86062280',
        tipo_logradouro='Avenida X',
        logradouro='Logradouro X',
        bairro='Bairro X',
        numero='100',
        complemento='Complemento X',
        telefone='123456789',
        email='mdiori@hotmail.com',
        diretor_nome='Nome diretor X',
        dre_cnpj='85.784.231/0001-96',
        dre_diretor_regional_rf='1234567',
        dre_diretor_regional_nome='Nome diretor regional X',
        dre_designacao_portaria='Portaria nº 0.000',
        dre_designacao_ano='2022',
    )


@pytest.fixture
def unidade_02(dre):
    return baker.make(
        'Unidade',
        criado_em=date(2021, 6, 16),
        nome='Unidade Abc',
        tipo_unidade='CEU',
        codigo_eol='100001',
        dre=dre,
        sigla='UT2',
        cep='86062280',
        tipo_logradouro='Avenida Y',
        logradouro='Logradouro Y',
        bairro='Bairro Y',
        numero='100',
        complemento='Complemento Y',
        telefone='123456789',
        email='mdiori@hotmail.com',
        diretor_nome='Nome diretor Y',
        dre_cnpj='59.716.621/0001-19',
        dre_diretor_regional_rf='1234567',
        dre_diretor_regional_nome='Nome diretor regional Y',
        dre_designacao_portaria='Portaria nº 0.000',
        dre_designacao_ano='2022',
    )


@pytest.fixture
def unidade_03(dre):
    return baker.make(
        'Unidade',
        criado_em=date(2021, 6, 16),
        nome='Unidade Xyz',
        tipo_unidade='CEU',
        codigo_eol='100002',
        dre=dre,
        sigla='UT3',
        cep='86062280',
        tipo_logradouro='Avenida Z',
        logradouro='Logradouro Z',
        bairro='Bairro Z',
        numero='100',
        complemento='Complemento Z',
        telefone='123456789',
        email='mdiori@hotmail.com',
        diretor_nome='Nome diretor Z',
        dre_cnpj='64.642.027/0001-60',
        dre_diretor_regional_rf='1234567',
        dre_diretor_regional_nome='Nome diretor regional Z',
        dre_designacao_portaria='Portaria nº 0.000',
        dre_designacao_ano='2022',
    )


@pytest.fixture
def unidade_04(dre):
    return baker.make(
        'Unidade',
        criado_em=date(2021, 6, 16),
        nome='Unidade Fgh',
        tipo_unidade='CEI',
        codigo_eol='100003',
        dre=dre,
        sigla='UT4',
        cep='86062280',
        tipo_logradouro='Avenida W',
        logradouro='Logradouro W',
        bairro='Bairro W',
        numero='100',
        complemento='Complemento W',
        telefone='123456789',
        email='mdiori@hotmail.com',
        diretor_nome='Nome diretor W',
        dre_cnpj='65.691.322/0001-70',
        dre_diretor_regional_rf='1234567',
        dre_diretor_regional_nome='Nome diretor regional W',
        dre_designacao_portaria='Portaria nº 0.000',
        dre_designacao_ano='2022',
    )


@pytest.fixture
def dre():
    return baker.make(
        'Unidade',
        codigo_eol='111111',
        tipo_unidade='DRE',
        nome='Nome da DRE de teste',
        sigla='DRET'
    )


@pytest.fixture
def associacao_01(unidade_01, periodo):
    return baker.make(
        'Associacao',
        nome='Associação teste 1',
        cnpj='04.524.648/0001-18',
        unidade=unidade_01,
        periodo_inicial=periodo,
        ccm='0.000.00-0',
        email="mdiori@hotmail.com",
        processo_regularidade='123456'
    )


@pytest.fixture
def associacao_02(unidade_02, periodo):
    return baker.make(
        'Associacao',
        nome='Associação teste 2',
        cnpj='52.020.867/0001-02',
        unidade=unidade_02,
        periodo_inicial=periodo,
        ccm='0.000.00-0',
        email="mdiori@hotmail.com",
        processo_regularidade='123458'
    )


@pytest.fixture
def associacao_03(unidade_03, periodo):
    return baker.make(
        'Associacao',
        nome='Associação teste 3',
        cnpj='93.685.623/0001-26',
        unidade=unidade_03,
        periodo_inicial=periodo,
        ccm='0.000.00-0',
        email="mdiori@hotmail.com",
        processo_regularidade='123458'
    )


@pytest.fixture
def associacao_04(unidade_04, periodo):
    return baker.make(
        'Associacao',
        nome='Associação teste 4',
        cnpj='87.894.714/0001-79',
        unidade=unidade_04,
        periodo_inicial=periodo,
        ccm='0.000.00-0',
        email="mdiori@hotmail.com",
        processo_regularidade='123458'
    )


@pytest.fixture
def periodo_anterior():
    return baker.make(
        'Periodo',
        referencia='2021.2',
        data_inicio_realizacao_despesas=date(2021, 6, 16),
        data_fim_realizacao_despesas=date(2021, 12, 31),
    )


@pytest.fixture
def periodo(periodo_anterior):
    return baker.make(
        'Periodo',
        referencia='2022.1',
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 12, 31),
        periodo_anterior=periodo_anterior,
    )


@pytest.fixture
def ata_parecer_tecnico(
    dre,
    periodo,
    consolidado_dre,
):
    return baker.make(
        'AtaParecerTecnico',
        periodo=periodo,
        dre=dre,
        status_geracao_pdf='CONCLUIDO',
        numero_ata=1,
        data_reuniao=date(2022, 6, 25),
        local_reuniao='Teste local da reunião',
        comentarios='Teste comentarios',
        consolidado_dre=consolidado_dre,
        sequencia_de_publicacao=1
    )


@pytest.fixture
def prestacao_conta_aprovada_01(periodo, associacao_01, consolidado_dre):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao_01,
        data_recebimento=date(2022, 1, 2),
        status=PrestacaoConta.STATUS_APROVADA,
        publicada=True,
        consolidado_dre=consolidado_dre
    )

@pytest.fixture
def prestacao_conta_aprovada_02(periodo, associacao_02, consolidado_dre):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao_02,
        data_recebimento=date(2022, 1, 2),
        status=PrestacaoConta.STATUS_APROVADA,
        publicada=True,
        consolidado_dre=consolidado_dre
    )


@pytest.fixture
def prestacao_conta_aprovada_03(periodo, associacao_03, consolidado_dre):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao_03,
        data_recebimento=date(2022, 1, 2),
        status=PrestacaoConta.STATUS_APROVADA,
        publicada=True,
        consolidado_dre=consolidado_dre
    )


@pytest.fixture
def prestacao_conta_aprovada_04(periodo, associacao_04, consolidado_dre):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao_04,
        data_recebimento=date(2022, 1, 2),
        status=PrestacaoConta.STATUS_APROVADA,
        publicada=True,
        consolidado_dre=consolidado_dre
    )


@pytest.fixture
def consolidado_dre(periodo, dre):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre,
        periodo=periodo,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS
    )


@pytest.fixture
def consolidado_dre_com_pc(
    consolidado_dre,
    prestacao_conta_aprovada_01,
    prestacao_conta_aprovada_02,
    prestacao_conta_aprovada_03,
    prestacao_conta_aprovada_04
):
    consolidado_dre.pcs_do_consolidado.add(prestacao_conta_aprovada_01)
    consolidado_dre.pcs_do_consolidado.add(prestacao_conta_aprovada_02)
    consolidado_dre.pcs_do_consolidado.add(prestacao_conta_aprovada_03)
    consolidado_dre.pcs_do_consolidado.add(prestacao_conta_aprovada_04)
    consolidado_dre.save()
    return consolidado_dre


@pytest.fixture
def tipo_conta_cheque(tipo_conta):
    return tipo_conta


@pytest.fixture
def tipo_conta_cartao():
    return baker.make('TipoConta', nome='Cartão')


@pytest.fixture
def conta_associacao_01(associacao_02, tipo_conta_cheque):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao_02,
        tipo_conta=tipo_conta_cheque,
        banco_nome='Teste nome do banco',
        agencia='12345',
        numero_conta='123456-x',
        numero_cartao='123456123456'
    )


@pytest.fixture
def conta_associacao_02(associacao_01, tipo_conta_cartao):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao_01,
        tipo_conta=tipo_conta_cartao,
        banco_nome='Teste nome do banco',
        agencia='12345',
        numero_conta='123456-x',
        numero_cartao='123456123456'
    )
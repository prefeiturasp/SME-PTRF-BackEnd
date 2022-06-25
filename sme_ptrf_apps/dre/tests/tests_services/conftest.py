from datetime import date
import pytest
from model_bakery import baker

from sme_ptrf_apps.core.models import PrestacaoConta
from ...models import ConsolidadoDRE

pytestmark = pytest.mark.django_db


@pytest.fixture
def dre_teste_service_consolidado_dre():
    return baker.make(
        'Unidade',
        codigo_eol='108500',
        tipo_unidade='DRE',
        nome='Dre Teste Model Consolidado Dre',
        sigla='A'
    )


@pytest.fixture
def periodo_anterior_teste_service_consolidado_dre():
    return baker.make(
        'Periodo',
        referencia='2021.2',
        data_inicio_realizacao_despesas=date(2021, 6, 16),
        data_fim_realizacao_despesas=date(2021, 12, 31),
    )


@pytest.fixture
def periodo_teste_service_consolidado_dre(periodo_anterior_teste_service_consolidado_dre):
    return baker.make(
        'Periodo',
        referencia='2022.1',
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 12, 31),
        periodo_anterior=periodo_anterior_teste_service_consolidado_dre,
    )


@pytest.fixture
def consolidado_dre_teste_service_consolidado_dre(periodo_teste_service_consolidado_dre,
                                                  dre_teste_service_consolidado_dre):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_service_consolidado_dre,
        periodo=periodo_teste_service_consolidado_dre,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS
    )


@pytest.fixture
def consolidado_dre_teste_service_consolidado_dre_status_gerados_totais(periodo_teste_service_consolidado_dre,
                                                                        dre_teste_service_consolidado_dre):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_service_consolidado_dre,
        periodo=periodo_teste_service_consolidado_dre,
        status=ConsolidadoDRE.STATUS_GERADOS_TOTAIS
    )


@pytest.fixture
def tipo_conta_cheque_teste_service(tipo_conta):
    return tipo_conta


@pytest.fixture
def tipo_conta_cartao_teste_service():
    return baker.make('TipoConta', nome='Cartão')


@pytest.fixture
def ano_analise_regularidade_2022_teste_service():
    return baker.make('AnoAnaliseRegularidade', ano=2022)


@pytest.fixture
def comissao_exame_contas_teste_service():
    return baker.make('Comissao', nome='Exame de Contas')


@pytest.fixture
def parametros_dre_teste_service(comissao_exame_contas_teste_service):
    return baker.make(
        'ParametrosDre',
        comissao_exame_contas=comissao_exame_contas_teste_service
    )


@pytest.fixture
def membro_comissao_teste_service(comissao_exame_contas_teste_service, dre_teste_service_consolidado_dre):
    membro = baker.make(
        'MembroComissao',
        rf='123456',
        nome='Beto',
        cargo='teste',
        email='beto@teste.com',
        dre=dre_teste_service_consolidado_dre,
        comissoes=[comissao_exame_contas_teste_service]
    )
    return membro


@pytest.fixture
def retorna_parcial_false():
    return False


@pytest.fixture
def retorna_username():
    return '6375548'

@pytest.fixture
def conta_associacao_teste_service(associacao_teste_service_02, tipo_conta_cheque_teste_service):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao_teste_service_02,
        tipo_conta=tipo_conta_cheque_teste_service,
        banco_nome='Banco do Brasil',
        agencia='12345',
        numero_conta='123456-x',
        numero_cartao='534653264523'
    )

@pytest.fixture
def conta_associacao_teste_service_02(associacao_teste_service, tipo_conta_cartao_teste_service):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao_teste_service,
        tipo_conta=tipo_conta_cartao_teste_service,
        banco_nome='Banco do Brasil',
        agencia='12345',
        numero_conta='123456-x',
        numero_cartao='534653264523'
    )

@pytest.fixture
def unidade_teste_service(dre_teste_service_consolidado_dre):
    return baker.make(
        'Unidade',
        nome='Escola Teste',
        tipo_unidade='DRE',
        codigo_eol='123456',
        dre=dre_teste_service_consolidado_dre,
        sigla='ET',
        cep='5868120',
        tipo_logradouro='Travessa',
        logradouro='dos Testes',
        bairro='COHAB INSTITUTO ADVENTISTA',
        numero='200',
        complemento='fundos',
        telefone='58212627',
        email='emefjopfilho@sme.prefeitura.sp.gov.br',
        diretor_nome='Pedro Amaro',
        dre_cnpj='63.058.286/0001-86',
        dre_diretor_regional_rf='1234567',
        dre_diretor_regional_nome='Anthony Edward Stark',
        dre_designacao_portaria='Portaria nº 0.000',
        dre_designacao_ano='2017',
    )


@pytest.fixture
def unidade_teste_service_02(dre_teste_service_consolidado_dre):
    return baker.make(
        'Unidade',
        nome='Escola Teste 02',
        tipo_unidade='DRE',
        codigo_eol='123457',
        dre=dre_teste_service_consolidado_dre,
        sigla='EA',
    )


@pytest.fixture
def associacao_teste_service(unidade_teste_service, periodo_teste_service_consolidado_dre):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='52.302.275/0001-83',
        unidade=unidade_teste_service,
        periodo_inicial=periodo_teste_service_consolidado_dre,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456'
    )

@pytest.fixture
def associacao_teste_service_02(unidade_teste_service_02, periodo_teste_service_consolidado_dre):
    return baker.make(
        'Associacao',
        nome='Escola Teste 02',
        cnpj='10.118.346/0001-42',
        unidade=unidade_teste_service_02,
        periodo_inicial=periodo_teste_service_consolidado_dre,
        ccm='0.000.00-0',
        email="ollyver.ottoboni@gmail.com",
        processo_regularidade='123458'
    )

@pytest.fixture
def prestacao_conta_aprovada_teste_service(periodo_teste_service_consolidado_dre, associacao_teste_service):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_teste_service_consolidado_dre,
        associacao=associacao_teste_service,
        data_recebimento=date(2022, 1, 2),
        status=PrestacaoConta.STATUS_APROVADA,
    )

@pytest.fixture
def prestacao_conta_reprovada_teste_service_publicada(periodo_teste_service_consolidado_dre, associacao_teste_service_02, consolidado_dre_teste_service_consolidado_dre):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_teste_service_consolidado_dre,
        associacao=associacao_teste_service_02,
        data_recebimento=date(2022, 1, 2),
        status=PrestacaoConta.STATUS_REPROVADA,
        publicada=True,
        consolidado_dre=consolidado_dre_teste_service_consolidado_dre
    )


@pytest.fixture
def prestacao_conta_aprovada_teste_service_pc_aprovada_info_pc(periodo_teste_service_consolidado_dre, associacao_teste_service, consolidado_dre_teste_service_consolidado_dre):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_teste_service_consolidado_dre,
        associacao=associacao_teste_service,
        data_recebimento=date(2022, 1, 2),
        status=PrestacaoConta.STATUS_APROVADA,
        publicada=True,
        consolidado_dre=consolidado_dre_teste_service_consolidado_dre
    )

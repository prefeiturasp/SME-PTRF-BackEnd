from datetime import date
import pytest
from model_bakery import baker
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

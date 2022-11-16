from datetime import date
import pytest
from model_bakery import baker
from ...models import ConsolidadoDRE

pytestmark = pytest.mark.django_db


@pytest.fixture
def dre_teste_model_consolidado_dre():
    return baker.make(
        'Unidade',
        codigo_eol='108500',
        tipo_unidade='DRE',
        nome='Dre Teste Model Consolidado Dre',
        sigla='A'
    )

@pytest.fixture
def periodo_anterior_teste_model_consolidado_dre():
    return baker.make(
        'Periodo',
        referencia='2021.2',
        data_inicio_realizacao_despesas=date(2021, 6, 16),
        data_fim_realizacao_despesas=date(2021, 12, 31),
    )


@pytest.fixture
def periodo_teste_model_consolidado_dre(periodo_anterior_teste_model_consolidado_dre):
    return baker.make(
        'Periodo',
        referencia='2022.1',
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 12, 31),
        periodo_anterior=periodo_anterior_teste_model_consolidado_dre,
    )


@pytest.fixture
def consolidado_dre_teste_model_consolidado_dre(periodo_teste_model_consolidado_dre, dre_teste_model_consolidado_dre):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_model_consolidado_dre,
        periodo=periodo_teste_model_consolidado_dre,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS
    )


@pytest.fixture
def consolidado_dre_em_analise(periodo_teste_model_consolidado_dre, dre_teste_model_consolidado_dre):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_model_consolidado_dre,
        periodo=periodo_teste_model_consolidado_dre,
        status=ConsolidadoDRE.STATUS_GERADOS_TOTAIS,
        status_sme=ConsolidadoDRE.STATUS_SME_EM_ANALISE,
    )


@pytest.fixture
def comissao_contas():
    return baker.make('Comissao', nome='Exame de Contas')


@pytest.fixture
def parametros_dre_comissoes(comissao_contas):
    return baker.make(
        'ParametrosDre',
        comissao_exame_contas=comissao_contas
    )


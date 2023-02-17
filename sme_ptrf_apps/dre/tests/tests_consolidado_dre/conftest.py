from datetime import date, timedelta
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
        sigla='A',
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
def consolidado_dre_teste_model_consolidado_dre(periodo_teste_model_consolidado_dre, dre_teste_model_consolidado_dre, analise_atual_consolidado_dre_2022):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_model_consolidado_dre,
        analise_atual=analise_atual_consolidado_dre_2022,
        periodo=periodo_teste_model_consolidado_dre,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS
    )


@pytest.fixture
def analise_atual_consolidado_dre_2022():
    return baker.make(
        'AnaliseConsolidadoDre',
        data_devolucao=date.today(),
        data_limite=date.today(),
        data_retorno_analise=date.today(),
        relatorio_acertos_versao=('FINAL', 'final'),
        relatorio_acertos_status='CONCLUIDO',
        relatorio_acertos_gerado_em=date.today()
    )


@pytest.fixture
def consolidado_dre_em_analise(periodo_teste_model_consolidado_dre, dre_teste_model_consolidado_dre, analise_atual_consolidado_dre_2022):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_model_consolidado_dre,
        analise_atual=analise_atual_consolidado_dre_2022,
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


@pytest.fixture
def unidade_do_consolidado(dre_teste_model_consolidado_dre):
    return baker.make(
        'Unidade',
        nome='Escola Teste',
        tipo_unidade='CEU',
        codigo_eol='123456',
        dre=dre_teste_model_consolidado_dre,
    )


@pytest.fixture
def associacao_do_consolidado(unidade_do_consolidado):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='52.302.275/0001-83',
        unidade=unidade_do_consolidado,
    )


@pytest.fixture
def prestacao_conta_do_consolidado(
    periodo_teste_model_consolidado_dre,
    associacao_do_consolidado
):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_teste_model_consolidado_dre,
        associacao=associacao_do_consolidado,
    )

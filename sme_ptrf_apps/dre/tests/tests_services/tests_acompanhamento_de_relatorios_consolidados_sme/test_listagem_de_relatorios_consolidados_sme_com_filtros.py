import pytest
from datetime import date
from sme_ptrf_apps.dre.services.consolidado_dre_service import ListagemPorStatusComFiltros
from model_bakery import baker

from sme_ptrf_apps.core.models import PrestacaoConta
from sme_ptrf_apps.dre.models import ConsolidadoDRE

pytestmark = pytest.mark.django_db


@pytest.fixture
def associacao_teste_listagem_01(periodo_anterior_teste_listagem_com_filtros_01):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='52.302.275/0001-83',
        periodo_inicial=periodo_anterior_teste_listagem_com_filtros_01,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456'
    )


@pytest.fixture
def associacao_teste_listagem_02(periodo_anterior_teste_listagem_com_filtros_01):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='13.392.303/0001-49',
        periodo_inicial=periodo_anterior_teste_listagem_com_filtros_01,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456'
    )


@pytest.fixture
def associacao_teste_listagem_03(periodo_anterior_teste_listagem_com_filtros_01):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='57.876.269/0001-53',
        periodo_inicial=periodo_anterior_teste_listagem_com_filtros_01,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456'
    )


@pytest.fixture
def associacao_teste_listagem_04(periodo_anterior_teste_listagem_com_filtros_01):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='84.326.913/0001-92',
        periodo_inicial=periodo_anterior_teste_listagem_com_filtros_01,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456'
    )


@pytest.fixture
def associacao_teste_listagem_05(periodo_anterior_teste_listagem_com_filtros_01):
    return baker.make(
        'Associacao',
        nome='Escola Teste Retificações',
        cnpj='13.473.276/0001-39',
        periodo_inicial=periodo_anterior_teste_listagem_com_filtros_01,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456'
    )


@pytest.fixture
def periodo_anterior_teste_listagem_com_filtros_01():
    return baker.make(
        'Periodo',
        referencia='2021.2',
        data_inicio_realizacao_despesas=date(2021, 6, 16),
        data_fim_realizacao_despesas=date(2021, 12, 31),
    )


@pytest.fixture
def periodo_teste_listagem_com_filtros_01(periodo_anterior_teste_listagem_com_filtros_01):
    return baker.make(
        'Periodo',
        referencia='2022.1',
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 12, 31),
        periodo_anterior=periodo_anterior_teste_listagem_com_filtros_01,
    )


@pytest.fixture
def prestacao_conta_teste_listagem_com_filtros_01(
    periodo_teste_listagem_com_filtros_01,
    associacao_teste_listagem_01,
    consolidado_teste_listagem_com_filtros_01,
    periodo_anterior_teste_listagem_com_filtros_01
):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_anterior_teste_listagem_com_filtros_01,
        associacao=associacao_teste_listagem_01,
        data_recebimento=date(2022, 1, 2),
        status=PrestacaoConta.STATUS_APROVADA,
        consolidado_dre=consolidado_teste_listagem_com_filtros_01
    )


@pytest.fixture
def prestacao_conta_teste_listagem_com_filtros_02(
    periodo_teste_listagem_com_filtros_01,
    associacao_teste_listagem_02,
    consolidado_teste_listagem_com_filtros_02,
    periodo_anterior_teste_listagem_com_filtros_01
):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_anterior_teste_listagem_com_filtros_01,
        associacao=associacao_teste_listagem_02,
        data_recebimento=date(2022, 1, 2),
        status=PrestacaoConta.STATUS_APROVADA,
        consolidado_dre=consolidado_teste_listagem_com_filtros_02
    )


@pytest.fixture
def prestacao_conta_teste_listagem_com_filtros_03(
    periodo_teste_listagem_com_filtros_01,
    associacao_teste_listagem_03,
    consolidado_teste_listagem_com_filtros_03,
    periodo_anterior_teste_listagem_com_filtros_01
):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_anterior_teste_listagem_com_filtros_01,
        associacao=associacao_teste_listagem_03,
        data_recebimento=date(2022, 1, 2),
        status=PrestacaoConta.STATUS_APROVADA,
        consolidado_dre=consolidado_teste_listagem_com_filtros_03
    )


@pytest.fixture
def prestacao_conta_teste_listagem_com_filtros_04(
    periodo_teste_listagem_com_filtros_01,
    associacao_teste_listagem_04,
    consolidado_teste_listagem_com_filtros_04,
    periodo_anterior_teste_listagem_com_filtros_01
):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_anterior_teste_listagem_com_filtros_01,
        associacao=associacao_teste_listagem_04,
        data_recebimento=date(2022, 1, 2),
        status=PrestacaoConta.STATUS_APROVADA,
        consolidado_dre=consolidado_teste_listagem_com_filtros_04
    )


@pytest.fixture
def prestacao_conta_teste_listagem_com_retificacao_01(
    periodo_teste_listagem_com_filtros_01,
    associacao_teste_listagem_05,
    consolidado_teste_listagem_com_filtros_retificacao_01,
    periodo_anterior_teste_listagem_com_filtros_01
):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_anterior_teste_listagem_com_filtros_01,
        associacao=associacao_teste_listagem_05,
        data_recebimento=date(2022, 1, 2),
        status=PrestacaoConta.STATUS_APROVADA,
        consolidado_dre=consolidado_teste_listagem_com_filtros_retificacao_01
    )


@pytest.fixture
def dre_teste_listagem_com_filtros_01():
    return baker.make(
        'Unidade',
        codigo_eol='109000',
        tipo_unidade='DRE',
        nome='Dre Teste Listagem Com Filtros 01',
        sigla='A'
    )


@pytest.fixture
def dre_teste_listagem_com_filtros_02_nao_gerado():
    return baker.make(
        'Unidade',
        codigo_eol='109100',
        tipo_unidade='DRE',
        nome='Dre Teste Listagem Com Filtros 02 Não Gerado',
        sigla='A'
    )


@pytest.fixture
def consolidado_teste_listagem_com_filtros_01(
    periodo_teste_listagem_com_filtros_01,
    dre_teste_listagem_com_filtros_01
):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_listagem_com_filtros_01,
        periodo=periodo_teste_listagem_com_filtros_01,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS,
        status_sme=ConsolidadoDRE.STATUS_SME_NAO_PUBLICADO,
        eh_parcial=True,
        sequencia_de_publicacao=1
    )


@pytest.fixture
def consolidado_teste_listagem_com_filtros_02(
    periodo_teste_listagem_com_filtros_01,
    dre_teste_listagem_com_filtros_01
):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_listagem_com_filtros_01,
        periodo=periodo_teste_listagem_com_filtros_01,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS,
        status_sme=ConsolidadoDRE.STATUS_SME_PUBLICADO,
        eh_parcial=True,
        sequencia_de_publicacao=2
    )


@pytest.fixture
def consolidado_teste_listagem_com_filtros_03(
    periodo_teste_listagem_com_filtros_01,
    dre_teste_listagem_com_filtros_01
):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_listagem_com_filtros_01,
        periodo=periodo_teste_listagem_com_filtros_01,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS,
        status_sme=ConsolidadoDRE.STATUS_SME_NAO_PUBLICADO,
        eh_parcial=True,
        sequencia_de_publicacao=3
    )


@pytest.fixture
def consolidado_teste_listagem_com_filtros_04(
    periodo_teste_listagem_com_filtros_01,
    dre_teste_listagem_com_filtros_01
):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_listagem_com_filtros_01,
        periodo=periodo_teste_listagem_com_filtros_01,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS,
        status_sme=ConsolidadoDRE.STATUS_SME_NAO_PUBLICADO,
        eh_parcial=False,
        sequencia_de_publicacao=0
    )


@pytest.fixture
def consolidado_teste_listagem_com_filtros_retificado(
    periodo_teste_listagem_com_filtros_01,
    dre_teste_listagem_com_filtros_01
):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_listagem_com_filtros_01,
        periodo=periodo_teste_listagem_com_filtros_01,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS,
        status_sme=ConsolidadoDRE.STATUS_SME_NAO_PUBLICADO,
        eh_parcial=True,
        sequencia_de_publicacao=5,
    )


@pytest.fixture
def consolidado_teste_listagem_com_filtros_retificacao_01(
    periodo_teste_listagem_com_filtros_01,
    dre_teste_listagem_com_filtros_01,
    consolidado_teste_listagem_com_filtros_retificado,
):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_listagem_com_filtros_01,
        periodo=periodo_teste_listagem_com_filtros_01,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS,
        status_sme=ConsolidadoDRE.STATUS_SME_NAO_PUBLICADO,
        eh_parcial=True,
        sequencia_de_publicacao=5,
        sequencia_de_retificacao=5,
        consolidado_retificado=consolidado_teste_listagem_com_filtros_retificado,
    )


def test_teste_listagem_com_filtros_sem_filtros_retificacao(
    periodo_teste_listagem_com_filtros_01,
    dre_teste_listagem_com_filtros_01,
    consolidado_teste_listagem_com_filtros_retificado,
    consolidado_teste_listagem_com_filtros_retificacao_01,
    prestacao_conta_teste_listagem_com_retificacao_01,
):
    listagem = ListagemPorStatusComFiltros(
        periodo=periodo_teste_listagem_com_filtros_01,
        dre=None,
        tipo_relatorio=None,
        status_sme=None
    ).retorna_listagem()

    resultado_esperado = [
        {
            'nome_da_dre': 'Dre Teste Listagem Com Filtros 01',
            'tipo_relatorio': 'Retificação',
            'total_unidades_no_relatorio': 1,
            'data_recebimento': None,
            'pode_visualizar': True,
            'status_sme': 'NAO_PUBLICADO',
            'status_sme_label': 'Não publicada no D.O.',
            "uuid_consolidado_dre": f"{consolidado_teste_listagem_com_filtros_retificacao_01.uuid}",
            "uuid_dre": f"{dre_teste_listagem_com_filtros_01.uuid}"
        },
        {
            "nome_da_dre": dre_teste_listagem_com_filtros_01.nome,
            "tipo_relatorio": "Parcial #5",
            "total_unidades_no_relatorio": 1,
            "data_recebimento": None,
            "status_sme": "NAO_PUBLICADO",
            "status_sme_label": "Não publicada no D.O.",
            "pode_visualizar": True,
            "uuid_consolidado_dre": f"{consolidado_teste_listagem_com_filtros_retificado.uuid}",
            "uuid_dre": f"{dre_teste_listagem_com_filtros_01.uuid}"
        },
    ]

    assert listagem == resultado_esperado


def test_teste_listagem_com_filtros__filtro_nao_gerado_e_tipo_relatorio_parcial(
    periodo_teste_listagem_com_filtros_01,
    dre_teste_listagem_com_filtros_02_nao_gerado,
    dre_teste_listagem_com_filtros_01,
    consolidado_teste_listagem_com_filtros_04,
    consolidado_teste_listagem_com_filtros_03,
    consolidado_teste_listagem_com_filtros_02,
    consolidado_teste_listagem_com_filtros_01,
    prestacao_conta_teste_listagem_com_filtros_01,
    prestacao_conta_teste_listagem_com_filtros_02,
    prestacao_conta_teste_listagem_com_filtros_03,
    prestacao_conta_teste_listagem_com_filtros_04,

):
    listagem = ListagemPorStatusComFiltros(
        periodo=periodo_teste_listagem_com_filtros_01,
        dre=None,
        tipo_relatorio='PARCIAL',
        status_sme=['NAO_GERADO']
    ).retorna_listagem()

    resultado_esperado = []

    assert listagem == resultado_esperado


def test_teste_listagem_com_filtros__filtro_nao_gerado_e_tipo_relatorio_unico(
    periodo_teste_listagem_com_filtros_01,
    dre_teste_listagem_com_filtros_02_nao_gerado,
    dre_teste_listagem_com_filtros_01,
    consolidado_teste_listagem_com_filtros_04,
    consolidado_teste_listagem_com_filtros_03,
    consolidado_teste_listagem_com_filtros_02,
    consolidado_teste_listagem_com_filtros_01,
    prestacao_conta_teste_listagem_com_filtros_01,
    prestacao_conta_teste_listagem_com_filtros_02,
    prestacao_conta_teste_listagem_com_filtros_03,
    prestacao_conta_teste_listagem_com_filtros_04,

):
    listagem = ListagemPorStatusComFiltros(
        periodo=periodo_teste_listagem_com_filtros_01,
        dre=None,
        tipo_relatorio='UNICO',
        status_sme=['NAO_GERADO']
    ).retorna_listagem()

    resultado_esperado = []

    assert listagem == resultado_esperado


def test_teste_listagem_com_filtros__filtro_nao_gerado_publicado_e_nao_publicado_e_tipo_relatorio_unico(
    periodo_teste_listagem_com_filtros_01,
    dre_teste_listagem_com_filtros_02_nao_gerado,
    dre_teste_listagem_com_filtros_01,
    consolidado_teste_listagem_com_filtros_04,
    consolidado_teste_listagem_com_filtros_03,
    consolidado_teste_listagem_com_filtros_02,
    consolidado_teste_listagem_com_filtros_01,
    prestacao_conta_teste_listagem_com_filtros_01,
    prestacao_conta_teste_listagem_com_filtros_02,
    prestacao_conta_teste_listagem_com_filtros_03,
    prestacao_conta_teste_listagem_com_filtros_04,

):
    listagem = ListagemPorStatusComFiltros(
        periodo=periodo_teste_listagem_com_filtros_01,
        dre=None,
        tipo_relatorio='UNICO',
        status_sme=['NAO_GERADO', 'PUBLICADO', 'NAO_PUBLICADO']
    ).retorna_listagem()

    resultado_esperado = [
        {
            "nome_da_dre": dre_teste_listagem_com_filtros_01.nome,
            "tipo_relatorio": "Único",
            "total_unidades_no_relatorio": 1,
            "data_recebimento": None,
            "status_sme": "NAO_PUBLICADO",
            "status_sme_label": "Não publicada no D.O.",
            "pode_visualizar": True,
            "uuid_consolidado_dre": f"{consolidado_teste_listagem_com_filtros_04.uuid}",
            "uuid_dre": f"{dre_teste_listagem_com_filtros_01.uuid}"
        },
    ]

    assert listagem == resultado_esperado


def test_teste_listagem_com_filtros__filtro_nao_gerado_publicado_e_nao_publicado(
    periodo_teste_listagem_com_filtros_01,
    dre_teste_listagem_com_filtros_02_nao_gerado,
    dre_teste_listagem_com_filtros_01,
    consolidado_teste_listagem_com_filtros_03,
    consolidado_teste_listagem_com_filtros_02,
    consolidado_teste_listagem_com_filtros_01,
    prestacao_conta_teste_listagem_com_filtros_01,
    prestacao_conta_teste_listagem_com_filtros_02,
    prestacao_conta_teste_listagem_com_filtros_03,

):
    listagem = ListagemPorStatusComFiltros(
        periodo=periodo_teste_listagem_com_filtros_01,
        dre=None,
        tipo_relatorio=None,
        status_sme=['NAO_GERADO', 'PUBLICADO', 'NAO_PUBLICADO']
    ).retorna_listagem()

    resultado_esperado = [
        {
            "nome_da_dre": dre_teste_listagem_com_filtros_01.nome,
            "tipo_relatorio": "Parcial #3",
            "total_unidades_no_relatorio": 1,
            "data_recebimento": None,
            "status_sme": "NAO_PUBLICADO",
            "status_sme_label": "Não publicada no D.O.",
            "pode_visualizar": True,
            "uuid_consolidado_dre": f"{consolidado_teste_listagem_com_filtros_03.uuid}",
            "uuid_dre": f"{dre_teste_listagem_com_filtros_01.uuid}"
        },
        {
            "nome_da_dre": dre_teste_listagem_com_filtros_01.nome,
            "tipo_relatorio": "Parcial #2",
            "total_unidades_no_relatorio": 1,
            "data_recebimento": None,
            "status_sme": "PUBLICADO",
            "status_sme_label": "Publicada no D.O.",
            "pode_visualizar": True,
            "uuid_consolidado_dre": f"{consolidado_teste_listagem_com_filtros_02.uuid}",
            "uuid_dre": f"{dre_teste_listagem_com_filtros_01.uuid}"
        },
        {
            "nome_da_dre": dre_teste_listagem_com_filtros_01.nome,
            "tipo_relatorio": "Parcial #1",
            "total_unidades_no_relatorio": 1,
            "data_recebimento": None,
            "status_sme": "NAO_PUBLICADO",
            "status_sme_label": "Não publicada no D.O.",
            "pode_visualizar": True,
            "uuid_consolidado_dre": f"{consolidado_teste_listagem_com_filtros_01.uuid}",
            "uuid_dre": f"{dre_teste_listagem_com_filtros_01.uuid}"
        },
        {
            "nome_da_dre": dre_teste_listagem_com_filtros_02_nao_gerado.nome,
            "tipo_relatorio": "-",
            "total_unidades_no_relatorio": '-',
            "data_recebimento": None,
            "status_sme": "NAO_GERADO",
            "status_sme_label": "Não gerado",
            "pode_visualizar": False,
            "uuid_consolidado_dre": None,
            "uuid_dre": f"{dre_teste_listagem_com_filtros_02_nao_gerado.uuid}"
        },
    ]

    assert listagem == resultado_esperado


def test_teste_listagem_com_filtros__filtro_nao_gerado(
    periodo_teste_listagem_com_filtros_01,
    dre_teste_listagem_com_filtros_02_nao_gerado,
    consolidado_teste_listagem_com_filtros_03,
    consolidado_teste_listagem_com_filtros_02,
    consolidado_teste_listagem_com_filtros_01,
    prestacao_conta_teste_listagem_com_filtros_01,
    prestacao_conta_teste_listagem_com_filtros_02,
    prestacao_conta_teste_listagem_com_filtros_03,

):
    listagem = ListagemPorStatusComFiltros(
        periodo=periodo_teste_listagem_com_filtros_01,
        dre=None,
        tipo_relatorio=None,
        status_sme=['NAO_GERADO']
    ).retorna_listagem()

    resultado_esperado = [
        {
            "nome_da_dre": dre_teste_listagem_com_filtros_02_nao_gerado.nome,
            "tipo_relatorio": "-",
            "total_unidades_no_relatorio": '-',
            "data_recebimento": None,
            "status_sme": "NAO_GERADO",
            "status_sme_label": "Não gerado",
            "pode_visualizar": False,
            "uuid_consolidado_dre": None,
            "uuid_dre": f"{dre_teste_listagem_com_filtros_02_nao_gerado.uuid}"
        }
    ]

    assert listagem == resultado_esperado


def test_teste_listagem_com_filtros__filtro_publicado_e_nao_publicado(
    periodo_teste_listagem_com_filtros_01,
    dre_teste_listagem_com_filtros_01,
    consolidado_teste_listagem_com_filtros_03,
    consolidado_teste_listagem_com_filtros_02,
    consolidado_teste_listagem_com_filtros_01,
    prestacao_conta_teste_listagem_com_filtros_01,
    prestacao_conta_teste_listagem_com_filtros_02,
    prestacao_conta_teste_listagem_com_filtros_03,

):
    listagem = ListagemPorStatusComFiltros(
        periodo=periodo_teste_listagem_com_filtros_01,
        dre=None,
        tipo_relatorio=None,
        status_sme=['PUBLICADO', 'NAO_PUBLICADO']
    ).retorna_listagem()

    resultado_esperado = [
        {
            "nome_da_dre": dre_teste_listagem_com_filtros_01.nome,
            "tipo_relatorio": "Parcial #3",
            "total_unidades_no_relatorio": 1,
            "data_recebimento": None,
            "status_sme": "NAO_PUBLICADO",
            "status_sme_label": "Não publicada no D.O.",
            "pode_visualizar": True,
            "uuid_consolidado_dre": f"{consolidado_teste_listagem_com_filtros_03.uuid}",
            "uuid_dre": f"{dre_teste_listagem_com_filtros_01.uuid}"
        },
        {
            "nome_da_dre": dre_teste_listagem_com_filtros_01.nome,
            "tipo_relatorio": "Parcial #2",
            "total_unidades_no_relatorio": 1,
            "data_recebimento": None,
            "status_sme": "PUBLICADO",
            "status_sme_label": "Publicada no D.O.",
            "pode_visualizar": True,
            "uuid_consolidado_dre": f"{consolidado_teste_listagem_com_filtros_02.uuid}",
            "uuid_dre": f"{dre_teste_listagem_com_filtros_01.uuid}"
        },
        {
            "nome_da_dre": dre_teste_listagem_com_filtros_01.nome,
            "tipo_relatorio": "Parcial #1",
            "total_unidades_no_relatorio": 1,
            "data_recebimento": None,
            "status_sme": "NAO_PUBLICADO",
            "status_sme_label": "Não publicada no D.O.",
            "pode_visualizar": True,
            "uuid_consolidado_dre": f"{consolidado_teste_listagem_com_filtros_01.uuid}",
            "uuid_dre": f"{dre_teste_listagem_com_filtros_01.uuid}"
        },
    ]

    assert listagem == resultado_esperado


def test_teste_listagem_com_filtros__filtro_publicado(
    periodo_teste_listagem_com_filtros_01,
    dre_teste_listagem_com_filtros_01,
    consolidado_teste_listagem_com_filtros_02,
    consolidado_teste_listagem_com_filtros_01,
    prestacao_conta_teste_listagem_com_filtros_02,

):
    listagem = ListagemPorStatusComFiltros(
        periodo=periodo_teste_listagem_com_filtros_01,
        dre=None,
        tipo_relatorio=None,
        status_sme=['PUBLICADO']
    ).retorna_listagem()

    resultado_esperado = [
        {
            "nome_da_dre": dre_teste_listagem_com_filtros_01.nome,
            "tipo_relatorio": "Parcial #2",
            "total_unidades_no_relatorio": 1,
            "data_recebimento": None,
            "status_sme": "PUBLICADO",
            "status_sme_label": "Publicada no D.O.",
            "pode_visualizar": True,
            "uuid_consolidado_dre": f"{consolidado_teste_listagem_com_filtros_02.uuid}",
            "uuid_dre": f"{dre_teste_listagem_com_filtros_01.uuid}"
        },
    ]

    assert listagem == resultado_esperado


def test_teste_listagem_com_filtros__sem_filtros(
    periodo_teste_listagem_com_filtros_01,
    dre_teste_listagem_com_filtros_01,
    consolidado_teste_listagem_com_filtros_01,
    prestacao_conta_teste_listagem_com_filtros_01,

):
    listagem = ListagemPorStatusComFiltros(
        periodo=periodo_teste_listagem_com_filtros_01,
        dre=None,
        tipo_relatorio=None,
        status_sme=None
    ).retorna_listagem()

    resultado_esperado = [
        {
            "nome_da_dre": dre_teste_listagem_com_filtros_01.nome,
            "tipo_relatorio": "Parcial #1",
            "total_unidades_no_relatorio": 1,
            "data_recebimento": None,
            "status_sme": "NAO_PUBLICADO",
            "status_sme_label": "Não publicada no D.O.",
            "pode_visualizar": True,
            "uuid_consolidado_dre": f"{consolidado_teste_listagem_com_filtros_01.uuid}",
            "uuid_dre": f"{dre_teste_listagem_com_filtros_01.uuid}"
        },
    ]

    assert listagem == resultado_esperado

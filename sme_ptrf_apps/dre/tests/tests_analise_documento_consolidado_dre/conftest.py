from datetime import date
import pytest
from model_bakery import baker
from ...models import ConsolidadoDRE

pytestmark = pytest.mark.django_db


@pytest.fixture
def analise_documento_consolidado_dre_01(
    analise_consolidado_dre_01,
    documento_adicional_consolidado_dre_01,
    relatorio_consolidado_dre_01,
    ata_parecer_tecnico_consolidado_dre_01,
):
    return baker.make(
        'AnaliseDocumentoConsolidadoDre',
        analise_consolidado_dre=analise_consolidado_dre_01,
        documento_adicional=documento_adicional_consolidado_dre_01,
        relatorio_consolidao_dre=relatorio_consolidado_dre_01,
        ata_parecer_tecnico=ata_parecer_tecnico_consolidado_dre_01,
    )

@pytest.fixture
def analise_consolidado_dre_01(consolidado_dre_teste_model_comentario_analise_consolidado_dre):
    return baker.make(
        'AnaliseConsolidadoDre',
        consolidado_dre=consolidado_dre_teste_model_comentario_analise_consolidado_dre,
    )

@pytest.fixture
def documento_adicional_consolidado_dre_01():
    return baker.make(
        'DocumentoAdicional',
    )

@pytest.fixture
def relatorio_consolidado_dre_01():
    return baker.make(
        'RelatorioConsolidadoDRE',
    )

@pytest.fixture
def ata_parecer_tecnico_consolidado_dre_01():
    return baker.make(
        'AtaParecerTecnico',
    )

@pytest.fixture
def dre_teste_model_comentario_analise_consolidado_dre():
    return baker.make(
        'Unidade',
        codigo_eol='108500',
        tipo_unidade='DRE',
        nome='Dre Teste Model Consolidado Dre',
        sigla='A'
    )


@pytest.fixture
def periodo_anterior_teste_model_comentario_analise_consolidado_dre():
    return baker.make(
        'Periodo',
        referencia='2021.2',
        data_inicio_realizacao_despesas=date(2021, 6, 16),
        data_fim_realizacao_despesas=date(2021, 12, 31),
    )


@pytest.fixture
def periodo_teste_model_comentario_analise_consolidado_dre(periodo_anterior_teste_model_comentario_analise_consolidado_dre):
    return baker.make(
        'Periodo',
        referencia='2022.1',
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 12, 31),
        periodo_anterior=periodo_anterior_teste_model_comentario_analise_consolidado_dre,
    )


@pytest.fixture
def consolidado_dre_teste_model_comentario_analise_consolidado_dre(periodo_teste_model_comentario_analise_consolidado_dre, dre_teste_model_comentario_analise_consolidado_dre):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_model_comentario_analise_consolidado_dre,
        periodo=periodo_teste_model_comentario_analise_consolidado_dre,
        status=ConsolidadoDRE.STATUS_SME_EM_ANALISE
    )

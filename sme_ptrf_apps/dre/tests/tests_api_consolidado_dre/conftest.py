from datetime import date
import pytest
from model_bakery import baker
from freezegun import freeze_time
from django.core.files.uploadedfile import SimpleUploadedFile

from ...models import ConsolidadoDRE

pytestmark = pytest.mark.django_db


@pytest.fixture
def dre_teste_api_consolidado_dre():
    return baker.make(
        'Unidade',
        codigo_eol='108500',
        tipo_unidade='DRE',
        nome='Dre Teste Model Consolidado Dre',
        sigla='A'
    )

@pytest.fixture
def periodo_anterior_teste_api_consolidado_dre():
    return baker.make(
        'Periodo',
        referencia='2021.2',
        data_inicio_realizacao_despesas=date(2021, 6, 16),
        data_fim_realizacao_despesas=date(2021, 12, 31),
    )


@pytest.fixture
def periodo_teste_api_consolidado_dre(periodo_anterior_teste_api_consolidado_dre):
    return baker.make(
        'Periodo',
        referencia='2022.1',
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 12, 31),
        periodo_anterior=periodo_anterior_teste_api_consolidado_dre,
    )


@pytest.fixture
def consolidado_dre_teste_api_consolidado_dre(periodo_teste_api_consolidado_dre, dre_teste_api_consolidado_dre):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_api_consolidado_dre,
        periodo=periodo_teste_api_consolidado_dre,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS
    )


@pytest.fixture
def tipo_conta_cheque_teste_api(tipo_conta):
    return tipo_conta

@pytest.fixture
def ano_analise_regularidade_2022_teste_api():
    return baker.make('AnoAnaliseRegularidade', ano=2022)


@pytest.fixture
@freeze_time('2020-10-27 13:59:00')
def arquivo_gerado_em_2020_10_27_13_59_00_teste_api():
    return SimpleUploadedFile(f'arquivo.txt', bytes(f'CONTEUDO TESTE TESTE TESTE', encoding="utf-8"))



@pytest.fixture
@freeze_time('2020-10-27 13:59:00')
def relatorio_dre_consolidado_gerado_final_teste_api(dre_teste_api_consolidado_dre, periodo_teste_api_consolidado_dre, tipo_conta_cheque_teste_api, consolidado_dre_teste_api_consolidado_dre, arquivo_gerado_em_2020_10_27_13_59_00_teste_api):
    return baker.make(
        'RelatorioConsolidadoDre',
        dre=dre_teste_api_consolidado_dre,
        tipo_conta=tipo_conta_cheque_teste_api,
        periodo=periodo_teste_api_consolidado_dre,
        arquivo=arquivo_gerado_em_2020_10_27_13_59_00_teste_api,
        status='GERADO_TOTAL',
        consolidado_dre=consolidado_dre_teste_api_consolidado_dre
    )


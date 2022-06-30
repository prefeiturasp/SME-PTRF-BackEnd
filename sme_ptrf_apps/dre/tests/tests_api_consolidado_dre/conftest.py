from datetime import date
import pytest
from model_bakery import baker
from freezegun import freeze_time
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

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
def relatorio_dre_consolidado_gerado_final_teste_api(
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    tipo_conta_cheque_teste_api,
    consolidado_dre_teste_api_consolidado_dre,
    arquivo_gerado_em_2020_10_27_13_59_00_teste_api
):
    return baker.make(
        'RelatorioConsolidadoDre',
        dre=dre_teste_api_consolidado_dre,
        tipo_conta=tipo_conta_cheque_teste_api,
        periodo=periodo_teste_api_consolidado_dre,
        arquivo=arquivo_gerado_em_2020_10_27_13_59_00_teste_api,
        status='GERADO_TOTAL',
        consolidado_dre=consolidado_dre_teste_api_consolidado_dre
    )


@pytest.fixture
@freeze_time('2022-06-25 13:59:00')
def arquivo_gerado_ata_parecer_tecnico_teste_api():
    return SimpleUploadedFile(f'arquivo.txt', bytes(f'CONTEUDO TESTE TESTE TESTE', encoding="utf-8"))


@pytest.fixture
@freeze_time('2022-06-25 13:59:00')
def ata_parecer_tecnico_teste_api(
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    consolidado_dre_teste_api_consolidado_dre,
    arquivo_gerado_ata_parecer_tecnico_teste_api
):
    return baker.make(
        'AtaParecerTecnico',
        arquivo_pdf=arquivo_gerado_ata_parecer_tecnico_teste_api,
        periodo=periodo_teste_api_consolidado_dre,
        dre=dre_teste_api_consolidado_dre,
        status_geracao_pdf='CONCLUIDO',
        numero_ata=1,
        data_reuniao=date(2022, 6, 25),
        local_reuniao='Escola Teste',
        comentarios='Teste',
        consolidado_dre=consolidado_dre_teste_api_consolidado_dre
    )

@pytest.fixture
@freeze_time('2022-06-25 13:59:00')
def ata_parecer_tecnico_teste_api_preenchida(
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    consolidado_dre_teste_api_consolidado_dre,
    arquivo_gerado_ata_parecer_tecnico_teste_api
):
    return baker.make(
        'AtaParecerTecnico',
        arquivo_pdf=arquivo_gerado_ata_parecer_tecnico_teste_api,
        periodo=periodo_teste_api_consolidado_dre,
        dre=dre_teste_api_consolidado_dre,
        status_geracao_pdf='CONCLUIDO',
        numero_ata=1,
        data_reuniao=date(2022, 6, 25),
        preenchida_em=date(2022, 6, 25),
        local_reuniao='Escola Teste',
        comentarios='Teste',
        consolidado_dre=consolidado_dre_teste_api_consolidado_dre
    )

@pytest.fixture
def visao_dre_teste_api():
    return baker.make('Visao', nome='DRE')


@pytest.fixture
def usuario_dre_teste_api(
    dre_teste_api_consolidado_dre,
    visao_dre_teste_api,
):
    senha = 'Sgp0418'
    login = '8989877'
    email = 'teste.api@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(dre_teste_api_consolidado_dre)
    user.visoes.add(visao_dre_teste_api)
    user.save()
    return user

@pytest.fixture
@freeze_time('2022-06-25 13:59:00')
def arquivo_gerado_lauda_teste_api():
    return SimpleUploadedFile(f'arquivo.txt', bytes(f'CONTEUDO TESTE TESTE TESTE', encoding="utf-8"))


@pytest.fixture
@freeze_time('2022-06-25 13:59:00')
def lauda_teste_api(
    arquivo_gerado_lauda_teste_api,
    consolidado_dre_teste_api_consolidado_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    tipo_conta_cheque_teste_api,
    usuario_dre_teste_api

):
    return baker.make(
        'Lauda',
        arquivo_lauda_txt=arquivo_gerado_lauda_teste_api,
        consolidado_dre=consolidado_dre_teste_api_consolidado_dre,
        dre=dre_teste_api_consolidado_dre,
        periodo=periodo_teste_api_consolidado_dre,
        tipo_conta=tipo_conta_cheque_teste_api,
        usuario=usuario_dre_teste_api,
        status='GERADA_TOTAL',
    )


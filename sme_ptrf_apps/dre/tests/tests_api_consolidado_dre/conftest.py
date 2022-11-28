from datetime import date
import pytest
from model_bakery import baker
from freezegun import freeze_time
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from ...models import ConsolidadoDRE

pytestmark = pytest.mark.django_db


@pytest.fixture
def unidade_teste_api_consolidado_dre_01(dre_teste_api_consolidado_dre):
    return baker.make(
        'Unidade',
        criado_em=date(2021, 6, 16),
        nome='Escola Teste',
        tipo_unidade='CEU',
        codigo_eol='123456',
        dre=dre_teste_api_consolidado_dre,
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
        dre_designacao_ano='2022',
    )

@pytest.fixture
def unidade_teste_api_consolidado_dre_02(dre_teste_api_consolidado_dre):
    return baker.make(
        'Unidade',
        criado_em=date(2021, 6, 16),
        nome='Escola Teste 02',
        tipo_unidade='CEU',
        codigo_eol='123457',
        dre=dre_teste_api_consolidado_dre,
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
        dre_designacao_ano='2022',
    )

@pytest.fixture
def associacao_teste_api_consolidado_dre_01(unidade_teste_api_consolidado_dre_01, periodo_teste_api_consolidado_dre):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='23.809.310/0001-57',
        unidade=unidade_teste_api_consolidado_dre_01,
        periodo_inicial=periodo_teste_api_consolidado_dre,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456'
    )

@pytest.fixture
def associacao_teste_api_consolidado_dre_02(unidade_teste_api_consolidado_dre_02, periodo_teste_api_consolidado_dre):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='67.462.804/0001-83',
        unidade=unidade_teste_api_consolidado_dre_02,
        periodo_inicial=periodo_teste_api_consolidado_dre,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456'
    )

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
def ata_parecer_tecnico_consolidado_dre_01():
    return baker.make(
        'AtaParecerTecnico',
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
def analise_consolidado_dre_test_api_ja_existente():
    return baker.make(
        'AnaliseConsolidadoDre',
        data_devolucao=date.today(),
        data_limite=date.today(),
        data_retorno_analise=date.today(),
        relatorio_acertos_versao=('FINAL', 'final'),
        relatorio_acertos_status='CONCLUIDO',
        relatorio_acertos_gerado_em=date.today(),
    )


@pytest.fixture
def consolidado_dre_teste_api_consolidado_dre_com_analise_atual(periodo_teste_api_consolidado_dre, dre_teste_api_consolidado_dre, analise_consolidado_dre_test_api_ja_existente):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_api_consolidado_dre,
        periodo=periodo_teste_api_consolidado_dre,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS,
        analise_atual=analise_consolidado_dre_test_api_ja_existente
    )


@pytest.fixture
def analise_documento_consolidado_dre_01(
    analise_consolidado_dre_test_api_ja_existente,
    documento_adicional_consolidado_dre_01,
    relatorio_consolidado_dre_01,
    ata_parecer_tecnico_consolidado_dre_01,
):
    return baker.make(
        'AnaliseDocumentoConsolidadoDre',
        analise_consolidado_dre=analise_consolidado_dre_test_api_ja_existente,
        documento_adicional=documento_adicional_consolidado_dre_01,
        relatorio_consolidao_dre=relatorio_consolidado_dre_01,
        ata_parecer_tecnico=ata_parecer_tecnico_consolidado_dre_01,
    )


@pytest.fixture
def analise_documento_consolidado_dre_02(
    analise_consolidado_dre_test_api_ja_existente,
    documento_adicional_consolidado_dre_01,
    relatorio_consolidado_dre_01,
    ata_parecer_tecnico_consolidado_dre_01,
):
    return baker.make(
        'AnaliseDocumentoConsolidadoDre',
        analise_consolidado_dre=analise_consolidado_dre_test_api_ja_existente,
        documento_adicional=documento_adicional_consolidado_dre_01,
        relatorio_consolidao_dre=relatorio_consolidado_dre_01,
        ata_parecer_tecnico=ata_parecer_tecnico_consolidado_dre_01,
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
def comentario_analise_consolidado_dre_01(consolidado_dre_teste_api_consolidado_dre_com_analise_atual):
    return baker.make(
        'ComentarioAnaliseConsolidadoDRE',
        consolidado_dre=consolidado_dre_teste_api_consolidado_dre_com_analise_atual,
        ordem=1,
        comentario='Este é um comentário de analise de consolidadodo DRE',
        notificado=False,
        notificado_em=None,
    )


@pytest.fixture
def comentario_analise_consolidado_dre_02(consolidado_dre_teste_api_consolidado_dre_com_analise_atual):
    return baker.make(
        'ComentarioAnaliseConsolidadoDRE',
        consolidado_dre=consolidado_dre_teste_api_consolidado_dre_com_analise_atual,
        ordem=2,
        comentario='Este é outro comentário de analise de consolidadodo DRE',
        notificado=False,
        notificado_em=None,
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
        consolidado_dre=consolidado_dre_teste_api_consolidado_dre,
        sequencia_de_publicacao=1
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
        consolidado_dre=consolidado_dre_teste_api_consolidado_dre,
        sequencia_de_publicacao=1
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


from datetime import date
import pytest
from model_bakery import baker
from ...models import ConsolidadoDRE
from django.contrib.auth.models import Permission
from sme_ptrf_apps.users.models import Grupo
from freezegun import freeze_time
from django.core.files.uploadedfile import SimpleUploadedFile

pytestmark = pytest.mark.django_db


@pytest.fixture
def permissoes_sme():
    permissoes = [
        Permission.objects.filter(codename='sme_leitura').first(),
        Permission.objects.filter(codename='sme_gravacao').first()
    ]

    return permissoes


@pytest.fixture
def grupo_sme(permissoes_sme):
    g = Grupo.objects.create(name="sme")
    g.permissions.add(*permissoes_sme)
    return g


@pytest.fixture
def usuario_permissao_sme(unidade, grupo_sme):
    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '1235678'
    email = 'usuario.sme@gmail.com'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_sme)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_sme_teste_analise_documento_consolidado_dre(client, usuario_permissao_sme):
    from unittest.mock import patch
    from rest_framework.test import APIClient
    api_client = APIClient()
    with patch('sme_ptrf_apps.users.api.views.login.AutenticacaoService.autentica') as mock_post:
        data = {
            "nome": "Usuario SME",
            "cpf": "12345678910",
            "email": "usuario.sme@gmail.com",
            "login": "1235678"
        }
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = data
        resp = api_client.post('/api/login',
                               {'login': usuario_permissao_sme.username, 'senha': usuario_permissao_sme.password},
                               format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client


@pytest.fixture
def permissoes_ver_relatorio_consolidado_dre():
    permissoes = [
        Permission.objects.filter(codename='dre_leitura').first(),
        Permission.objects.filter(codename='dre_gravacao').first()
    ]

    return permissoes


@pytest.fixture
def grupo_ver_relatorio_consolidado_dre(permissoes_ver_relatorio_consolidado_dre):
    g = Grupo.objects.create(name="grupo_view_relatorio_consolidado_dre")
    g.permissions.add(*permissoes_ver_relatorio_consolidado_dre)
    return g


@pytest.fixture
def usuario_permissao_ver_relatorio_consolidado(
    unidade,
    grupo_ver_relatorio_consolidado_dre):
    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_ver_relatorio_consolidado_dre)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_relatorio_consolidado(client, usuario_permissao_ver_relatorio_consolidado):
    from unittest.mock import patch

    from rest_framework.test import APIClient
    api_client = APIClient()
    with patch('sme_ptrf_apps.users.api.views.login.AutenticacaoService.autentica') as mock_post:
        data = {
            "nome": "LUCIA HELENA",
            "cpf": "62085077072",
            "email": "luh@gmail.com",
            "login": "7210418"
        }
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = data
        resp = api_client.post('/api/login', {'login': usuario_permissao_ver_relatorio_consolidado.username,
                                              'senha': usuario_permissao_ver_relatorio_consolidado.password},
                               format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client


@pytest.fixture
def analise_documento_consolidado_dre_gravar_acerto(
    analise_consolidado_dre_01,
    documento_adicional_consolidado_dre_01,
    relatorio_consolidado_dre_01,
    ata_parecer_tecnico_consolidado_dre_01,
):
    return baker.make(
        'AnaliseDocumentoConsolidadoDre',
        analise_consolidado_dre=analise_consolidado_dre_01,
        documento_adicional=None,
        relatorio_consolidao_dre=relatorio_consolidado_dre_01,
        ata_parecer_tecnico=None,
        detalhamento="",
        resultado="CORRETO",
    )


@pytest.fixture
def analise_documento_consolidado_dre_marcar_como_correto_analise_existente(
    analise_consolidado_dre_01,
    documento_adicional_consolidado_dre_01,
    relatorio_consolidado_dre_01,
    ata_parecer_tecnico_consolidado_dre_01,
):
    return baker.make(
        'AnaliseDocumentoConsolidadoDre',
        analise_consolidado_dre=analise_consolidado_dre_01,
        documento_adicional=None,
        relatorio_consolidao_dre=relatorio_consolidado_dre_01,
        ata_parecer_tecnico=None,
        detalhamento="Este é o novo detalhamento XXXXXXXXXXXx",
        resultado="AJUSTE",
    )


@pytest.fixture
def analise_documento_consolidado_dre_03(
    analise_consolidado_dre_01,
    documento_adicional_consolidado_dre_01,
    relatorio_consolidado_dre_01,
    ata_parecer_tecnico_consolidado_dre_01,
):
    return baker.make(
        'AnaliseDocumentoConsolidadoDre',
        analise_consolidado_dre=analise_consolidado_dre_01,
        documento_adicional=None,
        relatorio_consolidao_dre=relatorio_consolidado_dre_01,
        ata_parecer_tecnico=None,
        detalhamento="Este é o detalhamento da analise de documento 03",
    )


@pytest.fixture
def analise_documento_consolidado_dre_02(
    analise_consolidado_dre_01,
    documento_adicional_consolidado_dre_01,
    relatorio_consolidado_dre_01,
    ata_parecer_tecnico_consolidado_dre_01,
):
    return baker.make(
        'AnaliseDocumentoConsolidadoDre',
        analise_consolidado_dre=analise_consolidado_dre_01,
        documento_adicional=documento_adicional_consolidado_dre_01,
        relatorio_consolidao_dre=None,
        ata_parecer_tecnico=None,
    )


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
        documento_adicional=None,
        relatorio_consolidao_dre=relatorio_consolidado_dre_01,
        ata_parecer_tecnico=None,
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
def periodo_teste_model_comentario_analise_consolidado_dre(
    periodo_anterior_teste_model_comentario_analise_consolidado_dre):
    return baker.make(
        'Periodo',
        referencia='2022.1',
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 12, 31),
        periodo_anterior=periodo_anterior_teste_model_comentario_analise_consolidado_dre,
    )


@pytest.fixture
def consolidado_dre_teste_model_comentario_analise_consolidado_dre(
    periodo_teste_model_comentario_analise_consolidado_dre, dre_teste_model_comentario_analise_consolidado_dre):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_model_comentario_analise_consolidado_dre,
        periodo=periodo_teste_model_comentario_analise_consolidado_dre,
        status=ConsolidadoDRE.STATUS_SME_EM_ANALISE
    )


# ############# Teste Download Documentos

@pytest.fixture
def analise_documento_consolidado_dre_teste_download_documentos(
    relatorio_dre_consolidado_gerado_final_teste_api,
    analise_consolidado_dre_01
):
    return baker.make(
        'AnaliseDocumentoConsolidadoDre',
        analise_consolidado_dre=analise_consolidado_dre_01,
        documento_adicional=None,
        relatorio_consolidao_dre=relatorio_dre_consolidado_gerado_final_teste_api,
        ata_parecer_tecnico=None,
    )

@pytest.fixture
def dre_teste_analise_documento_consolidado_dre_teste_download_documentos():
    return baker.make(
        'Unidade',
        codigo_eol='108444',
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
def consolidado_dre_teste_api_consolidado_dre(periodo_teste_api_consolidado_dre, dre_teste_analise_documento_consolidado_dre_teste_download_documentos):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_analise_documento_consolidado_dre_teste_download_documentos,
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
    dre_teste_analise_documento_consolidado_dre_teste_download_documentos,
    periodo_teste_api_consolidado_dre,
    tipo_conta_cheque_teste_api,
    consolidado_dre_teste_api_consolidado_dre,
    arquivo_gerado_em_2020_10_27_13_59_00_teste_api
):
    return baker.make(
        'RelatorioConsolidadoDre',
        dre=dre_teste_analise_documento_consolidado_dre_teste_download_documentos,
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

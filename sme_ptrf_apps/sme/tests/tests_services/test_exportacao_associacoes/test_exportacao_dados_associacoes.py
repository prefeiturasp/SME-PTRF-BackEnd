from datetime import datetime, timedelta, date
from tempfile import NamedTemporaryFile
import pytest
from unittest.mock import patch

from model_bakery import baker

from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.sme.services.exporta_associacoes_service import ExportaAssociacoesService
from sme_ptrf_apps.core.models.associacao import Associacao

pytestmark = pytest.mark.django_db


@pytest.fixture
def ambiente():
    return baker.make(
        'Ambiente',
        prefixo='dev-sig-escola',
        nome='Ambiente de desenvolvimento',
    )


def test_cabecalho():
    dados = ExportaAssociacoesService()

    cabecalho = [cabecalho[0] for cabecalho in dados.cabecalho]

    resultado_esperado = [
        ('Recurso'),
        ('Código EOL'),
        ('Nome Unidade'),
        ('Nome Associação'),
        ('DRE'),
        ('CNPJ'),
        ('ID do Período Inicial'),
        ('Referência do Período inicial'),
        ('Data de encerramento'),
        ('CCM'),
        ('E-mail'),
        ('Número do processo de regularidade'),
        ('Status do presidente'),
        ('Cargo substituto do presidente'),
        ('Data e hora de criação'),
        ('Data e hora da última atualização'),
    ]

    assert cabecalho == resultado_esperado


def test_get_texto_filtro_aplicado_datas_inicio_e_fim():
    service = ExportaAssociacoesService(data_inicio="2024-12-01", data_final="2024-12-31")
    result = service.get_texto_filtro_aplicado()

    assert result == "Filtro aplicado: 01/12/2024 a 31/12/2024 (data de criação do registro)"


def test_get_texto_filtro_aplicado_data_inicio():
    service = ExportaAssociacoesService(data_inicio="2024-12-01")
    result = service.get_texto_filtro_aplicado()

    assert result == "Filtro aplicado: A partir de 01/12/2024 (data de criação do registro)"


def test_get_texto_filtro_aplicado_data_final():
    service = ExportaAssociacoesService(data_final="2024-12-31")
    result = service.get_texto_filtro_aplicado()

    assert result == "Filtro aplicado: Até 31/12/2024 (data de criação do registro)"


def test_filtra_range_data_inicial_e_final(associacao_factory):
    associacao_factory.create()
    associacao_factory.create()
    queryset = Associacao.objects.all().order_by('id')
    data_inicio = datetime.now().strftime("%Y-%m-%d")
    data_final = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    service = ExportaAssociacoesService(queryset=queryset, data_inicio=data_inicio, data_final=data_final)
    result = service.filtra_range_data("criado_em")
    new_queryset = Associacao.objects.all().order_by('id')

    assert result.count() == new_queryset.count()
    assert result[0].nome == new_queryset[0].nome


def test_monta_dados(associacao_factory_com_periodo_inicial):
    associacao_factory_com_periodo_inicial.create()
    associacao_factory_com_periodo_inicial.create(data_de_encerramento=date(2024, 10, 31))
    queryset = Associacao.objects.all().order_by('id')
    service = ExportaAssociacoesService(queryset=queryset)
    result = service.monta_dados()

    assert len(result) == 2
    assert result[0][0] == queryset[0].periodo_inicial.recurso.nome
    assert result[0][1] == queryset[0].unidade.codigo_eol
    assert result[0][2] == queryset[0].unidade.nome
    assert result[0][6] == str(queryset[0].periodo_inicial.id)
    assert result[1][9] == queryset[1].ccm
    assert result[1][10] == queryset[1].email


def test_rodape(ambiente, usuario_para_teste):
    service = ExportaAssociacoesService(ambiente=ambiente, user=usuario_para_teste)
    result = service.texto_rodape()

    data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    resultado_esperado = f"Arquivo solicitado via {ambiente.prefixo} pelo usuário {usuario_para_teste} em {data_atual}"

    assert result == resultado_esperado


def test_cria_registro_central_download(usuario_para_teste):
    with NamedTemporaryFile(
        mode="r+",
        newline='',
        encoding='utf-8',
        prefix='associacoes',
        suffix='.csv'
    ) as file:
        file.write("testando central de download")

        service = ExportaAssociacoesService(
            nome_arquivo='associacoes.csv',
            user=usuario_para_teste.username
        )
        service.cria_registro_central_download()
        service.envia_arquivo_central_download(file)
        objeto_arquivo_download = service.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_CONCLUIDO
    assert objeto_arquivo_download.identificador == 'associacoes.csv'
    assert ArquivoDownload.objects.count() == 1


@patch.object(ArquivoDownload, "save")
def test_envia_arquivo_central_download_exception(mock_save_arquivo_download, usuario_para_teste):
    with NamedTemporaryFile(
        mode="r+",
        newline='',
        encoding='utf-8',
        prefix='associacoes',
        suffix='.csv'
    ) as file:
        file.write("testando central de download")

        service = ExportaAssociacoesService(
            nome_arquivo='associacoes.csv',
            user=usuario_para_teste.username
        )
        service.cria_registro_central_download()
        mock_save_arquivo_download.side_effect = Exception("Erro")
        with pytest.raises(Exception):
            service.envia_arquivo_central_download(file)

    assert service.objeto_arquivo_download.status == ArquivoDownload.STATUS_ERRO
    assert service.objeto_arquivo_download.msg_erro == 'Erro'


def test_exporta_associacoes_csv(associacao_factory, usuario_para_teste):
    associacao_factory.create()
    queryset = Associacao.objects.all().order_by('id')
    service = ExportaAssociacoesService(
        queryset=queryset,
        nome_arquivo='associacoes.csv',
        user=usuario_para_teste.username)
    service.cria_registro_central_download()
    service.exporta_associacoes_csv()
    assert service.objeto_arquivo_download.status == ArquivoDownload.STATUS_CONCLUIDO

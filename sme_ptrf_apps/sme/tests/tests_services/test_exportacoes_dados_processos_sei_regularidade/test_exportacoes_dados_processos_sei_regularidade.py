import datetime
from tempfile import NamedTemporaryFile
import pytest
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload

from sme_ptrf_apps.sme.services.exporta_dados_processos_sei_regularidade_service import ExportaDadosProcessosSeiRegularidadeService
from sme_ptrf_apps.core.models.associacao import Associacao

pytestmark = pytest.mark.django_db


def test_cabecalho():
    dados = ExportaDadosProcessosSeiRegularidadeService()

    cabecalho = [cabecalho[0] for cabecalho in dados.cabecalho]

    resultado_esperado = [
        "Código EOL",
        "Nome Unidade",
        "Nome Associação",
        "CNPj da Associação",
        "DRE",
        "Número do processo SEI de regularidade",
    ]

    assert cabecalho == resultado_esperado


def test_dados_processos_sei_regularidade_esperados_csv(associacao_factory):
    associacao_factory.create()
    associacao_factory.create()

    queryset = Associacao.objects.all()

    dados = ExportaDadosProcessosSeiRegularidadeService(queryset=queryset).monta_dados()

    resultado_esperado = [
        [
            queryset[0].unidade.codigo_eol,
            queryset[0].unidade.nome,
            queryset[0].nome,
            queryset[0].cnpj,
            queryset[0].unidade.dre.nome,
            queryset[0].processo_regularidade,
        ],
        [
            queryset[1].unidade.codigo_eol,
            queryset[1].unidade.nome,
            queryset[1].nome,
            queryset[1].cnpj,
            queryset[1].unidade.dre.nome,
            queryset[1].processo_regularidade,
        ]
    ]

    assert resultado_esperado == dados


def test_rodape(ambiente, usuario_para_teste):
    queryset = Associacao.objects.all()

    dados = ExportaDadosProcessosSeiRegularidadeService(
        queryset=queryset,
        user=usuario_para_teste
    ).texto_info_arquivo_gerado()

    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    resultado_esperado = f"Arquivo solicitado via {ambiente.prefixo} pelo usuário {usuario_para_teste} em {data_atual}"

    assert dados == resultado_esperado


def test_cria_registro_central_download(usuario_para_teste):
    exportacao = ExportaDadosProcessosSeiRegularidadeService(
        nome_arquivo='processo_sei_regularidade.csv',
        user=usuario_para_teste.username
    )

    exportacao.cria_registro_central_download()
    objeto_arquivo_download = exportacao.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_EM_PROCESSAMENTO
    assert objeto_arquivo_download.identificador == 'processo_sei_regularidade.csv'
    assert ArquivoDownload.objects.count() == 1


def test_envia_arquivo_central_download(usuario_para_teste):
    with NamedTemporaryFile(
        mode="r+",
        newline='',
        encoding='utf-8',
        prefix='processo_sei_regularidade',
        suffix='.csv'
    ) as file:
        file.write("testando central de download")

        exportacao = ExportaDadosProcessosSeiRegularidadeService(
            nome_arquivo='processo_sei_regularidade.csv',
            user=usuario_para_teste.username
        )
        exportacao.cria_registro_central_download()
        exportacao.envia_arquivo_central_download(file)
        objeto_arquivo_download = exportacao.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_CONCLUIDO
    assert objeto_arquivo_download.identificador == 'processo_sei_regularidade.csv'
    assert ArquivoDownload.objects.count() == 1

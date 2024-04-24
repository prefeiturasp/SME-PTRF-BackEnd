import datetime
from tempfile import NamedTemporaryFile
import pytest
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload

from sme_ptrf_apps.sme.services.exporta_dados_processos_sei_prestacoao_contas_service import ExportacaoDadosProcessosSEIPrestacaoContasService
from sme_ptrf_apps.core.models.proccessos_associacao import ProcessoAssociacao

pytestmark = pytest.mark.django_db


def test_cabecalho():
    dados = ExportacaoDadosProcessosSEIPrestacaoContasService()

    cabecalho = [cabecalho[0] for cabecalho in dados.cabecalho]

    resultado_esperado = [
        "Código EOL",
        "Nome Unidade",
        "Nome Associação",
        "CNPj da Associação",
        "DRE",
        "Número do processo SEI",
        "Ano",
        "Períodos"
    ]

    assert cabecalho == resultado_esperado


def test_dados_processos_sei_esperados_csv(processo_associacao_factory):
    processo_associacao_factory.create()
    processo_associacao_factory.create()

    queryset = ProcessoAssociacao.objects.all()

    dados = ExportacaoDadosProcessosSEIPrestacaoContasService(queryset=queryset).monta_dados()

    periodos_strings_1 = []
    periodos_strings_2 = []

    for periodo in queryset[0].periodos.all():
        periodos_strings_1.append(periodo.referencia)

    periodos_concat_1 = ', '.join(periodos_strings_1)

    for periodo in queryset[1].periodos.all():
        periodos_strings_2.append(periodo.referencia)

    periodos_concat_2 = ', '.join(periodos_strings_2)

    resultado_esperado = [
        [
            queryset[0].associacao.unidade.codigo_eol,
            queryset[0].associacao.unidade.nome,
            queryset[0].associacao.nome,
            queryset[0].associacao.cnpj,
            queryset[0].associacao.unidade.dre.nome,
            queryset[0].numero_processo,
            queryset[0].ano,
            periodos_concat_1
        ],
        [
            queryset[1].associacao.unidade.codigo_eol,
            queryset[1].associacao.unidade.nome,
            queryset[1].associacao.nome,
            queryset[1].associacao.cnpj,
            queryset[1].associacao.unidade.dre.nome,
            queryset[1].numero_processo,
            queryset[1].ano,
            periodos_concat_2
        ]
    ]

    assert resultado_esperado == dados


def test_rodape(ambiente, usuario_para_teste):
    queryset = ProcessoAssociacao.objects.all()

    dados = ExportacaoDadosProcessosSEIPrestacaoContasService(
        queryset=queryset,
        user=usuario_para_teste
    ).texto_info_arquivo_gerado()

    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    resultado_esperado = f"Arquivo gerado via {ambiente.prefixo} pelo usuário {usuario_para_teste} em {data_atual}"

    assert dados == resultado_esperado


def test_cria_registro_central_download(usuario_para_teste):
    exportacao = ExportacaoDadosProcessosSEIPrestacaoContasService(
        nome_arquivo='processo_sei_prestacao_contas.csv',
        user=usuario_para_teste.username
    )

    exportacao.cria_registro_central_download()
    objeto_arquivo_download = exportacao.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_EM_PROCESSAMENTO
    assert objeto_arquivo_download.identificador == 'processo_sei_prestacao_contas.csv'
    assert ArquivoDownload.objects.count() == 1


def test_envia_arquivo_central_download(usuario_para_teste):
    with NamedTemporaryFile(
        mode="r+",
        newline='',
        encoding='utf-8',
        prefix='processo_sei_prestacao_contas',
        suffix='.csv'
    ) as file:
        file.write("testando central de download")

        exportacao = ExportacaoDadosProcessosSEIPrestacaoContasService(
            nome_arquivo='processo_sei_prestacao_contas.csv',
            user=usuario_para_teste.username
        )
        exportacao.cria_registro_central_download()
        exportacao.envia_arquivo_central_download(file)
        objeto_arquivo_download = exportacao.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_CONCLUIDO
    assert objeto_arquivo_download.identificador == 'processo_sei_prestacao_contas.csv'
    assert ArquivoDownload.objects.count() == 1

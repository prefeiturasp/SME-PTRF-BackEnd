import datetime
import pytest

from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.sme.services.exporta_dados_creditos_service import ExportacoesDadosCreditosService
from tempfile import NamedTemporaryFile


DATA_FILTRADAS = [
        (datetime.date(2020, 2, 25), datetime.date(2020, 4, 26), 2),
        (None, datetime.date(2020, 4, 26), 2),
        (datetime.date(2050, 10, 28), None, 0)
    ]


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('data_filtrada', DATA_FILTRADAS)
def test_exporta_creditos_principal(receita_queryset, usuario_para_teste, data_filtrada):
    ExportacoesDadosCreditosService(
        nome_arquivo='creditos_principal.csv',
        queryset=receita_queryset,
        data_inicio=data_filtrada[0],
        data_fim=data_filtrada[1],
        user=usuario_para_teste.username,
    ).exporta_creditos_principal()

    assert ArquivoDownload.objects.first().arquivo.name == 'creditos_principal.csv'
    assert ArquivoDownload.objects.count() == 1


@pytest.mark.parametrize('data_filtrada', DATA_FILTRADAS)
def test_exporta_creditos_motivos_estorno(receita_queryset, usuario_para_teste, data_filtrada):
    ExportacoesDadosCreditosService(
        nome_arquivo='creditos_motivos_estorno.csv',
        queryset=receita_queryset,
        data_inicio=data_filtrada[0],
        data_fim=data_filtrada[1],
        user=usuario_para_teste.username,
    ).exporta_creditos_motivos_estorno()

    assert ArquivoDownload.objects.first().arquivo.name == 'creditos_motivos_estorno.csv'
    assert ArquivoDownload.objects.count() == 1


def test_exporta_credito_csv(receita_queryset, usuario_para_teste):
    service = ExportacoesDadosCreditosService(
        nome_arquivo='creditos_motivos_estorno.csv',
        queryset=receita_queryset,
        data_inicio=None,
        data_fim=None,
        user=usuario_para_teste.username,
    )
    service.cabecalho = [
        ('ID do crédito (estorno)', ('id', 'motivos_estorno')),
        ('ID do motivo de estorno', 'id'),
        ('Descrição do motivo de estorno', 'motivo')
    ],
    service.cabecalho = service.cabecalho[0]
    service.exporta_credito_csv()

    assert ArquivoDownload.objects.first().arquivo.name == 'creditos_motivos_estorno.csv'
    assert ArquivoDownload.objects.count() == 1


def test_envia_arquivo_central_download(usuario_para_teste):
    with NamedTemporaryFile(
        mode="r+",
        newline='',
        encoding='utf-8',
        prefix='teste_arquivo',
        suffix='.txt'
    ) as file:
        file.write("testando central de download")
    ExportacoesDadosCreditosService(
        nome_arquivo='usuario_para_test.txt',
        user=usuario_para_teste.username
    ).envia_arquivo_central_download(file)

    assert ArquivoDownload.objects.count() == 1

@pytest.mark.parametrize('data_inicio, data_fim, len_queryset', DATA_FILTRADAS)
def test_filtra_range_data(receita_queryset, data_inicio, data_fim, len_queryset):
    queryset_filtrado = ExportacoesDadosCreditosService(
        queryset=receita_queryset,
        data_inicio=data_inicio,
        data_fim=data_fim
    ).filtra_range_data('data')

    assert queryset_filtrado.count() == len_queryset

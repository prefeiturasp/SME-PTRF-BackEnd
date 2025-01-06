from datetime import datetime, time, date
import pytest
import logging

from tempfile import NamedTemporaryFile
from django.utils.timezone import make_aware
from unittest.mock import MagicMock, patch
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.sme.services.exporta_dados_unidades_service import (
    ExportacoesDadosUnidadesService
)
logger = logging.getLogger(__name__)

pytestmark = pytest.mark.django_db

DATAS = (date(2020, 3, 26), date(2024, 4, 26))


def test_get_ambiente(export_service):
    with patch("sme_ptrf_apps.core.models.ambiente.Ambiente.objects.first") as mock_ambiente:
        mock_ambiente.return_value = MagicMock(prefixo="PROD")
        assert export_service.get_ambiente == "PROD"
        mock_ambiente.return_value = None
        assert export_service.get_ambiente == ""


def test_get_texto_filtro_aplicado(export_service):
    assert export_service.get_texto_filtro_aplicado() == (
        "Filtro aplicado: 01/01/2023 a 31/12/2023 (data de criação do registro)"
    )


def test_filtra_range_data(export_service, mock_query_set):
    export_service.data_inicio = "2023-01-01"
    export_service.data_final = "2023-12-31"

    filtered_queryset = export_service.filtra_range_data("criado_em")

    inicio = datetime.strptime("2023-01-01", "%Y-%m-%d").date()
    final = datetime.strptime("2023-12-31", "%Y-%m-%d").date()

    # utilizar a funcao make_aware do timezone para obter os sminutos e
    # segundos finais por meio do time.max
    final_aware = make_aware(datetime.combine(final, time.max))

    # Verifique se o método filter foi chamado com os argumentos corretos
    mock_query_set.filter.assert_called_with(
        criado_em__gte=inicio,
        criado_em__lte=final_aware,
    )
    assert filtered_queryset == mock_query_set


def test_monta_dados(export_service):
    mock_instance = MagicMock()
    mock_instance.codigo_eol = "1234"
    mock_instance.criado_em = datetime(2023, 1, 1)
    mock_instance.alterado_em = datetime(2023, 1, 2)

    export_service.queryset = [mock_instance]
    with patch("sme_ptrf_apps.sme.services.exporta_dados_unidades_service.Unidade.objects.filter") as mock_filter, \
        patch(
            "sme_ptrf_apps.sme.services.exporta_dados_unidades_service.get_recursive_attr",
            side_effect=lambda obj, attr: getattr(obj, attr, None)):

        mock_filter.return_value.exists.return_value = True
        dados = export_service.monta_dados()
        assert len(dados) == 1
        assert dados[0][0] == "1234"


def test_criar_registro_central_download(export_service):
    with patch("sme_ptrf_apps.sme.services.exporta_dados_unidades_service.gerar_arquivo_download") as mock_gerar_arqv:
        mock_gerar_arqv.return_value = ArquivoDownload(usuario=export_service.user)
        export_service.cria_registro_central_download()
        mock_gerar_arqv.assert_called_once_with(
            export_service.user, export_service.nome_arquivo, export_service.texto_filtro_aplicado
        )


def test_envia_arquivo_central_download(usuario_teste):
    with NamedTemporaryFile(
        mode="r+",
        newline='',
        encoding='utf-8',
        prefix='teste_arquivo_unidades',
        suffix='.csv'
    ) as file:
        file.write("testando central de download")

    service = ExportacoesDadosUnidadesService(
        nome_arquivo='teste_arquivo_unidades',
        user=usuario_teste.username
    )
    service.cria_registro_central_download()
    service.envia_arquivo_central_download(file)

    arquivo = ArquivoDownload.objects.get(identificador='teste_arquivo_unidades')

    assert arquivo is not None
    assert arquivo.arquivo is not None


def test_texto_rodape(export_service):
    export_service.ambiente = "Ambiente de Teste"
    resultado = export_service.texto_rodape()

    assert resultado is not None


@patch('csv.writer')
def test_exporta_unidades_csv(mock_writer):
    nome_arquivo = "exportacao_unidades"
    cabecalho = [[
        'Código EOL', 'Tipo', 'Nome', 'CEP', 'Tipo Logradouro', 'Logradouro',
        'Bairro', 'Número', 'Complemento', 'Telefone', 'E-mail',
        'Código EOL DRE', 'Nome DRE', 'Sigla DRE', 'Nome Diretor Unidade',
        'Data e hora de criação do registro',
        'Data e hora da última atualização do registro', ],
        ["Nome", "Descrição"]]
    service = ExportacoesDadosUnidadesService(nome_arquivo=nome_arquivo, cabecalho=cabecalho)

    mock_write = MagicMock()
    mock_writer.return_value = mock_write

    service.monta_dados = MagicMock(return_value=[["1", "Dado 1"], ["2", "Dado 2"]])
    service.cria_rodape = MagicMock()
    service.envia_arquivo_central_download = MagicMock()

    service.exporta_unidades_csv()

    cabecalho_esperado = [
        'Código EOL', 'Tipo', 'Nome', 'CEP', 'Tipo Logradouro', 'Logradouro',
        'Bairro', 'Número', 'Complemento', 'Telefone', 'E-mail',
        'Código EOL DRE', 'Nome DRE', 'Sigla DRE', 'Nome Diretor Unidade',
        'Data e hora de criação do registro',
        'Data e hora da última atualização do registro']
    mock_write.writerow.assert_any_call(cabecalho_esperado)

    mock_write.writerow.assert_any_call(["1", "Dado 1"])
    mock_write.writerow.assert_any_call(["2", "Dado 2"])

    service.envia_arquivo_central_download.assert_called_once()

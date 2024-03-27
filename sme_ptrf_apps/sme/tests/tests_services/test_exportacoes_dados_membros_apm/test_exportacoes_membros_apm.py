import datetime
from tempfile import NamedTemporaryFile
import pytest
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload

from sme_ptrf_apps.mandatos.models.cargo_composicao import CargoComposicao
from sme_ptrf_apps.mandatos.models.ocupante_cargo import OcupanteCargo
from sme_ptrf_apps.sme.services.exporta_dados_membros_apm_service import ExportacaoDadosMembrosApmService
from sme_ptrf_apps.receitas.models.repasse import Repasse

pytestmark = pytest.mark.django_db


def test_cabecalho():
    dados = ExportacaoDadosMembrosApmService()

    cabecalho = [cabecalho[0] for cabecalho in dados.cabecalho]

    resultado_esperado = [
        "Código EOL",
        "Tipo da unidade",
        "Nome da Unidade",
        "Nome da Associação",
        "CNPJ",
        "DRE",
        "Mandato",
        "Data inicial do mandato",
        "Data final do mandato",
        "Composição data inicial",
        "Composição data final",
        "Cargo",
        "Número de identificação",
        "Representação",
        "Período inicial de ocupação",
        "Período final de ocupação",
    ]

    assert cabecalho == resultado_esperado


def test_dados_repasses_esperados_csv(membros_apm_fixture_mock, ambiente):
    queryset = CargoComposicao.objects.all()
    
    dados = ExportacaoDadosMembrosApmService(queryset=queryset).monta_dados()
    linha_individual = dados[0]
    
    resultado_esperado = [
        queryset[0].composicao.associacao.unidade.codigo_eol,
        queryset[0].composicao.associacao.unidade.tipo_unidade,
        queryset[0].composicao.associacao.unidade.nome,
        queryset[0].composicao.associacao.nome,
        queryset[0].composicao.associacao.cnpj,
        queryset[0].composicao.associacao.unidade.dre.nome,
        queryset[0].composicao.mandato.referencia_mandato,
        '19/07/2023',
        '20/07/2023',
        '01/01/2023',
        '31/12/2025',
        queryset[0].cargo_associacao,
        '907XXXXXX86',
        queryset[0].ocupante_do_cargo.representacao,
        '10/01/2023',
        '10/04/2023',
    ]

    assert resultado_esperado == linha_individual


def test_rodape(membros_apm_fixture_mock, ambiente):
    queryset = Repasse.objects.all()

    dados = ExportacaoDadosMembrosApmService(
        queryset=queryset,
        user="12345"
    ).texto_info_arquivo_gerado()

    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    resultado_esperado = f"Arquivo gerado via {ambiente.prefixo} pelo usuário 12345 em {data_atual}"

    assert dados == resultado_esperado


def test_filtra_range_data_fora_do_range(membros_apm_fixture_mock):
    queryset = Repasse.objects.all()

    data_inicio = datetime.date(2020, 2, 10)
    data_final = datetime.date(2020, 5, 10)

    queryset_filtrado = ExportacaoDadosMembrosApmService(
        queryset=queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == 0


def test_filtra_range_data_dentro_do_range(membros_apm_fixture_mock):
    queryset = Repasse.objects.all()

    data_inicio = datetime.date.today()
    data_final = datetime.date.today()

    queryset_filtrado = ExportacaoDadosMembrosApmService(
        queryset=queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset)


def test_filtra_range_data_com_data_inicio_e_sem_data_final(membros_apm_fixture_mock):
    queryset = Repasse.objects.all()

    data_inicio = datetime.date.today()

    queryset_filtrado = ExportacaoDadosMembrosApmService(
        queryset=queryset,
        data_inicio=data_inicio
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset)


def test_filtra_range_data_sem_data_inicio_e_com_data_final(membros_apm_fixture_mock):
    queryset = Repasse.objects.all()

    data_final = datetime.date.today()

    queryset_filtrado = ExportacaoDadosMembrosApmService(
        queryset=queryset,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset)


def test_filtra_range_data_sem_data_inicio_e_sem_data_final(membros_apm_fixture_mock):
    queryset = Repasse.objects.all()

    queryset_filtrado = ExportacaoDadosMembrosApmService(
        queryset=queryset
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset)


def test_filtros_aplicados_sem_data_inicio_e_sem_data_final(membros_apm_fixture_mock):
    queryset = Repasse.objects.all()

    dados = ExportacaoDadosMembrosApmService(
        queryset=queryset
    ).get_texto_filtro_aplicado()

    resultado_esperado = ""

    assert dados == resultado_esperado


def test_filtros_aplicados_com_data_inicio_e_com_data_final(membros_apm_fixture_mock):
    queryset = Repasse.objects.all()

    data_inicio = datetime.date.today()
    data_final = datetime.date.today()

    dados = ExportacaoDadosMembrosApmService(
        queryset=queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).get_texto_filtro_aplicado()

    resultado_esperado = f"Filtro aplicado: {data_inicio.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')} (data de criação do registro)"

    assert dados == resultado_esperado


def test_filtros_aplicados_com_data_inicio_e_sem_data_final(membros_apm_fixture_mock):
    queryset = Repasse.objects.all()

    data_inicio = datetime.date.today()

    dados = ExportacaoDadosMembrosApmService(
        queryset=queryset,
        data_inicio=data_inicio,
    ).get_texto_filtro_aplicado()

    resultado_esperado = f"Filtro aplicado: A partir de {data_inicio.strftime('%d/%m/%Y')} (data de criação do registro)"

    assert dados == resultado_esperado


def test_filtros_aplicados_sem_data_inicio_e_com_data_final(membros_apm_fixture_mock):
    queryset = Repasse.objects.all()

    data_final = datetime.date.today()

    dados = ExportacaoDadosMembrosApmService(
        queryset=queryset,
        data_final=data_final,
    ).get_texto_filtro_aplicado()

    resultado_esperado = f"Filtro aplicado: Até {data_final.strftime('%d/%m/%Y')} (data de criação do registro)"

    assert dados == resultado_esperado


def test_cria_registro_central_download(usuario_para_teste):
    exportacao_repasses = ExportacaoDadosMembrosApmService(
        nome_arquivo='repasses.csv',
        user=usuario_para_teste.username
    )

    exportacao_repasses.cria_registro_central_download()
    objeto_arquivo_download = exportacao_repasses.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_EM_PROCESSAMENTO
    assert objeto_arquivo_download.identificador == 'repasses.csv'
    assert ArquivoDownload.objects.count() == 1


def test_envia_arquivo_central_download(usuario_para_teste):
    with NamedTemporaryFile(
        mode="r+",
        newline='',
        encoding='utf-8',
        prefix='repasses',
        suffix='.csv'
    ) as file:
        file.write("testando central de download")

        exportacao_repasses = ExportacaoDadosMembrosApmService(
            nome_arquivo='repasses.csv',
            user=usuario_para_teste.username
        )
        exportacao_repasses.cria_registro_central_download()
        exportacao_repasses.envia_arquivo_central_download(file)
        objeto_arquivo_download = exportacao_repasses.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_CONCLUIDO
    assert objeto_arquivo_download.identificador == 'repasses.csv'
    assert ArquivoDownload.objects.count() == 1

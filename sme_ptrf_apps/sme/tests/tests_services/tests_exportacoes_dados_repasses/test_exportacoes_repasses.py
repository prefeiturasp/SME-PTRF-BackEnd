import datetime
from tempfile import NamedTemporaryFile
import pytest
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload

from sme_ptrf_apps.sme.services.exporta_repasses_service import ExportacaoDadosRepassesService
from sme_ptrf_apps.receitas.models.repasse import Repasse

pytestmark = pytest.mark.django_db


def test_cabecalho():
    dados = ExportacaoDadosRepassesService()

    cabecalho = [cabecalho[0] for cabecalho in dados.cabecalho]

    resultado_esperado = [
        'Código EOL',
        'Nome Unidade',
        'Nome Associação',
        'DRE',
        'Período',
        'Nome do tipo de conta',
        'Nome da Ação',
        'Valor custeio',
        'Valor capital',
        'Valor livre aplicação',
        'Realizado custeio?',
        'Realizado capital?',
        'Realizado livre aplicação?',
        'Carga origem',
        'ID da linha da carga origem',
        'Data e hora de criação',
    ]

    assert cabecalho == resultado_esperado


def test_dados_repasses_esperados_csv(repasse_exportacao_csv, ambiente):
    queryset = Repasse.objects.all()

    dados = ExportacaoDadosRepassesService(queryset=queryset).monta_dados()

    linha_individual = dados[0]

    resultado_esperado = [
        repasse_exportacao_csv.associacao.unidade.codigo_eol,
        repasse_exportacao_csv.associacao.unidade.nome,
        repasse_exportacao_csv.associacao.nome,
        repasse_exportacao_csv.associacao.unidade.nome_dre,
        repasse_exportacao_csv.periodo.referencia,
        repasse_exportacao_csv.conta_associacao.tipo_conta.nome,
        repasse_exportacao_csv.acao_associacao.acao.nome,
        "1000,00",
        "1000,00",
        "0,00",
        "Sim",
        "Não",
        "Não",
        None,
        0,
        repasse_exportacao_csv.criado_em.strftime("%d/%m/%Y às %H:%M:%S")

    ]

    assert linha_individual == resultado_esperado


def test_rodape(repasse_exportacao_csv, ambiente):
    queryset = Repasse.objects.all()

    dados = ExportacaoDadosRepassesService(
        queryset=queryset,
        user="12345"
    ).texto_info_arquivo_gerado()

    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    resultado_esperado = f"Arquivo gerado via {ambiente.prefixo} pelo usuário 12345 em {data_atual}"

    assert dados == resultado_esperado


def test_filtra_range_data_fora_do_range(repasse_exportacao_csv):
    queryset = Repasse.objects.all()

    data_inicio = str(datetime.date(2020, 2, 10))
    data_final = str(datetime.date(2020, 5, 10))

    queryset_filtrado = ExportacaoDadosRepassesService(
        queryset=queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == 0


def test_filtra_range_data_dentro_do_range(repasse_exportacao_csv):
    queryset = Repasse.objects.all()

    data_inicio = str(datetime.date.today())
    data_final = str(datetime.date.today())

    queryset_filtrado = ExportacaoDadosRepassesService(
        queryset=queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset)


def test_filtra_range_data_com_data_inicio_e_sem_data_final(repasse_exportacao_csv):
    queryset = Repasse.objects.all()

    data_inicio = str(datetime.date.today())

    queryset_filtrado = ExportacaoDadosRepassesService(
        queryset=queryset,
        data_inicio=data_inicio
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset)


def test_filtra_range_data_sem_data_inicio_e_com_data_final(repasse_exportacao_csv):
    queryset = Repasse.objects.all()

    data_final = str(datetime.date.today())

    queryset_filtrado = ExportacaoDadosRepassesService(
        queryset=queryset,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset)


def test_filtra_range_data_sem_data_inicio_e_sem_data_final(repasse_exportacao_csv):
    queryset = Repasse.objects.all()

    queryset_filtrado = ExportacaoDadosRepassesService(
        queryset=queryset
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset)


def test_filtros_aplicados_sem_data_inicio_e_sem_data_final(repasse_exportacao_csv):
    queryset = Repasse.objects.all()

    dados = ExportacaoDadosRepassesService(
        queryset=queryset
    ).get_texto_filtro_aplicado()

    resultado_esperado = ""

    assert dados == resultado_esperado


def test_filtros_aplicados_com_data_inicio_e_com_data_final(repasse_exportacao_csv):
    queryset = Repasse.objects.all()

    data_inicio = datetime.date.today()
    data_final = datetime.date.today()

    dados = ExportacaoDadosRepassesService(
        queryset=queryset,
        data_inicio=str(data_inicio),
        data_final=str(data_final)
    ).get_texto_filtro_aplicado()

    resultado_esperado = f"Filtro aplicado: {data_inicio.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')} (data de criação do registro)"

    assert dados == resultado_esperado


def test_filtros_aplicados_com_data_inicio_e_sem_data_final(repasse_exportacao_csv):
    queryset = Repasse.objects.all()

    data_inicio = datetime.date.today()

    dados = ExportacaoDadosRepassesService(
        queryset=queryset,
        data_inicio=str(data_inicio),
    ).get_texto_filtro_aplicado()

    resultado_esperado = f"Filtro aplicado: A partir de {data_inicio.strftime('%d/%m/%Y')} (data de criação do registro)"

    assert dados == resultado_esperado


def test_filtros_aplicados_sem_data_inicio_e_com_data_final(repasse_exportacao_csv):
    queryset = Repasse.objects.all()

    data_final = datetime.date.today()

    dados = ExportacaoDadosRepassesService(
        queryset=queryset,
        data_final=str(data_final),
    ).get_texto_filtro_aplicado()

    resultado_esperado = f"Filtro aplicado: Até {data_final.strftime('%d/%m/%Y')} (data de criação do registro)"

    assert dados == resultado_esperado


def test_cria_registro_central_download(usuario_para_teste):
    exportacao_repasses = ExportacaoDadosRepassesService(
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

        exportacao_repasses = ExportacaoDadosRepassesService(
            nome_arquivo='repasses.csv',
            user=usuario_para_teste.username
        )
        exportacao_repasses.cria_registro_central_download()
        exportacao_repasses.envia_arquivo_central_download(file)
        objeto_arquivo_download = exportacao_repasses.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_CONCLUIDO
    assert objeto_arquivo_download.identificador == 'repasses.csv'
    assert ArquivoDownload.objects.count() == 1

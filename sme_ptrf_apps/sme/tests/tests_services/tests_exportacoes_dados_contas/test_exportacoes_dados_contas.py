import datetime
from tempfile import NamedTemporaryFile
import pytest
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.sme.services.exporta_dados_contas_service import ExportacaoDadosContasService
from sme_ptrf_apps.core.models.conta_associacao import ContaAssociacao

pytestmark = pytest.mark.django_db


def test_cabecalho():
    dados = ExportacaoDadosContasService()
    cabecalho = [cabecalho[0] for cabecalho in dados.cabecalho]

    resultado_esperado = [
        'Código EOL',
        'Nome Unidade',
        'Nome Associação',
        'DRE',
        'Nome do tipo de conta',
        'Data de criação da conta',
        'Data de início da conta',
        'Banco',
        'Agência',
        'Nº da conta com o dígito',
        'Saldo_atual',
        'Status',
        'Data do encerramento',
        'Status do encerramento',
        'Motivo de rejeição do encerramento',
    ]

    assert cabecalho == resultado_esperado


def test_rodape(conta_associacao_exportacao_csv, ambiente):
    queryset = ContaAssociacao.objects.all()

    dados = ExportacaoDadosContasService(
        queryset=queryset,
        user="12345"
    ).texto_rodape()

    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    resultado_esperado = f"Arquivo gerado via {ambiente.prefixo} pelo usuário 12345 em {data_atual}"

    assert dados == resultado_esperado


def test_filtra_range_data_fora_do_range(conta_associacao_exportacao_csv):
    queryset = ContaAssociacao.objects.all()

    data_inicio = str(datetime.date(2020, 2, 10))
    data_final = str(datetime.date(2020, 5, 10))

    queryset_filtrado = ExportacaoDadosContasService(
        queryset=queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == 0


def test_filtra_range_data_dentro_do_range(conta_associacao_exportacao_csv):
    queryset = ContaAssociacao.objects.all()

    data_inicio = str(datetime.date.today())
    data_final = str(datetime.date.today())

    queryset_filtrado = ExportacaoDadosContasService(
        queryset=queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset)


def test_filtra_range_data_com_data_inicio_e_sem_data_final(conta_associacao_exportacao_csv):
    queryset = ContaAssociacao.objects.all()

    data_inicio = str(datetime.date.today())

    queryset_filtrado = ExportacaoDadosContasService(
        queryset=queryset,
        data_inicio=data_inicio
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset)


def test_filtra_range_data_sem_data_inicio_e_com_data_final(conta_associacao_exportacao_csv):
    queryset = ContaAssociacao.objects.all()

    data_final = str(datetime.date.today())

    queryset_filtrado = ExportacaoDadosContasService(
        queryset=queryset,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset)


def test_filtra_range_data_sem_data_inicio_e_sem_data_final(conta_associacao_exportacao_csv):
    queryset = ContaAssociacao.objects.all()

    queryset_filtrado = ExportacaoDadosContasService(
        queryset=queryset
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset)


def test_filtros_aplicados_sem_data_inicio_e_sem_data_final(conta_associacao_exportacao_csv):
    queryset = ContaAssociacao.objects.all()

    dados = ExportacaoDadosContasService(
        queryset=queryset
    ).get_texto_filtro_aplicado()

    resultado_esperado = ""

    assert dados == resultado_esperado


def test_filtros_aplicados_com_data_inicio_e_com_data_final(conta_associacao_exportacao_csv):
    queryset = ContaAssociacao.objects.all()

    data_inicio = datetime.date.today()
    data_final = datetime.date.today()

    dados = ExportacaoDadosContasService(
        queryset=queryset,
        data_inicio=str(data_inicio),
        data_final=str(data_final)
    ).get_texto_filtro_aplicado()

    resultado_esperado = f"Filtro aplicado: {data_inicio.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')} (data de criação do registro)"

    assert dados == resultado_esperado


def test_filtros_aplicados_com_data_inicio_e_sem_data_final(conta_associacao_exportacao_csv):
    queryset = ContaAssociacao.objects.all()

    data_inicio = datetime.date.today()

    dados = ExportacaoDadosContasService(
        queryset=queryset,
        data_inicio=str(data_inicio),
    ).get_texto_filtro_aplicado()

    resultado_esperado = f"Filtro aplicado: A partir de {data_inicio.strftime('%d/%m/%Y')} (data de criação do registro)"

    assert dados == resultado_esperado


def test_filtros_aplicados_sem_data_inicio_e_com_data_final(conta_associacao_exportacao_csv):
    queryset = ContaAssociacao.objects.all()

    data_final = datetime.date.today()

    dados = ExportacaoDadosContasService(
        queryset=queryset,
        data_final=str(data_final),
    ).get_texto_filtro_aplicado()

    resultado_esperado = f"Filtro aplicado: Até {data_final.strftime('%d/%m/%Y')} (data de criação do registro)"

    assert dados == resultado_esperado


def test_cria_registro_central_download(usuario_para_teste):
    exportacao_dados_contas = ExportacaoDadosContasService(
        nome_arquivo='dados_contas.csv',
        user=usuario_para_teste.username
    )

    exportacao_dados_contas.cria_registro_central_download()
    objeto_arquivo_download = exportacao_dados_contas.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_EM_PROCESSAMENTO
    assert objeto_arquivo_download.identificador == 'dados_contas.csv'
    assert ArquivoDownload.objects.count() == 1


def test_envia_arquivo_central_download(usuario_para_teste):
    with NamedTemporaryFile(
        mode="r+",
        newline='',
        encoding='utf-8',
        prefix='dados_contas',
        suffix='.csv'
    ) as file:
        file.write("testando central de download")

        exportacao_dados_contas = ExportacaoDadosContasService(
            nome_arquivo='dados_contas.csv',
            user=usuario_para_teste.username
        )
        exportacao_dados_contas.cria_registro_central_download()
        exportacao_dados_contas.envia_arquivo_central_download(file)
        objeto_arquivo_download = exportacao_dados_contas.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_CONCLUIDO
    assert objeto_arquivo_download.identificador == 'dados_contas.csv'
    assert ArquivoDownload.objects.count() == 1

import datetime
from tempfile import NamedTemporaryFile
import pytest
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload

from sme_ptrf_apps.sme.services.exporta_dados_saldos_bancarios_service import ExportacaoDadosSaldosBancariosService
from sme_ptrf_apps.core.models.observacao_conciliacao import ObservacaoConciliacao

pytestmark = pytest.mark.django_db


def test_cabecalho():
    dados = ExportacaoDadosSaldosBancariosService()

    cabecalho = [cabecalho[0] for cabecalho in dados.cabecalho]

    resultado_esperado = [
        'Código EOL da Unidade',
        'Nome Unidade',
        'Tipo da unidade',
        'Nome Associação',
        'DRE',
        'Data extrato',
        'Valor extrato',
        'Período',
        'Conta',
        'Comprovante do saldo da conta',
        'Última atualização'
    ]

    assert cabecalho == resultado_esperado


def test_dados_saldos_bancarios_esperados_csv(observacao_conciliacao_exportacao_csv, ambiente):
    queryset = ObservacaoConciliacao.objects.all()

    dados = ExportacaoDadosSaldosBancariosService(queryset=queryset).monta_dados()

    linha_individual = dados[0]

    resultado_esperado = [
        observacao_conciliacao_exportacao_csv.associacao.unidade.codigo_eol,
        observacao_conciliacao_exportacao_csv.associacao.unidade.nome,
        observacao_conciliacao_exportacao_csv.associacao.unidade.tipo_unidade,
        observacao_conciliacao_exportacao_csv.associacao.nome,
        observacao_conciliacao_exportacao_csv.associacao.unidade.dre.nome,
        '30/06/2020',
        '300,00',
        observacao_conciliacao_exportacao_csv.periodo.referencia,
        observacao_conciliacao_exportacao_csv.conta_associacao.tipo_conta.nome,
        'https://dev-sig-escola.sme.prefeitura.sp.gov.br/media/comprovante.pdf',
        observacao_conciliacao_exportacao_csv.alterado_em.strftime("%d/%m/%Y às %H:%M:%S")

    ]

    assert linha_individual == resultado_esperado


def test_rodape(observacao_conciliacao_exportacao_csv, ambiente):
    queryset = ObservacaoConciliacao.objects.all()

    dados = ExportacaoDadosSaldosBancariosService(
        queryset=queryset,
        user="12345"
    ).texto_info_arquivo_gerado()

    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    resultado_esperado = f"Arquivo solicitado via {ambiente.prefixo} pelo usuário 12345 em {data_atual}"

    assert dados == resultado_esperado


def test_filtra_range_data_fora_do_range(observacao_conciliacao_exportacao_csv):
    queryset = ObservacaoConciliacao.objects.all()

    data_inicio = str(datetime.date(2020, 2, 10))
    data_final = str(datetime.date(2020, 5, 10))

    queryset_filtrado = ExportacaoDadosSaldosBancariosService(
        queryset=queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == 0


def test_filtra_range_data_dentro_do_range(observacao_conciliacao_exportacao_csv):
    queryset = ObservacaoConciliacao.objects.all()

    data_inicio = str(datetime.date.today())
    data_final = str(datetime.date.today())

    queryset_filtrado = ExportacaoDadosSaldosBancariosService(
        queryset=queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset)


def test_filtra_range_data_com_data_inicio_e_sem_data_final(observacao_conciliacao_exportacao_csv):
    queryset = ObservacaoConciliacao.objects.all()

    data_inicio = str(datetime.date.today())

    queryset_filtrado = ExportacaoDadosSaldosBancariosService(
        queryset=queryset,
        data_inicio=data_inicio
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset)


def test_filtra_range_data_sem_data_inicio_e_com_data_final(observacao_conciliacao_exportacao_csv):
    queryset = ObservacaoConciliacao.objects.all()

    data_final = str(datetime.date.today())

    queryset_filtrado = ExportacaoDadosSaldosBancariosService(
        queryset=queryset,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset)


def test_filtra_range_data_sem_data_inicio_e_sem_data_final(observacao_conciliacao_exportacao_csv):
    queryset = ObservacaoConciliacao.objects.all()

    queryset_filtrado = ExportacaoDadosSaldosBancariosService(
        queryset=queryset
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset)


def test_filtros_aplicados_sem_data_inicio_e_sem_data_final(observacao_conciliacao_exportacao_csv):
    queryset = ObservacaoConciliacao.objects.all()

    dados = ExportacaoDadosSaldosBancariosService(
        queryset=queryset
    ).get_texto_filtro_aplicado()

    resultado_esperado = ""

    assert dados == resultado_esperado


def test_filtros_aplicados_com_data_inicio_e_com_data_final(observacao_conciliacao_exportacao_csv):
    queryset = ObservacaoConciliacao.objects.all()

    data_inicio = datetime.date.today()
    data_final = datetime.date.today()

    dados = ExportacaoDadosSaldosBancariosService(
        queryset=queryset,
        data_inicio=str(data_inicio),
        data_final=str(data_final)
    ).get_texto_filtro_aplicado()

    resultado_esperado = f"Filtro aplicado: {data_inicio.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')} (data de criação do registro)"

    assert dados == resultado_esperado


def test_filtros_aplicados_com_data_inicio_e_sem_data_final(observacao_conciliacao_exportacao_csv):
    queryset = ObservacaoConciliacao.objects.all()

    data_inicio = datetime.date.today()

    dados = ExportacaoDadosSaldosBancariosService(
        queryset=queryset,
        data_inicio=str(data_inicio),
    ).get_texto_filtro_aplicado()

    resultado_esperado = f"Filtro aplicado: A partir de {data_inicio.strftime('%d/%m/%Y')} (data de criação do registro)"

    assert dados == resultado_esperado


def test_filtros_aplicados_sem_data_inicio_e_com_data_final(observacao_conciliacao_exportacao_csv):
    queryset = ObservacaoConciliacao.objects.all()

    data_final = datetime.date.today()

    dados = ExportacaoDadosSaldosBancariosService(
        queryset=queryset,
        data_final=str(data_final),
    ).get_texto_filtro_aplicado()

    resultado_esperado = f"Filtro aplicado: Até {data_final.strftime('%d/%m/%Y')} (data de criação do registro)"

    assert dados == resultado_esperado


def test_cria_registro_central_download(usuario_para_teste):
    exportacao_saldos_bancarios = ExportacaoDadosSaldosBancariosService(
        nome_arquivo='saldo_bancario_unidades.csv',
        user=usuario_para_teste.username
    )

    exportacao_saldos_bancarios.cria_registro_central_download()
    objeto_arquivo_download = exportacao_saldos_bancarios.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_EM_PROCESSAMENTO
    assert objeto_arquivo_download.identificador == 'saldo_bancario_unidades.csv'
    assert ArquivoDownload.objects.count() == 1


def test_envia_arquivo_central_download(usuario_para_teste):
    with NamedTemporaryFile(
        mode="r+",
        newline='',
        encoding='utf-8',
        prefix='saldo_bancario_unidades',
        suffix='.csv'
    ) as file:
        file.write("testando central de download")

        exportacao_saldos_bancarios = ExportacaoDadosSaldosBancariosService(
            nome_arquivo='saldo_bancario_unidades.csv',
            user=usuario_para_teste.username
        )
        exportacao_saldos_bancarios.cria_registro_central_download()
        exportacao_saldos_bancarios.envia_arquivo_central_download(file)
        objeto_arquivo_download = exportacao_saldos_bancarios.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_CONCLUIDO
    assert objeto_arquivo_download.identificador == 'saldo_bancario_unidades.csv'
    assert ArquivoDownload.objects.count() == 1

import datetime
import pytest

from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.sme.services.exporta_saldo_final_periodo_pc_service import ExportacoesDadosSaldosFinaisPeriodoService
from tempfile import NamedTemporaryFile

pytestmark = pytest.mark.django_db


def test_cria_registro_central_download(usuario_para_teste):
    exportacao_saldo_final = ExportacoesDadosSaldosFinaisPeriodoService(
        nome_arquivo='pcs_saldo_final_periodo.csv',
        user=usuario_para_teste.username
    )

    exportacao_saldo_final.cria_registro_central_download()
    objeto_arquivo_download = exportacao_saldo_final.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_EM_PROCESSAMENTO
    assert objeto_arquivo_download.identificador == 'pcs_saldo_final_periodo.csv'
    assert ArquivoDownload.objects.count() == 1


def test_envia_arquivo_central_download(usuario_para_teste):
    with NamedTemporaryFile(
        mode="r+",
        newline='',
        encoding='utf-8',
        prefix='pcs_saldo_final_periodo',
        suffix='.csv'
    ) as file:
        file.write("testando central de download")

        exportacao_saldo_final = ExportacoesDadosSaldosFinaisPeriodoService(
            nome_arquivo='pcs_saldo_final_periodo.csv',
            user=usuario_para_teste.username
        )
        exportacao_saldo_final.cria_registro_central_download()
        exportacao_saldo_final.envia_arquivo_central_download(file)
        objeto_arquivo_download = exportacao_saldo_final.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_CONCLUIDO
    assert objeto_arquivo_download.identificador == 'pcs_saldo_final_periodo.csv'
    assert ArquivoDownload.objects.count() == 1


def test_filtra_range_data_fora_do_range(fechamento_periodo_queryset):
    data_inicio = datetime.date(2020, 2, 25)
    data_inicio = data_inicio.strftime('%Y-%m-%d')
    data_final = datetime.date(2020, 4, 26)
    data_final = data_final.strftime('%Y-%m-%d')

    queryset_filtrado = ExportacoesDadosSaldosFinaisPeriodoService(
        queryset=fechamento_periodo_queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == 0


def test_filtra_range_data_dentro_do_range(fechamento_periodo_queryset):
    data_inicio = datetime.date.today()
    data_inicio = data_inicio.strftime('%Y-%m-%d')
    data_final = datetime.date.today()
    data_final = data_final.strftime('%Y-%m-%d')

    queryset_filtrado = ExportacoesDadosSaldosFinaisPeriodoService(
        queryset=fechamento_periodo_queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(fechamento_periodo_queryset)


def test_filtra_range_data_com_data_inicio_e_sem_data_final(fechamento_periodo_queryset):
    data_inicio = datetime.date.today()
    data_inicio = data_inicio.strftime('%Y-%m-%d')

    queryset_filtrado = ExportacoesDadosSaldosFinaisPeriodoService(
        queryset=fechamento_periodo_queryset,
        data_inicio=data_inicio
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(fechamento_periodo_queryset)


def test_filtra_range_data_sem_data_inicio_e_com_data_final(fechamento_periodo_queryset):
    data_final = datetime.date.today()
    data_final = data_final.strftime('%Y-%m-%d')

    queryset_filtrado = ExportacoesDadosSaldosFinaisPeriodoService(
        queryset=fechamento_periodo_queryset,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(fechamento_periodo_queryset)


def test_filtra_range_data_sem_data_inicio_e_sem_data_final(fechamento_periodo_queryset):
    queryset_filtrado = ExportacoesDadosSaldosFinaisPeriodoService(
        queryset=fechamento_periodo_queryset
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(fechamento_periodo_queryset)


def test_quantidade_dados_extracao(fechamento_periodo_queryset):
    dados = ExportacoesDadosSaldosFinaisPeriodoService(
        queryset=fechamento_periodo_queryset,
    ).monta_dados()

    # Existem dois registros de fechamentos, porém é criado uma linha para cada tipo de recurso (Custeio, Capital, Livre)
    # Portando o tamanho correto é 2x3 (6)

    assert len(dados) == 6


def test_quantidade_linha_individual_dados_extracao(fechamento_periodo_queryset):
    dados = ExportacoesDadosSaldosFinaisPeriodoService(
        queryset=fechamento_periodo_queryset,
    ).monta_dados()

    linha_individual = dados[0]

    """
        É esperado que tenha 9 registros sendo eles:
            Codigo eol
            Nome unidade
            Nome associacao
            Referencia do periodo
            Status da PC
            Nome do tipo de Conta
            Tipo de aplicação do recurso
            Valor
    """

    assert len(linha_individual) == 10


def test_resultado_esperado_dados_extracao(fechamento_periodo_queryset):
    dados = ExportacoesDadosSaldosFinaisPeriodoService(
        queryset=fechamento_periodo_queryset,
    ).monta_dados()

    linha_individual = dados[0]
    primeiro_fechamento = fechamento_periodo_queryset.first()

    resultado_esperado = [
        primeiro_fechamento.associacao.unidade.codigo_eol,
        primeiro_fechamento.associacao.unidade.nome,
        primeiro_fechamento.associacao.nome,
        primeiro_fechamento.associacao.unidade.dre.nome,
        primeiro_fechamento.periodo.referencia,
        primeiro_fechamento.prestacao_conta.status,
        primeiro_fechamento.conta_associacao.tipo_conta.nome,
        primeiro_fechamento.acao_associacao.acao.nome,
        "Custeio",
        str(getattr(primeiro_fechamento, "saldo_reprogramado_custeio")).replace(".", ",")
    ]

    assert linha_individual == resultado_esperado


def test_cabecalho(fechamento_periodo_queryset):
    dados = ExportacoesDadosSaldosFinaisPeriodoService(
        queryset=fechamento_periodo_queryset,
    )

    cabecalho = [cabecalho[0] for cabecalho in dados.cabecalho]

    resultado_esperado = [
        'Código EOL',
        'Nome Unidade',
        'Nome Associação',
        'DRE',
        'Referência do Período da PC',
        'Status da PC',
        'Nome do tipo de Conta',
        'Nome da Ação',
        'Tipo de aplicação do recurso',
        'Valor'
    ]

    assert cabecalho == resultado_esperado


def test_rodape(fechamento_periodo_queryset, ambiente):
    dados = ExportacoesDadosSaldosFinaisPeriodoService(
        queryset=fechamento_periodo_queryset,
        user="12345"
    ).texto_rodape()

    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    resultado_esperado = f"Arquivo gerado via {ambiente.prefixo} pelo usuário 12345 em {data_atual}"

    assert dados == resultado_esperado


def test_filtros_aplicados_sem_data_inicio_e_sem_data_final(fechamento_periodo_queryset, ambiente):
    dados = ExportacoesDadosSaldosFinaisPeriodoService(
        queryset=fechamento_periodo_queryset,
    ).get_informacoes_download()

    resultado_esperado = ""

    assert dados == resultado_esperado


def test_filtros_aplicados_com_data_inicio_e_com_data_final(fechamento_periodo_queryset, ambiente):

    data_inicio = '2024-03-01'
    data_final = '2024-03-26'

    dados = ExportacoesDadosSaldosFinaisPeriodoService(
        queryset=fechamento_periodo_queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).get_informacoes_download()

    resultado_esperado = f"Filtro aplicado: 01/03/2024 a 26/03/2024 (data de criação do registro)"

    assert dados == resultado_esperado


def test_filtros_aplicados_com_data_inicio_e_sem_data_final(fechamento_periodo_queryset, ambiente):

    data_inicio = '2024-03-01'

    dados = ExportacoesDadosSaldosFinaisPeriodoService(
        queryset=fechamento_periodo_queryset,
        data_inicio=data_inicio,
    ).get_informacoes_download()

    resultado_esperado = f"Filtro aplicado: A partir de 01/03/2024 (data de criação do registro)"

    assert dados == resultado_esperado


def test_filtros_aplicados_sem_data_inicio_e_com_data_final(fechamento_periodo_queryset, ambiente):

    data_final = '2024-03-26'

    dados = ExportacoesDadosSaldosFinaisPeriodoService(
        queryset=fechamento_periodo_queryset,
        data_final=data_final,
    ).get_informacoes_download()

    resultado_esperado = f"Filtro aplicado: Até 26/03/2024 (data de criação do registro)"

    assert dados == resultado_esperado

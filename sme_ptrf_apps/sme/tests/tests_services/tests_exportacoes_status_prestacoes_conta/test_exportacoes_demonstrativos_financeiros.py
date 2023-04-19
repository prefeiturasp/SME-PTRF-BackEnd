import datetime
import pytest

from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.sme.services.exporta_demonstrativos_financeiros_service import ExportaDemonstrativosFinanceirosService
from tempfile import NamedTemporaryFile
from decimal import Decimal

pytestmark = pytest.mark.django_db


def test_cria_registro_central_download(usuario_para_teste):
    demonstrativo_financeiro = ExportaDemonstrativosFinanceirosService(
        nome_arquivo='pcs_demonstrativos.csv',
        user=usuario_para_teste.username
    )

    demonstrativo_financeiro.cria_registro_central_download()
    objeto_arquivo_download = demonstrativo_financeiro.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_EM_PROCESSAMENTO
    assert objeto_arquivo_download.identificador == 'pcs_demonstrativos.csv'
    assert ArquivoDownload.objects.count() == 1


def test_envia_arquivo_central_download(usuario_para_teste):
    with NamedTemporaryFile(
        mode="r+",
        newline='',
        encoding='utf-8',
        prefix='pcs_demonstrativos',
        suffix='.csv'
    ) as file:
        file.write("testando central de download")

        demonstrativo_financeiro = ExportaDemonstrativosFinanceirosService(
            nome_arquivo='pcs_demonstrativos.csv',
            user=usuario_para_teste.username
        )
        demonstrativo_financeiro.cria_registro_central_download()
        demonstrativo_financeiro.envia_arquivo_central_download(file)
        objeto_arquivo_download = demonstrativo_financeiro.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_CONCLUIDO
    assert objeto_arquivo_download.identificador == 'pcs_demonstrativos.csv'
    assert ArquivoDownload.objects.count() == 1


def test_filtra_range_data_fora_do_range(demonstrativo_financeiro_queryset):
    data_inicio = datetime.date(2020, 2, 25)
    data_final = datetime.date(2020, 4, 26)

    queryset_filtrado = ExportaDemonstrativosFinanceirosService(
        queryset=demonstrativo_financeiro_queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == 0


def test_filtra_range_data_dentro_do_range(demonstrativo_financeiro_queryset):
    data_inicio = datetime.date.today()
    data_final = datetime.date.today()

    queryset_filtrado = ExportaDemonstrativosFinanceirosService(
        queryset=demonstrativo_financeiro_queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(demonstrativo_financeiro_queryset)


def test_filtra_range_data_com_data_inicio_e_sem_data_final(demonstrativo_financeiro_queryset):
    data_inicio = datetime.date.today()

    queryset_filtrado = ExportaDemonstrativosFinanceirosService(
        queryset=demonstrativo_financeiro_queryset,
        data_inicio=data_inicio
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(demonstrativo_financeiro_queryset)


def test_filtra_range_data_sem_data_inicio_e_com_data_final(demonstrativo_financeiro_queryset):
    data_final = datetime.date.today()

    queryset_filtrado = ExportaDemonstrativosFinanceirosService(
        queryset=demonstrativo_financeiro_queryset,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(demonstrativo_financeiro_queryset)


def test_filtra_range_data_sem_data_inicio_e_sem_data_final(demonstrativo_financeiro_queryset):
    queryset_filtrado = ExportaDemonstrativosFinanceirosService(
        queryset=demonstrativo_financeiro_queryset
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(demonstrativo_financeiro_queryset)

def test_quantidade_dados_extracao(demonstrativo_financeiro_queryset):
    dados = ExportaDemonstrativosFinanceirosService(
        queryset=demonstrativo_financeiro_queryset,
    ).monta_dados()

    # Existem dois registros de demonstrativo financeiro
    assert len(dados) == 2


def test_quantidade_linha_individual_dados_extracao(demonstrativo_financeiro_queryset):
    dados = ExportaDemonstrativosFinanceirosService(
        queryset=demonstrativo_financeiro_queryset,
    ).monta_dados()

    linha_individual = dados[0]

    """
        É esperado que tenha 13 registros sendo eles:
        Código EOL
        Nome Unidade
        Nome Associação
        Referência do Período da PC
        Nome do tipo de Conta
        Data (Saldo bancário)
        Saldo bancário'
        Justificativa e informações adicionais (Informações de conciliação)
        URL do arquivo PDF
        Status
        Versão
        Data e hora de criação
        Data e hora da última atualização
    """

    assert len(linha_individual) == 13


def test_resultado_esperado_dados_extracao(
    demonstrativo_financeiro_queryset,
    observacao_conciliacao_teste_exportacao,
    ambiente
):
    dados = ExportaDemonstrativosFinanceirosService(
        queryset=demonstrativo_financeiro_queryset,
    ).monta_dados()

    linha_individual = dados[0]
    primeiro_demonstrativo_financeiro = demonstrativo_financeiro_queryset.first()

    resultado_esperado = [
        primeiro_demonstrativo_financeiro.conta_associacao.associacao.unidade.codigo_eol,
        primeiro_demonstrativo_financeiro.conta_associacao.associacao.unidade.nome,
        primeiro_demonstrativo_financeiro.conta_associacao.associacao.nome,
        primeiro_demonstrativo_financeiro.prestacao_conta.periodo.referencia,
        primeiro_demonstrativo_financeiro.conta_associacao.tipo_conta.nome,
        datetime.date(2020, 7, 1),
        Decimal('1000.00'),
        'Uma bela observação.',
        f"https://{ambiente.prefixo}.sme.prefeitura.sp.gov.br{primeiro_demonstrativo_financeiro.arquivo_pdf.url}",
        primeiro_demonstrativo_financeiro.status,
        primeiro_demonstrativo_financeiro.versao,
        primeiro_demonstrativo_financeiro.criado_em.strftime("%d/%m/%Y às %H:%M:%S"),
        primeiro_demonstrativo_financeiro.alterado_em.strftime("%d/%m/%Y às %H:%M:%S"),
    ]

    assert linha_individual == resultado_esperado


def test_cabecalho(demonstrativo_financeiro_queryset):
    dados = ExportaDemonstrativosFinanceirosService(
        queryset=demonstrativo_financeiro_queryset,
    )

    cabecalho = [cabecalho[0] for cabecalho in dados.cabecalho]

    resultado_esperado = [
        'Código EOL',
        'Nome Unidade',
        'Nome Associação',
        'Referência do Período da PC',
        'Nome do tipo de Conta',
        'Data (Saldo bancário)',
        'Saldo bancário',
        'Justificativa e informações adicionais (Informações de conciliação)',
        'URL do arquivo PDF',
        'Status',
        'Versão',
        'Data e hora de criação',
        'Data e hora da última atualização',
    ]

    assert cabecalho == resultado_esperado


def test_rodape(demonstrativo_financeiro_queryset, ambiente):
    dados = ExportaDemonstrativosFinanceirosService(
        queryset=demonstrativo_financeiro_queryset,
    ).texto_rodape()

    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    resultado_esperado = f"Arquivo gerado pelo {ambiente.prefixo} em {data_atual}"

    assert dados == resultado_esperado

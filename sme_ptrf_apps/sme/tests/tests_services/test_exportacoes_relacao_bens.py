import datetime
import pytest

from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.sme.services.exporta_relacao_bens_pc import ExportacoesDadosRelacaoBensService
from tempfile import NamedTemporaryFile

pytestmark = pytest.mark.django_db


def test_envia_arquivo_central_download(usuario_para_teste):
    with NamedTemporaryFile(
        mode="r+",
        newline='',
        encoding='utf-8',
        prefix='pcs_relacoes_bens',
        suffix='.csv'
    ) as file:
        file.write("testando central de download")
    ExportacoesDadosRelacaoBensService(
        nome_arquivo='pcs_relacoes_bens.csv',
        user=usuario_para_teste.username
    ).envia_arquivo_central_download(file)

    assert ArquivoDownload.objects.count() == 1

def test_filtra_range_data_fora_do_range(relacao_bens_queryset):
    data_inicio = datetime.date(2020, 2, 25)
    data_final = datetime.date(2020, 4, 26)

    queryset_filtrado = ExportacoesDadosRelacaoBensService(
        queryset=relacao_bens_queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == 0

def test_filtra_range_data_dentro_do_range(relacao_bens_queryset):
    data_inicio = datetime.date.today()
    data_final = datetime.date.today()

    queryset_filtrado = ExportacoesDadosRelacaoBensService(
        queryset=relacao_bens_queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(relacao_bens_queryset)

def test_filtra_range_data_com_data_inicio_e_sem_data_final(relacao_bens_queryset):
    data_inicio = datetime.date.today()

    queryset_filtrado = ExportacoesDadosRelacaoBensService(
        queryset=relacao_bens_queryset,
        data_inicio=data_inicio
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(relacao_bens_queryset)

def test_filtra_range_data_sem_data_inicio_e_com_data_final(relacao_bens_queryset):
    data_final = datetime.date.today()

    queryset_filtrado = ExportacoesDadosRelacaoBensService(
        queryset=relacao_bens_queryset,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(relacao_bens_queryset)

def test_filtra_range_data_sem_data_inicio_e_sem_data_final(relacao_bens_queryset):
    queryset_filtrado = ExportacoesDadosRelacaoBensService(
        queryset=relacao_bens_queryset
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(relacao_bens_queryset)


def test_quantidade_dados_extracao(relacao_bens_queryset):
    dados = ExportacoesDadosRelacaoBensService(
        queryset=relacao_bens_queryset,
    ).monta_dados()

    # Existem dois registros de relação de bens
    assert len(dados) == 2

def test_quantidade_linha_individual_dados_extracao(relacao_bens_queryset):
    dados = ExportacoesDadosRelacaoBensService(
        queryset=relacao_bens_queryset,
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
            URL do arquivo PDF
            Status,
            Versão,
            Data e hora de criação,
            Data e hora da última atualização
    """

    assert len(linha_individual) == 11

def test_resultado_esperado_dados_extracao(relacao_bens_queryset, ambiente):
    dados = ExportacoesDadosRelacaoBensService(
        queryset=relacao_bens_queryset,
    ).monta_dados()

    linha_individual = dados[0]
    primeira_relacao_bens = relacao_bens_queryset.first()

    resultado_esperado = [
        primeira_relacao_bens.prestacao_conta.associacao.unidade.codigo_eol,
        primeira_relacao_bens.prestacao_conta.associacao.unidade.nome,
        primeira_relacao_bens.prestacao_conta.associacao.nome,
        primeira_relacao_bens.prestacao_conta.periodo.referencia,
        primeira_relacao_bens.prestacao_conta.status,
        primeira_relacao_bens.conta_associacao.tipo_conta.nome,
        f"https://{ambiente.prefixo}.sme.prefeitura.sp.gov.br{primeira_relacao_bens.arquivo_pdf.url}",
        primeira_relacao_bens.status,
        primeira_relacao_bens.versao,
        primeira_relacao_bens.criado_em.strftime("%d/%m/%Y às %H:%M:%S"),
        primeira_relacao_bens.alterado_em.strftime("%d/%m/%Y às %H:%M:%S"),
    ]

    assert linha_individual == resultado_esperado

def test_cabecalho(relacao_bens_queryset):
    dados = ExportacoesDadosRelacaoBensService(
        queryset=relacao_bens_queryset,
    )

    cabecalho = [cabecalho[0] for cabecalho in dados.cabecalho]

    resultado_esperado = [
        'Código EOL',
        'Nome Unidade',
        'Nome Associação',
        'Referência do Período da PC',
        'Status da PC',
        'Nome do tipo de Conta',
        'URL do arquivo PDF',
        'Status',
        'Versão',
        'Data e hora de criação',
        'Data e hora da última atualização'
    ]

    assert cabecalho == resultado_esperado

def test_rodape(relacao_bens_queryset, ambiente):
    dados = ExportacoesDadosRelacaoBensService(
        queryset=relacao_bens_queryset,
    ).texto_rodape()

    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    resultado_esperado = f"Arquivo gerado pelo {ambiente.prefixo} em {data_atual}"

    assert dados == resultado_esperado


import datetime
import pytest

from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.sme.services.exporta_rateios_service import ExportacoesRateiosService
from tempfile import NamedTemporaryFile

pytestmark = pytest.mark.django_db

def test_cria_registro_central_download(usuario_para_teste):
    exportacao_rateio = ExportacoesRateiosService(
        nome_arquivo='despesas_classificacao_item.csv',
        user=usuario_para_teste.username
    )

    exportacao_rateio.cria_registro_central_download()
    objeto_arquivo_download = exportacao_rateio.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_EM_PROCESSAMENTO
    assert objeto_arquivo_download.identificador == 'despesas_classificacao_item.csv'
    assert ArquivoDownload.objects.count() == 1


def test_envia_arquivo_central_download(usuario_para_teste):
    with NamedTemporaryFile(
        mode="r+",
        newline='',
        encoding='utf-8',
        prefix='despesas_classificacao_item',
        suffix='.csv'
    ) as file:
        file.write("testando central de download")

        exportacao_rateio = ExportacoesRateiosService(
            nome_arquivo='despesas_classificacao_item.csv',
            user=usuario_para_teste.username
        )
        exportacao_rateio.cria_registro_central_download()
        exportacao_rateio.envia_arquivo_central_download(file)
        objeto_arquivo_download = exportacao_rateio.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_CONCLUIDO
    assert objeto_arquivo_download.identificador == 'despesas_classificacao_item.csv'
    assert ArquivoDownload.objects.count() == 1

def test_filtra_range_data_fora_do_range(rateios_despesa_queryset):
    data_inicio = datetime.date(2020, 2, 25)
    data_final = datetime.date(2020, 4, 26)

    queryset_filtrado = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('despesa__criado_em')

    assert queryset_filtrado.count() == 0

def test_filtra_range_data_dentro_do_range(rateios_despesa_queryset):
    data_inicio = datetime.date.today()
    data_final = datetime.date.today()

    queryset_filtrado = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('despesa__criado_em')

    assert queryset_filtrado.count() == len(rateios_despesa_queryset)

def test_filtra_range_data_com_data_inicio_e_sem_data_final(rateios_despesa_queryset):
    data_inicio = datetime.date.today()

    queryset_filtrado = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset,
        data_inicio=data_inicio
    ).filtra_range_data('despesa__criado_em')

    assert queryset_filtrado.count() == len(rateios_despesa_queryset)

def test_filtra_range_data_sem_data_inicio_e_com_data_final(rateios_despesa_queryset):
    data_final = datetime.date.today()

    queryset_filtrado = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset,
        data_final=data_final
    ).filtra_range_data('despesa__criado_em')

    assert queryset_filtrado.count() == len(rateios_despesa_queryset)

def test_filtra_range_data_sem_data_inicio_e_sem_data_final(rateios_despesa_queryset):
    queryset_filtrado = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset
    ).filtra_range_data('despesa__criado_em')

    assert queryset_filtrado.count() == len(rateios_despesa_queryset)


def test_quantidade_dados_extracao(rateios_despesa_queryset):
    dados = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset,
    ).monta_dados()

    # Existem tres registros de rateios
    assert len(dados) == 3

def test_quantidade_linha_individual_dados_extracao(rateios_despesa_queryset):
    dados = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset,
    ).monta_dados()

    linha_individual = dados[0]

    """
        É esperado que tenha 9 registros sendo eles:
            Codigo eol
            Nome unidade
            Nome associacao
            ID do Gasto
            Número do documento
            Tipo de documento
            Data do documento
            CPF_CNPJ do fornecedor
            Nome do fornecedor
            Tipo de transação
            Número do documento da transação
            Data da transação
            Tipo de aplicação do recurso
            Nome do Tipo de Custeio
            Descrição da Especificação de Material ou Serviço
            Nome do tipo de Conta
            Nome da Ação
            Quantidade de itens
            Valor unitário
            Número do processo de incorporação
            Valor
            Valor realizado
            Status do rateio
            Conferido
            Referência do período de conciliação
            Descrição da tag
            É saída de recurso externo?
            É gasto sem comprovação fiscal?
            É pagamento antecipado?
            Tem estorno cadastrado?
            Data e hora de criação
            Data e hora da última atualização
            UUID do rateio
    """

    assert len(linha_individual) == 33

def test_resultado_esperado_dados_extracao(rateios_despesa_queryset):
    dados = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset,
    ).monta_dados()

    linha_individual = dados[0]
    primeiro_rateio = rateios_despesa_queryset.first()

    resultado_esperado = [
        primeiro_rateio.associacao.unidade.codigo_eol,
        primeiro_rateio.associacao.unidade.nome,
        primeiro_rateio.associacao.nome,
        primeiro_rateio.despesa.id,
        primeiro_rateio.despesa.numero_documento,
        primeiro_rateio.despesa.tipo_documento.nome,
        primeiro_rateio.despesa.data_documento.strftime("%d/%m/%Y"),
        primeiro_rateio.despesa.cpf_cnpj_fornecedor,
        primeiro_rateio.despesa.nome_fornecedor,
        primeiro_rateio.despesa.tipo_transacao.nome,
        primeiro_rateio.despesa.documento_transacao,
        primeiro_rateio.despesa.data_transacao.strftime("%d/%m/%Y"),
        primeiro_rateio.aplicacao_recurso,
        primeiro_rateio.tipo_custeio.nome,
        primeiro_rateio.especificacao_material_servico.descricao,
        primeiro_rateio.conta_associacao.tipo_conta.nome,
        primeiro_rateio.acao_associacao.acao.nome,
        primeiro_rateio.quantidade_itens_capital,
        str(getattr(primeiro_rateio, 'valor_item_capital')).replace(".", ","),
        primeiro_rateio.numero_processo_incorporacao_capital,
        str(getattr(primeiro_rateio, 'valor_rateio')).replace(".", ","),
        str(getattr(primeiro_rateio, 'valor_original')).replace(".", ","),
        "Completo",
        "Sim",
        primeiro_rateio.periodo_conciliacao.referencia,
        "COVID-19",
        "Não",
        "Não",
        "Não",
        "Não",
        primeiro_rateio.criado_em.strftime("%d/%m/%Y às %H:%M:%S"),
        primeiro_rateio.alterado_em.strftime("%d/%m/%Y às %H:%M:%S"),
        primeiro_rateio.uuid,
    ]

    assert linha_individual == resultado_esperado

def test_cabecalho(rateios_despesa_queryset):
    dados = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset,
    )

    cabecalho = [cabecalho[0] for cabecalho in dados.cabecalho]

    resultado_esperado = [
        'Código EOL',
        'Nome Unidade',
        'Nome Associação',
        'ID do Gasto',
        'Número do documento',
        'Tipo de documento',
        'Data do documento',
        'CPF_CNPJ do fornecedor',
        'Nome do fornecedor',
        'Tipo de transação',
        'Número do documento da transação',
        'Data da transação',
        'Tipo de aplicação do recurso',
        'Nome do Tipo de Custeio',
        'Descrição da Especificação de Material ou Serviço',
        'Nome do tipo de Conta',
        'Nome da Ação',
        'Quantidade de itens',
        'Valor unitário',
        'Número do processo de incorporação',
        'Valor',
        'Valor realizado',
        'Status do rateio',
        'Conferido',
        'Referência do período de conciliação',
        'Descrição da tag',
        'É saída de recurso externo?',
        'É gasto sem comprovação fiscal?',
        'É pagamento antecipado?',
        'Tem estorno cadastrado?',
        'Data e hora de criação',
        'Data e hora da última atualização',
        'UUID do rateio'
    ]

    assert cabecalho == resultado_esperado

def test_rodape(rateios_despesa_queryset, ambiente):
    dados = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset,
    ).texto_rodape()

    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    resultado_esperado = f"Arquivo gerado pelo {ambiente.prefixo} em {data_atual}"

    assert dados == resultado_esperado


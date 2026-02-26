import datetime
import pytest

from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.sme.services.exporta_rateios_service import ExportacoesRateiosService
from sme_ptrf_apps.utils.anonimizar_cpf_cnpj import anonimizar_cpf
from tempfile import NamedTemporaryFile

pytestmark = pytest.mark.django_db


def test_dados_extracao(rateios_despesa_queryset):
    dados = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset,
    ).monta_dados()

    # Existem tres registros de rateios
    assert len(dados) == 3


def test_dados_extracao_dre(rateios_despesa_queryset, dre_ipiranga):

    rateios_despesa_queryset_dre = rateios_despesa_queryset.filter(
        associacao__unidade__dre__uuid=f"{dre_ipiranga.uuid}",
    ).order_by('id')

    dados = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset_dre,
        dre_uuid=dre_ipiranga.uuid
    ).monta_dados()

    # Não existe nenhum rateio para a Dre Ipiranga
    assert len(dados) == 0


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
    data_inicio = str(datetime.date(2020, 2, 25))
    data_final = str(datetime.date(2020, 4, 26))

    queryset_filtrado = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('despesa__criado_em')

    assert queryset_filtrado.count() == 0


def test_filtra_range_data_dentro_do_range(rateios_despesa_queryset):
    data_inicio = str(datetime.date.today())
    data_final = str(datetime.date.today())

    queryset_filtrado = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('despesa__criado_em')

    assert queryset_filtrado.count() == len(rateios_despesa_queryset)


def test_filtra_range_data_com_data_inicio_e_sem_data_final(rateios_despesa_queryset):
    data_inicio = str(datetime.date.today())

    queryset_filtrado = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset,
        data_inicio=data_inicio
    ).filtra_range_data('despesa__criado_em')

    assert queryset_filtrado.count() == len(rateios_despesa_queryset)


def test_filtra_range_data_sem_data_inicio_e_com_data_final(rateios_despesa_queryset):
    data_final = str(datetime.date.today())

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
        É esperado que tenha 35 registros sendo eles:
            Recurso
            Codigo eol
            Nome unidade
            Nome associacao
            DRE
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

    assert len(linha_individual) == 35


def test_resultado_esperado_dados_extracao(rateios_despesa_queryset):
    dados = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset,
    ).monta_dados()

    linha_individual = dados[0]
    primeiro_rateio = rateios_despesa_queryset.first()

    resultado_esperado = [
        primeiro_rateio.despesa.recurso.nome,
        primeiro_rateio.associacao.unidade.codigo_eol,
        primeiro_rateio.associacao.unidade.nome,
        primeiro_rateio.associacao.nome,
        primeiro_rateio.associacao.unidade.nome_dre,
        primeiro_rateio.despesa.id,
        f'="{primeiro_rateio.despesa.numero_documento}"',
        primeiro_rateio.despesa.tipo_documento.nome,
        primeiro_rateio.despesa.data_documento.strftime("%d/%m/%Y"),
        anonimizar_cpf(
            primeiro_rateio.despesa.cpf_cnpj_fornecedor
        ) if primeiro_rateio.despesa.cpf_cnpj_fornecedor else "",
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
        'Recurso',
        'Código EOL',
        'Nome Unidade',
        'Nome Associação',
        'DRE',
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
        user="12345"
    ).texto_rodape()

    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    resultado_esperado = (
        f"Arquivo solicitado via {ambiente.prefixo} pelo usuário 12345 em "
        f"{data_atual}"
    )

    assert dados == resultado_esperado


def test_filtros_aplicados_sem_data_inicio_e_sem_data_final(rateios_despesa_queryset):
    dados = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset,
    ).get_texto_filtro_aplicado()

    resultado_esperado = ""

    assert dados == resultado_esperado


def test_filtros_aplicados_com_data_inicio_e_com_data_final(
    rateios_despesa_queryset,
):
    data_inicio = datetime.date.today()
    data_final = datetime.date.today()

    dados = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset,
        data_inicio=str(data_inicio),
        data_final=str(data_final)
    ).get_texto_filtro_aplicado()

    resultado_esperado = (
        "Filtro aplicado: "
        f"{data_inicio.strftime('%d/%m/%Y')} a "
        f"{data_final.strftime('%d/%m/%Y')} (data de criação do registro)"
    )

    assert dados == resultado_esperado


def test_filtros_aplicados_com_data_inicio_e_sem_data_final(
    rateios_despesa_queryset,
):
    data_inicio = datetime.date.today()

    dados = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset,
        data_inicio=str(data_inicio)
    ).get_texto_filtro_aplicado()

    resultado_esperado = (
        "Filtro aplicado: "
        f"A partir de {data_inicio.strftime('%d/%m/%Y')} "
        "(data de criação do registro)"
    )

    assert dados == resultado_esperado


def test_filtros_aplicados_sem_data_inicio_e_com_data_final(
    rateios_despesa_queryset,
):
    data_final = datetime.date.today()

    dados = ExportacoesRateiosService(
        queryset=rateios_despesa_queryset,
        data_final=str(data_final)
    ).get_texto_filtro_aplicado()

    resultado_esperado = (
        "Filtro aplicado: "
        f"Até {data_final.strftime('%d/%m/%Y')} (data de criação do registro)"
    )

    assert dados == resultado_esperado

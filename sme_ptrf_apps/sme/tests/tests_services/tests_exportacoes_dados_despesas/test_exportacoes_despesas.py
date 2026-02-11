from tempfile import NamedTemporaryFile
import pytest
import datetime
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload

from sme_ptrf_apps.sme.services.exporta_documentos_despesas import ExportacoesDocumentosDespesasService
from sme_ptrf_apps.utils.anonimizar_cpf_cnpj import anonimizar_cpf_cnpj_fornecedor

pytestmark = pytest.mark.django_db


def test_dados_esperados_csv(queryset_ordered):
    dados = ExportacoesDocumentosDespesasService(queryset=queryset_ordered).monta_dados()

    linha_individual = dados[0]
    primeira_despesa = queryset_ordered.first()

    resultado_esperado = [
        primeira_despesa.associacao.unidade.codigo_eol,
        primeira_despesa.associacao.unidade.nome,
        primeira_despesa.associacao.nome,
        primeira_despesa.associacao.unidade.dre.nome,
        primeira_despesa.id,
        'Sim' if primeira_despesa.eh_despesa_sem_comprovacao_fiscal else 'Não',
        'Sim' if primeira_despesa.eh_despesa_reconhecida_pela_associacao else 'Não',
        primeira_despesa.numero_documento,
        primeira_despesa.tipo_documento.nome,
        primeira_despesa.data_documento.strftime("%d/%m/%Y"),
        anonimizar_cpf_cnpj_fornecedor(
            primeira_despesa.cpf_cnpj_fornecedor
        ) if primeira_despesa.cpf_cnpj_fornecedor else "",
        primeira_despesa.nome_fornecedor,
        primeira_despesa.tipo_transacao.nome,
        primeira_despesa.documento_transacao,
        primeira_despesa.data_transacao.strftime("%d/%m/%Y"),
        str(primeira_despesa.valor_total).replace(".", ","),
        str(primeira_despesa.valor_original).replace(".", ","),
        str(primeira_despesa.valor_recursos_proprios).replace(".", ","),
        primeira_despesa.numero_boletim_de_ocorrencia,
        'Sim' if primeira_despesa.retem_imposto else 'Não',
        '',
        'Sim' if primeira_despesa.valor_recursos_proprios > 0 else 'Não',
        primeira_despesa.status,
        primeira_despesa.criado_em.strftime("%d/%m/%Y às %H:%M:%S"),
        primeira_despesa.alterado_em.strftime("%d/%m/%Y às %H:%M:%S"),
        str(primeira_despesa.uuid),
    ]

    assert linha_individual == resultado_esperado


def test_cabecalho():
    dados = ExportacoesDocumentosDespesasService()

    cabecalho = [cabecalho[0] for cabecalho in dados.cabecalho]

    resultado_esperado = [
        'Código EOL',
        'Nome unidade',
        'Nome associação',
        'DRE',
        'ID do gasto',
        'É despesa sem comprovação fiscal?',
        'É despesa reconhecida pela Associação?',
        'Número do documento',
        'Tipo de documento',
        'Data do documento',
        'CPF_CNPJ do fornecedor',
        'Nome do fornecedor',
        'Tipo de transação',
        'Número do documento de transação',
        'Data da transação',
        'Valor total do documento',
        'Valor realizado',
        'Valor pago com recursos próprios',
        'Número do Boletim de Ocorrência',
        'Retem impostos?',
        'Descrição do motivo de pagamento antecipado',
        'É saída de recurso externo?',
        'Status do gasto',
        'Data e hora de criação',
        'Data e hora da última atualização',
        'UUID do gasto'
    ]

    assert cabecalho == resultado_esperado


def test_rodape(ambiente):
    dados = ExportacoesDocumentosDespesasService(
        user="12345"
    ).texto_rodape()

    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    # resultado_esperado = f"Arquivo gerado pelo {ambiente.prefixo} em {data_atual}"
    resultado_esperado = (
        f"Arquivo solicitado via {ambiente.prefixo} pelo usuário 12345 em "
        f"{data_atual}"
    )

    assert dados == resultado_esperado


def test_filtra_range_data_fora_do_range(queryset_ordered):
    data_inicio = datetime.date(2020, 2, 25)
    data_inicio = data_inicio.strftime('%Y-%m-%d')
    data_final = datetime.date(2020, 4, 26)
    data_final = data_final.strftime('%Y-%m-%d')

    queryset_filtrado = ExportacoesDocumentosDespesasService(
        queryset=queryset_ordered,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == 0


def test_filtra_range_data_dentro_do_range(queryset_ordered):
    data_inicio = datetime.date.today()
    data_inicio = data_inicio.strftime('%Y-%m-%d')
    data_final = datetime.date.today()
    data_final = data_final.strftime('%Y-%m-%d')

    queryset_filtrado = ExportacoesDocumentosDespesasService(
        queryset=queryset_ordered,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset_ordered)


def test_filtra_range_data_com_data_inicio_e_sem_data_final(queryset_ordered):
    data_inicio = datetime.date.today()
    data_inicio = data_inicio.strftime('%Y-%m-%d')

    queryset_filtrado = ExportacoesDocumentosDespesasService(
        queryset=queryset_ordered,
        data_inicio=data_inicio
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset_ordered)


def test_filtra_range_data_sem_data_inicio_e_com_data_final(queryset_ordered):
    data_final = datetime.date.today()
    data_final = data_final.strftime('%Y-%m-%d')

    queryset_filtrado = ExportacoesDocumentosDespesasService(
        queryset=queryset_ordered,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset_ordered)


def test_filtra_range_data_sem_data_inicio_e_sem_data_final(queryset_ordered):
    queryset_filtrado = ExportacoesDocumentosDespesasService(
        queryset=queryset_ordered
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset_ordered)


def test_cria_registro_central_download(usuario_para_teste):
    exportacao_saldo_final = ExportacoesDocumentosDespesasService(
        nome_arquivo='pcs_despesas.csv',
        user=usuario_para_teste.username
    )

    exportacao_saldo_final.cria_registro_central_download()
    objeto_arquivo_download = exportacao_saldo_final.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_EM_PROCESSAMENTO
    assert objeto_arquivo_download.identificador == 'pcs_despesas.csv'
    assert ArquivoDownload.objects.count() == 1


def test_envia_arquivo_central_download(usuario_para_teste):
    with NamedTemporaryFile(
        mode="r+",
        newline='',
        encoding='utf-8',
        prefix='pcs_despesas',
        suffix='.csv'
    ) as file:
        file.write("testando central de download")

        exportacao_despesas = ExportacoesDocumentosDespesasService(
            nome_arquivo='pcs_despesas.csv',
            user=usuario_para_teste.username
        )
        exportacao_despesas.cria_registro_central_download()
        exportacao_despesas.envia_arquivo_central_download(file)
        objeto_arquivo_download = exportacao_despesas.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_CONCLUIDO
    assert objeto_arquivo_download.identificador == 'pcs_despesas.csv'
    assert ArquivoDownload.objects.count() == 1


def test_filtros_aplicados_sem_data_inicio_e_sem_data_final(queryset_ordered, ambiente):
    dados = ExportacoesDocumentosDespesasService(
        queryset=queryset_ordered,
    ).get_informacoes_download()

    resultado_esperado = ""

    assert dados == resultado_esperado


def test_filtros_aplicados_com_data_inicio_e_com_data_final(queryset_ordered, ambiente):

    data_inicio = '2024-03-01'
    data_final = '2024-03-26'

    dados = ExportacoesDocumentosDespesasService(
        queryset=queryset_ordered,
        data_inicio=data_inicio,
        data_final=data_final
    ).get_informacoes_download()

    resultado_esperado = (
        "Filtro aplicado: 01/03/2024 a 26/03/2024 "
        "(data de criação do registro)"
    )

    assert dados == resultado_esperado


def test_filtros_aplicados_com_data_inicio_e_sem_data_final(queryset_ordered, ambiente):

    data_inicio = '2024-03-01'

    dados = ExportacoesDocumentosDespesasService(
        queryset=queryset_ordered,
        data_inicio=data_inicio,
    ).get_informacoes_download()

    resultado_esperado = (
        "Filtro aplicado: A partir de 01/03/2024 "
        "(data de criação do registro)"
    )

    assert dados == resultado_esperado


def test_filtros_aplicados_sem_data_inicio_e_com_data_final(queryset_ordered, ambiente):

    data_final = '2024-03-26'

    dados = ExportacoesDocumentosDespesasService(
        queryset=queryset_ordered,
        data_final=data_final
    ).get_informacoes_download()

    resultado_esperado = (
        "Filtro aplicado: Até 26/03/2024 "
        "(data de criação do registro)"
    )

    assert dados == resultado_esperado

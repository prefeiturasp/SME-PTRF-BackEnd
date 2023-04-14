from tempfile import NamedTemporaryFile
import pytest
import datetime
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.models.devolucao_ao_tesouro import DevolucaoAoTesouro

from sme_ptrf_apps.sme.services.exporta_devolucao_tesouro_prestacoes_conta import ExportacoesDevolucaoTesouroPrestacoesContaService

pytestmark = pytest.mark.django_db

def test_dados_esperados_csv(queryset_ordered):
    dados = ExportacoesDevolucaoTesouroPrestacoesContaService(
        queryset=queryset_ordered
    ).monta_dados()

    linha_individual = dados[0]
    primeira_solicitacao = queryset_ordered.first()

    pc = primeira_solicitacao.solicitacao_acerto_lancamento.analise_lancamento.analise_prestacao_conta.prestacao_conta

    despesa = primeira_solicitacao.solicitacao_acerto_lancamento.analise_lancamento.despesa

    rateio = despesa.rateios.first()

    devolucao_ao_tesouro = DevolucaoAoTesouro.objects.filter(despesa_id=despesa.id).first()

    resultado_esperado = [
        pc.associacao.unidade.codigo_eol,
        pc.associacao.unidade.nome,
        pc.associacao.nome,
        pc.periodo.referencia,
        pc.status,
        despesa.id,
        despesa.numero_documento,
        despesa.tipo_documento.nome,
        despesa.data_documento.strftime("%d/%m/%Y"),
        despesa.cpf_cnpj_fornecedor,
        despesa.nome_fornecedor,
        despesa.tipo_transacao.nome,
        despesa.documento_transacao,
        despesa.data_transacao.strftime("%d/%m/%Y"),
        str(despesa.valor_original).replace(".", ","),
        str(despesa.valor_total).replace(".", ","),
        rateio.aplicacao_recurso,
        rateio.tipo_custeio.nome,
        rateio.especificacao_material_servico.descricao,
        rateio.conta_associacao.tipo_conta.nome,
        rateio.acao_associacao.acao.nome,
        str(rateio.valor_rateio).replace(".", ","),
        str(rateio.valor_original).replace(".", ","),
        devolucao_ao_tesouro.tipo.id,
        devolucao_ao_tesouro.tipo.nome,
        devolucao_ao_tesouro.motivo,
        'Sim' if devolucao_ao_tesouro.devolucao_total else 'Não',
        str(devolucao_ao_tesouro.valor).replace(".", ","),
        devolucao_ao_tesouro.data.strftime("%d/%m/%Y"),
        primeira_solicitacao.solicitacao_acerto_lancamento.justificativa if primeira_solicitacao.solicitacao_acerto_lancamento.justificativa is not None else ''
    ]

    assert linha_individual == resultado_esperado

def test_cabecalho():
    dados = ExportacoesDevolucaoTesouroPrestacoesContaService()

    cabecalho = [cabecalho[0] for cabecalho in dados.cabecalho]

    resultado_esperado = [
        'Código EOL', 
        'Nome Unidade', 
        'Nome Associação', 
        'Referência do Período da PC', 
        'Status da PC', 
        'ID da despesa',
        'Número do documento',
        'Tipo do documento', 
        'Data do documento', 
        'CPF_CNPJ do fornecedor', 
        'Nome do fornecedor', 
        'Tipo de transação', 
        'Número do documento da transação', 
        'Data da transação', 
        'Valor (Despeza)', 
        'Valor realizado (Despesa)', 
        'Tipo de aplicação do recurso', 
        'Nome do Tipo de Custeio',
        'Descrição da especificação de Material ou Serviço',
        'Nome do tipo de Conta',
        'Nome da Ação',
        'Valor (Rateios)',
        'Valor realizado (Rateio)',
        'Tipo de devolução',
        'Descrição do Tipo de devolução',
        'Motivo',
        'É devolução total?',
        'Valor (Devolução)',
        'Data de devolução ao tesouro',
        'Justificativa (não realização)',
    ]

    assert cabecalho == resultado_esperado

def test_rodape(ambiente):
    dados = ExportacoesDevolucaoTesouroPrestacoesContaService().texto_rodape()

    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    resultado_esperado = f"Arquivo gerado pelo {ambiente.prefixo} em {data_atual}"

    assert dados == resultado_esperado

def test_filtra_range_data_fora_do_range(queryset_ordered):
    data_inicio = datetime.date(2020, 2, 10)
    data_final = datetime.date(2020, 5, 10)

    queryset_filtrado = ExportacoesDevolucaoTesouroPrestacoesContaService(
        queryset=queryset_ordered,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == 0

def test_filtra_range_data_dentro_do_range(queryset_ordered):
    data_inicio = datetime.date.today()
    data_final = datetime.date.today()

    queryset_filtrado = ExportacoesDevolucaoTesouroPrestacoesContaService(
        queryset=queryset_ordered,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset_ordered)

def test_filtra_range_data_com_data_inicio_e_sem_data_final(queryset_ordered):
    data_inicio = datetime.date.today()

    queryset_filtrado = ExportacoesDevolucaoTesouroPrestacoesContaService(
        queryset=queryset_ordered,
        data_inicio=data_inicio
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset_ordered)

def test_filtra_range_data_sem_data_inicio_e_com_data_final(queryset_ordered):
    data_final = datetime.date.today()

    queryset_filtrado = ExportacoesDevolucaoTesouroPrestacoesContaService(
        queryset=queryset_ordered,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset_ordered)

def test_filtra_range_data_sem_data_inicio_e_sem_data_final(queryset_ordered):
    queryset_filtrado = ExportacoesDevolucaoTesouroPrestacoesContaService(
        queryset=queryset_ordered
    ).filtra_range_data('criado_em')
    
    assert queryset_filtrado.count() == len(queryset_ordered)

def test_cria_registro_central_download(usuario_para_teste):
    exportacao_saldo_final = ExportacoesDevolucaoTesouroPrestacoesContaService(
        nome_arquivo='pcs_devolucoes_tesouro.csv',
        user=usuario_para_teste.username
    )

    exportacao_saldo_final.cria_registro_central_download()
    objeto_arquivo_download = exportacao_saldo_final.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_EM_PROCESSAMENTO
    assert objeto_arquivo_download.identificador == 'pcs_devolucoes_tesouro.csv'
    assert ArquivoDownload.objects.count() == 1

def test_envia_arquivo_central_download(usuario_para_teste):
    with NamedTemporaryFile(
        mode="r+",
        newline='',
        encoding='utf-8',
        prefix='pcs_relacoes_bens',
        suffix='.csv'
    ) as file:
        file.write("testando central de download")

        exportacao_relacao_bens = ExportacoesDevolucaoTesouroPrestacoesContaService(
            nome_arquivo='pcs_devolucoes_tesouro.csv',
            user=usuario_para_teste.username
        )
        exportacao_relacao_bens.cria_registro_central_download()
        exportacao_relacao_bens.envia_arquivo_central_download(file)
        objeto_arquivo_download = exportacao_relacao_bens.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_CONCLUIDO
    assert objeto_arquivo_download.identificador == 'pcs_devolucoes_tesouro.csv'
    assert ArquivoDownload.objects.count() == 1
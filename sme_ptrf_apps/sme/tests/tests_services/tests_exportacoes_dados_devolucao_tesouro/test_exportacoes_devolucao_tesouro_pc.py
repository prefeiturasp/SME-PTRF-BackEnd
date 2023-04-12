import pytest
import datetime

from sme_ptrf_apps.sme.services.exporta_devolucao_tesouro_prestacoes_conta import ExportacoesDevolucaoTesouroPrestacoesContaService

pytestmark = pytest.mark.django_db

resultado_esperado = [
    ['123456', 'Escola Teste', 'Escola Teste', '2019.2', 'EM_ANALISE', 10, '123456', 'NFe', '10/03/2020', '11.478.276/0001-04', 'Fornecedor SA', 'Boleto', '12345', '10/03/2020', '0,00', '100,00', 'CUSTEIO', 'Servico', 'Material elétrico', 'Cheque', 'PTRF', '20,00', '10,00', 10, 'Tipo devolução 1', 'Motivo teste 1', 'Sim', '100,00', '01/07/2020'], ['123456', 'Escola Teste', 'Escola Teste', '2019.2', 'EM_ANALISE', 10, '123456', 'NFe', '10/03/2020', '11.478.276/0001-04', 'Fornecedor SA', 'Boleto', '12345', '10/03/2020', '0,00', '100,00', 'CUSTEIO', 'Servico', 'Material elétrico', 'Cheque', 'PTRF', '80,00', '70,00', 10, 'Tipo devolução 1', 'Motivo teste 1', 'Sim', '100,00', '01/07/2020'], ['123456', 'Escola Teste', 'Outra', '2019.2', 'EM_ANALISE', 11, '123456', 'NFe', '10/03/2020', '11.478.276/0001-04', 'Fornecedor SA', 'Boleto', '6789', '10/03/2020', '0,00', '200,00', '', '', '', '', '', '', '', 11, 'Tipo devolução 2', 'Motivo teste 2', 'Não', '50,00', '01/05/2020']
]

def test_dados_esperados_csv(queryset_ordered):
    print(queryset_ordered)
    dados = ExportacoesDevolucaoTesouroPrestacoesContaService(
        queryset=queryset_ordered
    ).monta_dados()

    print(dados)

    assert dados == resultado_esperado

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
        'Data de devolução ao tesouro'
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
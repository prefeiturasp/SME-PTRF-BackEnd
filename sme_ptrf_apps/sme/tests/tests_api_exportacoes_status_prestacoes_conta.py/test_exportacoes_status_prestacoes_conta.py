import pytest
import datetime

from sme_ptrf_apps.sme.services.exporta_status_prestacoes_conta_service import ExportacoesStatusPrestacoesContaService

pytestmark = pytest.mark.django_db

resultado_esperado = [
    ['123456', 'Escola Teste', 'Escola Teste', '2019.2', 'APROVADA_RESSALVA', 'Motivo aprovação 1', 'Recomendação teste', ''], 
    ['123456', 'Escola Teste', 'Escola Teste', '2019.2', 'APROVADA_RESSALVA', 'Motivo aprovação 2', 'Recomendação teste', ''], 
    ['123456', 'Escola Teste', 'Escola Teste', '2019.2', 'APROVADA_RESSALVA', 'Teste outro motivo aprovação ressalva', 'Recomendação teste', ''], 
    ['123456', 'Escola Teste', 'Outra', '2019.2', 'REPROVADA', '', '', 'Motivo reprovação 1'], 
    ['123456', 'Escola Teste', 'Outra', '2019.2', 'REPROVADA', '', '', 'Motivo reprovação 2'], 
    ['123456', 'Escola Teste', 'Outra', '2019.2', 'REPROVADA', '', '', 'Teste outro motivo reprovação']]

def test_dados_esperados_csv(queryset_ordered):
    dados = ExportacoesStatusPrestacoesContaService(
        queryset=queryset_ordered
    ).monta_dados()

    assert dados == resultado_esperado

def test_cabecalho(queryset_ordered):
    dados = ExportacoesStatusPrestacoesContaService(queryset=queryset_ordered)

    cabecalho = [cabecalho[0] for cabecalho in dados.cabecalho]

    resultado_esperado = [
        'Código EOL',
        'Nome Unidade',
        'Nome Associação',
        'Referência do Período da PC',
        'Status da PC',
        'Descrição do motivo aprovação com ressalvas',
        'Recomendações da aprovação com resalvas',
        'Descrição do motivo de reprovação',
    ]

    assert cabecalho == resultado_esperado


def test_rodape(ambiente):
    dados = ExportacoesStatusPrestacoesContaService().texto_rodape()

    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    resultado_esperado = f"Arquivo gerado pelo {ambiente.prefixo} em {data_atual}"

    assert dados == resultado_esperado

def test_filtra_range_data_fora_do_range(queryset_ordered):
    data_inicio = datetime.date(2020, 2, 10)
    data_final = datetime.date(2020, 5, 10)

    queryset_filtrado = ExportacoesStatusPrestacoesContaService(
        queryset=queryset_ordered,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == 0

def test_filtra_range_data_dentro_do_range(queryset_ordered):
    data_inicio = datetime.date.today()
    data_final = datetime.date.today()

    queryset_filtrado = ExportacoesStatusPrestacoesContaService(
        queryset=queryset_ordered,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset_ordered)

def test_filtra_range_data_com_data_inicio_e_sem_data_final(queryset_ordered):
    data_inicio = datetime.date.today()

    queryset_filtrado = ExportacoesStatusPrestacoesContaService(
        queryset=queryset_ordered,
        data_inicio=data_inicio
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset_ordered)

def test_filtra_range_data_sem_data_inicio_e_com_data_final(queryset_ordered):
    data_final = datetime.date.today()

    queryset_ordered[0].criado_em = datetime.date(2020, 1, 1)

    queryset_filtrado = ExportacoesStatusPrestacoesContaService(
        queryset=queryset_ordered,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset_ordered)

def test_filtra_range_data_sem_data_inicio_e_sem_data_final(queryset_ordered):
    queryset_filtrado = ExportacoesStatusPrestacoesContaService(
        queryset=queryset_ordered
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset_ordered)
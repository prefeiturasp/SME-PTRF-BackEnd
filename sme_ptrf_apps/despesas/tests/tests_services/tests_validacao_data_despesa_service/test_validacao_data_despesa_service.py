import pytest
from rest_framework import status
from sme_ptrf_apps.despesas.services.valida_data_despesa_service import ValidaDataDaDespesaAssociacaoEncerrada
import datetime

pytestmark = pytest.mark.django_db


def test_validacao_data_despesa_service_associacao_sem_data_encerramento(associacao):
    response = ValidaDataDaDespesaAssociacaoEncerrada(data_da_despesa='2023-04-26',
                                                      associacao=associacao).response

    assert response["sucesso"] == "Data da despesa válida"
    assert response["status"] == status.HTTP_200_OK

def test_validacao_data_despesa_service_despesa_com_data_menor_que_encerramento(associacao_encerrada_2020_1):
    data_da_despesa = '2020-06-29'
    data_da_despesa = datetime.datetime.strptime(data_da_despesa, '%Y-%m-%d')
    data_da_despesa = data_da_despesa.date()

    response = ValidaDataDaDespesaAssociacaoEncerrada(data_da_despesa=data_da_despesa,
                                                      associacao=associacao_encerrada_2020_1).response

    assert response["sucesso"] == "Data da despesa válida"
    assert response["status"] == status.HTTP_200_OK

def test_validacao_data_despesa_service_despesa_com_data_igual_ao_encerramento(associacao_encerrada_2020_1):
    data_da_despesa = '2020-06-30'
    data_da_despesa = datetime.datetime.strptime(data_da_despesa, '%Y-%m-%d')
    data_da_despesa = data_da_despesa.date()

    response = ValidaDataDaDespesaAssociacaoEncerrada(data_da_despesa=data_da_despesa,
                                                      associacao=associacao_encerrada_2020_1).response

    assert response["sucesso"] == "Data da despesa válida"
    assert response["status"] == status.HTTP_200_OK

def test_validacao_data_despesa_service_despesa_com_data_maior_ao_encerramento(associacao_encerrada_2020_1):
    data_da_despesa = '2020-07-01'
    data_da_despesa = datetime.datetime.strptime(data_da_despesa, '%Y-%m-%d')
    data_da_despesa = data_da_despesa.date()

    data_de_encerramento_tratada = associacao_encerrada_2020_1.data_de_encerramento.strftime("%d/%m/%Y")

    response = ValidaDataDaDespesaAssociacaoEncerrada(data_da_despesa=data_da_despesa,
                                                      associacao=associacao_encerrada_2020_1).response

    mensagem_validacao = f"A data de documento e/ou data do pagamento não pode ser posterior à " \
                         f"{data_de_encerramento_tratada}, data de encerramento da associação."

    assert response["erro_data_da_despesa"] is True
    assert response["data_de_encerramento"] == data_de_encerramento_tratada
    assert response["mensagem"] == mensagem_validacao
    assert response["status"] == status.HTTP_400_BAD_REQUEST

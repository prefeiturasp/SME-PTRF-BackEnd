import datetime
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_service_valida_data_da_receita_associacao_encerrada_deve_gerar_erro_data_da_receita_maior_que_data_encerramento_associacao(
    associacao_com_data_de_encerramento
):
    from ...services.receita_service import ValidaDataDaReceitaAssociacaoEncerrada

    data_da_receita = '2023-04-27'
    data_da_receita = datetime.datetime.strptime(data_da_receita, '%Y-%m-%d')
    data_da_receita = data_da_receita.date()

    # data_de_encerramento_da_associacao=date(2023, 4, 25),
    data_de_encerramento_tratada = associacao_com_data_de_encerramento.data_de_encerramento.strftime("%d/%m/%Y")

    response = ValidaDataDaReceitaAssociacaoEncerrada(data_da_receita=data_da_receita,
                                                      associacao=associacao_com_data_de_encerramento).response

    status_response = response.pop("status")

    assert status_response == status.HTTP_400_BAD_REQUEST

    esperado = {
        "erro_data_da_receita": True,
        "data_de_encerramento": f"{data_de_encerramento_tratada}",
        "mensagem": f"A data do crédito não pode ser posterior à {data_de_encerramento_tratada}, data de encerramento da associação.",
    }

    assert response == esperado


def test_service_valida_data_da_receita_associacao_encerrada_deve_passar_data_da_receita_menor_que_data_encerramento_associacao(
    associacao_com_data_de_encerramento
):
    from ...services.receita_service import ValidaDataDaReceitaAssociacaoEncerrada

    data_da_receita = '2023-04-25'
    data_da_receita = datetime.datetime.strptime(data_da_receita, '%Y-%m-%d')
    data_da_receita = data_da_receita.date()

    # data_de_encerramento_da_associacao=date(2023, 4, 25),

    response = ValidaDataDaReceitaAssociacaoEncerrada(data_da_receita=data_da_receita,
                                                      associacao=associacao_com_data_de_encerramento).response

    status_response = response.pop("status")

    assert status_response == status.HTTP_200_OK

    esperado = {
        "sucesso": "Data da receita válida",
    }

    assert response == esperado

from rest_framework import status

class ValidaDataDaDespesaAssociacaoEncerrada:
    """
        Valida data de documento ou data de transacao da despesa
    """

    def __init__(self, data_da_despesa, associacao):
        self.__data_da_despesa = data_da_despesa
        self.__associacao = associacao
        self.__data_de_encerramento = None
        self.__set_response()

    @property
    def data_da_despesa(self):
        return self.__data_da_despesa

    @property
    def associacao(self):
        return self.__associacao

    def __set_response(self):
        self.data_de_encerramento = self.associacao.data_de_encerramento if self.associacao.data_de_encerramento else None

        if self.data_da_despesa and self.data_de_encerramento and self.data_da_despesa > self.data_de_encerramento:
            data_de_encerramento_tratada = self.data_de_encerramento.strftime("%d/%m/%Y")
            self.response = {
                "erro_data_da_despesa":True,
                "data_de_encerramento": f"{data_de_encerramento_tratada}",
                "mensagem": f"A data de documento e/ou data do pagamento não pode ser posterior à "
                            f"{data_de_encerramento_tratada}, data de encerramento da associação.",
                "status": status.HTTP_400_BAD_REQUEST,
            }
        else:
            self.response = {
                "sucesso": "Data da despesa válida",
                "status": status.HTTP_200_OK,
            }

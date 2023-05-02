from rest_framework import status

from sme_ptrf_apps.core.models import Periodo


class ValidaDataDaReceitaAssociacaoEncerrada():
    def __init__(self, data_da_receita, associacao):
        self.__data_da_receita = data_da_receita
        self.__associacao = associacao
        self.__data_de_encerramento = None
        self.__set_response()


    @property
    def data_da_receita(self):
        return self.__data_da_receita

    @property
    def associacao(self):
        return self.__associacao

    def __set_response(self):
        self.data_de_encerramento = self.associacao.data_de_encerramento if self.associacao.data_de_encerramento else None

        if self.data_da_receita and self.data_de_encerramento and self.data_da_receita > self.data_de_encerramento:
            data_de_encerramento_tratada = self.data_de_encerramento.strftime("%d/%m/%Y")
            self.response = {
                "erro_data_da_receita":True,
                "data_de_encerramento": f"{data_de_encerramento_tratada}",
                "mensagem": f"A data do crédito não pode ser posterior à {data_de_encerramento_tratada}, data de encerramento da associação.",
                "status": status.HTTP_400_BAD_REQUEST,
            }
        else:
            self.response = {
                "sucesso": "Data da receita válida",
                "status": status.HTTP_200_OK,
            }


class ValidaPeriodosReceitaAssociacaoEncerrada():
    def __init__(self, associacao):
        self.__associacao = associacao
        self.__data_de_encerramento_da_associacao = associacao.data_de_encerramento
        self.__periodo_inicial_da_associacao = associacao.periodo_inicial
        self.__set_response()


    @property
    def associacao(self):
        return self.__associacao

    @property
    def data_de_encerramento_da_associacao(self):
        return self.__data_de_encerramento_da_associacao

    @property
    def periodo_inicial_da_associacao(self):
        return self.__periodo_inicial_da_associacao

    def __set_response(self):
        self.response = Periodo.objects.all()

        if self.periodo_inicial_da_associacao:
            data_inicio_realizacao_despesas_periodo_inicial = self.periodo_inicial_da_associacao.data_inicio_realizacao_despesas
            uuid_periodo_inicial = self.periodo_inicial_da_associacao.uuid

            self.response = self.response.filter(
                data_inicio_realizacao_despesas__gt=data_inicio_realizacao_despesas_periodo_inicial
            ).exclude(uuid=uuid_periodo_inicial).order_by('-data_inicio_realizacao_despesas')

        if self.data_de_encerramento_da_associacao:
            self.response = self.response.filter(
                data_inicio_realizacao_despesas__lt=self.data_de_encerramento_da_associacao
            ).order_by('-data_inicio_realizacao_despesas')






from django.db.models import Q
from ...despesas.models import Despesa
from ...receitas.models import Receita

class ValidaDataDeEncerramento():
    def __init__(self, associacao, data_de_encerramento):
        self.__associacao = associacao
        self.__data_de_encerramento = data_de_encerramento
        self.despesas = None
        self.receitas = None
        self.pode_encerrar = True

        self.checa_se_pode_encerrar()

    @property
    def data_de_encerramento(self):
        return self.__data_de_encerramento

    @property
    def associacao(self):
        return self.__associacao

    def retorna_se_tem_despesa(self):
        return Despesa.objects.filter(
                Q(status="COMPLETO") &
                Q(data_e_hora_de_inativacao__isnull=True) &
                Q(associacao=self.associacao) &
                Q(data_transacao__gte=self.data_de_encerramento)
            ).exists()

    def retorna_se_tem_receita(self):
        return Receita.objects.filter(
                Q(status="COMPLETO") &
                Q(associacao=self.associacao) &
                Q(data__gte=self.data_de_encerramento)
            ).exists()

    def checa_se_pode_encerrar(self):
        self.despesas = self.retorna_se_tem_despesa()
        self.receitas = self.retorna_se_tem_receita()

        if self.despesas or self.receitas:
            self.pode_encerrar = False

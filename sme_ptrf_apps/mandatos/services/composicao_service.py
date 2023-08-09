from ..models import Composicao
from datetime import date
from django.db.models import Q


class ServicoComposicaoVigente:

    def __init__(self, associacao, mandato):
        self.__associacao = associacao
        self.__mandato = mandato

    @property
    def associacao(self):
        return self.__associacao

    @property
    def mandato(self):
        return self.__mandato


    def get_composicao_vigente(self):
        data_atual = date.today()

        # Filtrar as composições com data_inicial anterior ou igual à data atual
        qs = Composicao.objects.filter(data_inicial__lte=data_atual)

        # Filtrar as composições com data_final posterior ou igual à data atual OU sem data_final definida
        qs = qs.filter(Q(data_final__gte=data_atual) | Q(data_final__isnull=True))

        # Filtrar as composições da associacao
        qs = qs.filter(associacao=self.associacao)

        #Filtrar as composições do mandato
        qs = qs.filter(mandato=self.mandato)

        # Verificar se há mais de uma composicao vigente, e caso haja, retornar o último (o mais recente)
        composicao_vigente = qs.last()

        return composicao_vigente


class ServicoCriaComposicaoVigenteDoMandato(ServicoComposicaoVigente):

    def __init__(self, associacao, mandato):
        super().__init__(associacao, mandato)

    def cria_composicao_vigente(self):
        composicao = Composicao.objects.create(
            associacao=self.associacao,
            mandato=self.mandato,
            data_inicial=self.mandato.data_inicial,
            data_final=self.mandato.data_final
        )

        return composicao


from datetime import datetime
from factory import SubFactory
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.core.models.prestacao_conta_reprovada_nao_apresentacao import PrestacaoContaReprovadaNaoApresentacao
from . import AssociacaoFactory
from .periodo_factory import PeriodoFactory

fake = Faker("pt_BR")


class PrestacaoContaReprovadaNaoApresentacaoFactory(DjangoModelFactory):
    class Meta:
        model = PrestacaoContaReprovadaNaoApresentacao

    periodo = SubFactory(PeriodoFactory)
    associacao = SubFactory(AssociacaoFactory)
    data_de_reprovacao = datetime(2024, 3, 4)

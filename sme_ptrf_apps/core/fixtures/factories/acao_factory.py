from factory import Sequence
from factory.django import DjangoModelFactory
from factory import SubFactory
from faker import Faker
from sme_ptrf_apps.core.models.acao import Acao
from sme_ptrf_apps.core.fixtures.factories.recurso_factory import RecursoFactory

fake = Faker("pt_BR")


class AcaoFactory(DjangoModelFactory):
    class Meta:
        model = Acao

    nome = Sequence(lambda n: fake.unique.name())
    posicao_nas_pesquisas = "ZZZZZZZZZZ"
    e_recursos_proprios = False
    aceita_capital = False
    aceita_custeio = False
    aceita_livre = False
    recurso = SubFactory(RecursoFactory)

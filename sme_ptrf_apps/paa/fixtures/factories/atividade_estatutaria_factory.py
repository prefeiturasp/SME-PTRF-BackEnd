from factory import Sequence, LazyFunction
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.paa.models import AtividadeEstatutaria
from sme_ptrf_apps.paa.choices import StatusChoices
from sme_ptrf_apps.paa.enums import TipoAtividadeEstatutariaEnum

fake = Faker("pt_BR")


class AtividadeEstatutariaFactory(DjangoModelFactory):
    class Meta:
        model = AtividadeEstatutaria

    status = LazyFunction(lambda: fake.random_element([StatusChoices.ATIVO, StatusChoices.INATIVO]))
    tipo = LazyFunction(lambda: fake.random_element([i.name for i in TipoAtividadeEstatutariaEnum]))
    nome = Sequence(lambda n: fake.unique.word())
    mes = Sequence(lambda n: fake.random_int(min=1, max=12))

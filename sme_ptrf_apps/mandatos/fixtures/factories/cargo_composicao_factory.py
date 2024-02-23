from factory import DjangoModelFactory, Sequence, LazyAttribute, SubFactory
from datetime import datetime, timedelta
from faker import Faker
from sme_ptrf_apps.mandatos.models import CargoComposicao
from .composicao_factory import ComposicaoFactory
from .ocupante_cargo_factory import OcupanteCargoFactory
from ..providers.cargo_composicao_provider import provider_cargo_associacao

fake = Faker("pt_BR")
fake.add_provider(provider_cargo_associacao)


class CargoComposicaoFactory(DjangoModelFactory):
    class Meta:
        model = CargoComposicao

    composicao = SubFactory(ComposicaoFactory)
    ocupante_do_cargo = SubFactory(OcupanteCargoFactory)
    cargo_associacao = fake.provider_cargo_associacao()
    substituto = False
    substituido = False
    data_inicio_no_cargo = Sequence(lambda n: fake.date_between_dates(date_start=datetime(2019, 1, 1), date_end=datetime.today()))
    data_fim_no_cargo = LazyAttribute(lambda obj: obj.data_inicio_no_cargo + timedelta(days=365))

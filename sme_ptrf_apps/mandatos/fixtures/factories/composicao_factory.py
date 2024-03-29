from factory import DjangoModelFactory, Sequence, LazyAttribute, SubFactory
from datetime import datetime, timedelta
from faker import Faker
from sme_ptrf_apps.mandatos.models import Composicao
from sme_ptrf_apps.core.fixtures.factories import AssociacaoFactory
from .mandato_factory import MandatoFactory

fake = Faker("pt_BR")

class ComposicaoFactory(DjangoModelFactory):
    class Meta:
        model = Composicao

    mandato = SubFactory(MandatoFactory)
    associacao = SubFactory(AssociacaoFactory)
    data_inicial = Sequence(lambda n: fake.date_between_dates(date_start=datetime(2019, 1, 1), date_end=datetime.today()))
    data_final = LazyAttribute(lambda obj: obj.data_inicial + timedelta(days=365))

from factory import DjangoModelFactory, Sequence, LazyAttribute
from datetime import datetime, timedelta
from faker import Faker
from sme_ptrf_apps.mandatos.models import Mandato

fake = Faker("pt_BR")

class MandatoFactory(DjangoModelFactory):
    class Meta:
        model = Mandato

    data_inicial = Sequence(lambda n: datetime.today())
    data_final = LazyAttribute(lambda obj: obj.data_inicial + timedelta(days=365))
    referencia_mandato = LazyAttribute(lambda obj: obj.data_inicial.strftime("%Y.1"))

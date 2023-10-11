from factory import DjangoModelFactory, Sequence, LazyAttribute
from datetime import datetime, timedelta, date
from faker import Faker
from sme_ptrf_apps.core.models.periodo import Periodo

fake = Faker("pt_BR")

class PeriodoFactory(DjangoModelFactory):
    class Meta:
        model = Periodo

    data_inicio_realizacao_despesas = Sequence(lambda n: fake.date_between_dates(date_start=datetime(2019, 1, 1), date_end=datetime.today()))
    data_fim_realizacao_despesas = LazyAttribute(lambda obj: obj.data_inicio_realizacao_despesas + timedelta(days=120))
    referencia = LazyAttribute(lambda obj: obj.data_inicio_realizacao_despesas.strftime("%Y.1"))

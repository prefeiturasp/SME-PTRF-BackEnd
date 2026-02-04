from datetime import datetime, timedelta
from faker import Faker
from factory import Sequence, Iterator, LazyAttribute
from factory.django import DjangoModelFactory
from sme_ptrf_apps.core.models.periodo import Periodo
from sme_ptrf_apps.core.models.recurso import Recurso
fake = Faker("pt_BR")


class PeriodoFactory(DjangoModelFactory):
    class Meta:
        model = Periodo

    data_inicio_realizacao_despesas = Sequence(lambda n: fake.date_between_dates(
        date_start=datetime(2019, 1, 1), date_end=datetime.today()))
    data_fim_realizacao_despesas = LazyAttribute(lambda obj: obj.data_inicio_realizacao_despesas + timedelta(days=120))
    referencia = LazyAttribute(lambda obj: obj.data_inicio_realizacao_despesas.strftime("%Y.1"))
    recurso = Iterator(Recurso.objects.all())

    # TODO adicionar outros campos


class PeriodoFactoryComDataFixa(DjangoModelFactory):
    class Meta:
        model = Periodo

    data_inicio_realizacao_despesas = Sequence(lambda n: fake.date_between_dates(
        date_start=datetime(2024, 4, 1), date_end=datetime(2024, 6, 1)))
    recurso = Iterator(Recurso.objects.all())

from factory import SubFactory
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.paa.models import OutroRecursoPeriodoPaa
from sme_ptrf_apps.paa.fixtures.factories import PeriodoPaaFactory, OutroRecursoFactory

fake = Faker("pt_BR")


class OutroRecursoPeriodoFactory(DjangoModelFactory):
    class Meta:
        model = OutroRecursoPeriodoPaa

    periodo_paa = SubFactory(PeriodoPaaFactory)
    outro_recurso = SubFactory(OutroRecursoFactory)
    ativo = True

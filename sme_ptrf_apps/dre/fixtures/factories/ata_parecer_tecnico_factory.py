import datetime

from factory import Sequence, SubFactory, LazyFunction
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.dre.models.ata_parecer_tecnico import AtaParecerTecnico
from sme_ptrf_apps.core.fixtures.factories.periodo_factory import PeriodoFactory
from sme_ptrf_apps.core.fixtures.factories.unidade_factory import DreFactory



fake = Faker("pt_BR")

class AtaParecerTecnicoFactory(DjangoModelFactory):
    class Meta:
        model = AtaParecerTecnico

    arquivo_pdf = None
    periodo = SubFactory(PeriodoFactory)
    dre = SubFactory(DreFactory)
    status_geracao_pdf = AtaParecerTecnico.STATUS_NAO_GERADO
    numero_ata = Sequence(lambda n: n + 1)
    data_reuniao = fake.date_this_decade()
    hora_reuniao = LazyFunction(lambda: datetime.time(hour=10, minute=0, second=0))
    local_reuniao = fake.city()
    comentarios = fake.sentence(nb_words=8)
    preenchida_em = fake.date_time_this_decade()
    numero_portaria = Sequence(lambda n: n + 1000)
    data_portaria = fake.date_this_decade()
    sequencia_de_publicacao = 1
    sequencia_de_retificacao = None


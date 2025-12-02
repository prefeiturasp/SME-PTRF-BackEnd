from factory import SubFactory
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.paa.models.documento_paa import DocumentoPaa
from sme_ptrf_apps.paa.fixtures.factories import PaaFactory

fake = Faker("pt_BR")


class DocumentoPaaFactory(DjangoModelFactory):
    class Meta:
        model = DocumentoPaa

    paa = SubFactory(PaaFactory)
    versao = "FINAL"
    status_geracao = "CONCLUIDO"

from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.paa.models.documento_paa import DocumentoPaa

fake = Faker("pt_BR")


class DocumentoPaaFactory(DjangoModelFactory):
    class Meta:
        model = DocumentoPaa

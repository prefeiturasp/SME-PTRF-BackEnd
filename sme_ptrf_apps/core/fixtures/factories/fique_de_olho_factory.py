from faker import Faker
from factory import LazyFunction, LazyAttribute, Sequence
from factory.django import DjangoModelFactory
from sme_ptrf_apps.core.models import FiqueDeOlho, Recurso, TipoTextoFiqueDeOlhoChoices

fake = Faker("pt_BR")


class FiqueDeOlhoFactory(DjangoModelFactory):
    class Meta:
        model = FiqueDeOlho

    texto = Sequence(lambda n: fake.text(max_nb_chars=100))

    tipo_texto = LazyAttribute(lambda x: fake.random_element(
        elements=[choice[0] for choice in TipoTextoFiqueDeOlhoChoices.choices]))

    recurso = LazyFunction(lambda: Recurso.objects.get(legado=True))

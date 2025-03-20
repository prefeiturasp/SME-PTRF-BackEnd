from factory import DjangoModelFactory, Sequence
from faker import Faker
from waffle.models import Flag

fake = Faker("pt_BR")


class FlagFactory(DjangoModelFactory):
    class Meta:
        model = Flag

    name = Sequence(lambda n: fake.unique.name())
    everyone = True

from factory import Sequence
from factory.django import DjangoModelFactory
from sme_ptrf_apps.users.models import Visao
import random


class VisaoFactory(DjangoModelFactory):
    class Meta:
        model = Visao

    nome = Sequence(lambda n: random.choice(["UE", "DRE", "SME"]))

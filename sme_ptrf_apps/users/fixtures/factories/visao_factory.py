from factory import DjangoModelFactory, Sequence
from sme_ptrf_apps.users.models import Visao
import random

class VisaoFactory(DjangoModelFactory):
    class Meta:
        model = Visao

    nome = Sequence(lambda n: random.choice(["UE", "DRE", "SME"]))
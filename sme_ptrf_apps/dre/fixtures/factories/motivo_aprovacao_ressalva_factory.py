from factory import Sequence
from factory.django import DjangoModelFactory

from sme_ptrf_apps.dre.models import MotivoAprovacaoRessalva


class MotivoAprovacaoRessalvaFactory(DjangoModelFactory):
    class Meta:
        model = MotivoAprovacaoRessalva

    motivo = Sequence(lambda n: f"Motivo aprovacao ressalva {n}")

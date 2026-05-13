from factory import Sequence, LazyFunction
from factory.django import DjangoModelFactory

from sme_ptrf_apps.core.models.recurso import Recurso
from sme_ptrf_apps.dre.models import MotivoReprovacao


class MotivoReprovacaoFactory(DjangoModelFactory):
    class Meta:
        model = MotivoReprovacao

    motivo = Sequence(lambda n: f"Motivo reprovacao {n}")
    recurso = LazyFunction(lambda: Recurso.objects.get(legado=True))

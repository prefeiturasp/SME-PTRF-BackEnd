from factory import Sequence, SubFactory
from factory.django import DjangoModelFactory

from sme_ptrf_apps.core.fixtures.factories.recurso_factory import RecursoFactory
from sme_ptrf_apps.dre.models import MotivoAprovacaoRessalva


class MotivoAprovacaoRessalvaFactory(DjangoModelFactory):
    class Meta:
        model = MotivoAprovacaoRessalva

    motivo = Sequence(lambda n: f"Motivo aprovacao ressalva {n}")
    recurso = SubFactory(RecursoFactory)

from factory import Sequence, SubFactory
from factory.django import DjangoModelFactory

from sme_ptrf_apps.core.fixtures.factories.recurso_factory import RecursoFactory
from sme_ptrf_apps.dre.models import MotivoReprovacao


class MotivoReprovacaoFactory(DjangoModelFactory):
    class Meta:
        model = MotivoReprovacao

    motivo = Sequence(lambda n: f"Motivo reprovacao {n}")
    recurso = SubFactory(RecursoFactory)

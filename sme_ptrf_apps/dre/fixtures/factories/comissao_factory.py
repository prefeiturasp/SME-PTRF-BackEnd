from factory import Sequence, post_generation
from factory.django import DjangoModelFactory

from sme_ptrf_apps.core.fixtures.factories.recurso_factory import RecursoFactory
from sme_ptrf_apps.dre.models import Comissao


class ComissaoFactory(DjangoModelFactory):
    class Meta:
        model = Comissao

    nome = Sequence(lambda n: f"Comissao {n}")
    responsavel_analise_pc = False

    @post_generation
    def recursos(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for recurso in extracted:
                self.recursos.add(recurso)
            return

        self.recursos.add(RecursoFactory())

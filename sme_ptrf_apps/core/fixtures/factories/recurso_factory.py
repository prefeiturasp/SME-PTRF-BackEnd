from factory import Sequence, Iterator
from factory.django import DjangoModelFactory
from sme_ptrf_apps.core.models.recurso import Recurso


class RecursoFactory(DjangoModelFactory):
    class Meta:
        model = Recurso
        django_get_or_create = ("cor",)

    nome = Sequence(lambda n: f"Recurso {n}")
    nome_exibicao = Sequence(lambda n: f"R{n}")
    cor = Iterator([c for c, _ in Recurso.CorChoices.choices])
    legado = False

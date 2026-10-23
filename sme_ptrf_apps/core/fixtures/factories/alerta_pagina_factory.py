from datetime import date

from factory import Sequence, SubFactory, post_generation
from factory.django import DjangoModelFactory
from faker import Faker

from sme_ptrf_apps.core.fixtures.factories.recurso_factory import RecursoFactory
from sme_ptrf_apps.core.models import AlertaPagina
from sme_ptrf_apps.core.choices import AlertaPaginaCategoriaChoices

fake = Faker("pt_BR")


class AlertaPaginaFactory(DjangoModelFactory):
    class Meta:
        model = AlertaPagina

    texto = Sequence(lambda n: f"<p>{fake.text(max_nb_chars=100)}</p>")
    categoria = AlertaPaginaCategoriaChoices.AVISO_REMOCAO_PRESIDENTE
    data_disparo = date(2026, 11, 15)
    recurso = SubFactory(RecursoFactory)
    ativo = True
    enviar_email = False
    assunto_email = ""

    @post_generation
    def grupos_email(self, create, extraidos, **kwargs):
        if create and extraidos:
            self.grupos_email.set(extraidos)

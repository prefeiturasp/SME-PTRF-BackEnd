from factory import DjangoModelFactory, SubFactory
from faker import Faker
from sme_ptrf_apps.users.models import UnidadeEmSuporte
from sme_ptrf_apps.core.fixtures.factories.unidade_factory import UnidadeFactory
from sme_ptrf_apps.users.fixtures.factories.usuario_factory import UsuarioFactory

fake = Faker("pt_BR")


class UnidadeEmSuporteFactory(DjangoModelFactory):
    class Meta:
        model = UnidadeEmSuporte

    unidade = SubFactory(UnidadeFactory)
    user = SubFactory(UsuarioFactory)

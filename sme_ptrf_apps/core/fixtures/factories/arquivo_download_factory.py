from factory import DjangoModelFactory, SubFactory, Sequence
from faker import Faker
from sme_ptrf_apps.core.models import (
    ArquivoDownload
)
from sme_ptrf_apps.users.fixtures.factories import UsuarioFactory

fake = Faker("pt_BR")


class ArquivoDownloadFactory(DjangoModelFactory):
    class Meta:
        model = ArquivoDownload

    identificador = Sequence(lambda n: fake.unique.word())
    informacoes = Sequence(lambda n: fake.name())
    arquivo = None
    status = ArquivoDownload.STATUS_CONCLUIDO
    msg_erro = ''
    lido = False
    usuario = SubFactory(UsuarioFactory)

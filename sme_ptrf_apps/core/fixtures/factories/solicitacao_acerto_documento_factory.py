import factory
from sme_ptrf_apps.core.models.solicitacao_acerto_documento import SolicitacaoAcertoDocumento
from .analise_documento_prestacao_conta_factory import AnaliseDocumentoPrestacaoContaFactory
from .tipo_acerto_documento_factory import TipoAcertoDocumentoFactory


class SolicitacaoAcertoDocumentoFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = SolicitacaoAcertoDocumento

    analise_documento = factory.SubFactory(AnaliseDocumentoPrestacaoContaFactory)
    tipo_acerto = factory.SubFactory(TipoAcertoDocumentoFactory)

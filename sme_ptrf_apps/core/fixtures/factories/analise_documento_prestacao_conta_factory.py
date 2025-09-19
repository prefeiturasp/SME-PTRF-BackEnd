import factory
from factory.django import DjangoModelFactory
from sme_ptrf_apps.core.models.analise_documento_prestacao_conta import AnaliseDocumentoPrestacaoConta
from .analise_prestacao_conta_factory import AnalisePrestacaoContaFactory
from .tipo_documento_prestacao_conta_factory import TipoDocumentoPrestacaoContaFactory


class AnaliseDocumentoPrestacaoContaFactory(DjangoModelFactory):
    class Meta:
        model = AnaliseDocumentoPrestacaoConta

    analise_prestacao_conta = factory.SubFactory(AnalisePrestacaoContaFactory)
    tipo_documento_prestacao_conta = factory.SubFactory(TipoDocumentoPrestacaoContaFactory)
    resultado = AnaliseDocumentoPrestacaoConta.RESULTADO_AJUSTE
    status_realizacao = AnaliseDocumentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE

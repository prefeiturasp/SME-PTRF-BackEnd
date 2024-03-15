import factory

from sme_ptrf_apps.core.models.solicitacao_acerto_lancamento import SolicitacaoAcertoLancamento
from .analise_lancamento_prestacao_conta_factory import AnaliseLancamentoPrestacaoContaFactory
from .tipo_acerto_lancamento_factory import TipoAcertoLancamentoFactory

class SolicitacaoAcertoLancamentoFactory(factory.django.DjangoModelFactory):
    
    class Meta:
        model = SolicitacaoAcertoLancamento
        
    analise_lancamento = factory.SubFactory(AnaliseLancamentoPrestacaoContaFactory)
    tipo_acerto = factory.SubFactory(TipoAcertoLancamentoFactory)
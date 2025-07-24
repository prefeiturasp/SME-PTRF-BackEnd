import factory
from factory.django import DjangoModelFactory
from sme_ptrf_apps.core.models.analise_lancamento_prestacao_conta import AnaliseLancamentoPrestacaoConta
from .analise_prestacao_conta_factory import AnalisePrestacaoContaFactory


class AnaliseLancamentoPrestacaoContaFactory(DjangoModelFactory):
    class Meta:
        model = AnaliseLancamentoPrestacaoConta

    analise_prestacao_conta = factory.SubFactory(AnalisePrestacaoContaFactory)
    tipo_lancamento = AnaliseLancamentoPrestacaoConta.TIPO_LANCAMENTO_GASTO
    resultado = AnaliseLancamentoPrestacaoConta.RESULTADO_AJUSTE
    status_realizacao = AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE
    devolucao_tesouro_atualizada = False
    lancamento_atualizado = False
    lancamento_excluido = False
    conciliacao_atualizada = False
    houve_considerados_corretos_automaticamente = False

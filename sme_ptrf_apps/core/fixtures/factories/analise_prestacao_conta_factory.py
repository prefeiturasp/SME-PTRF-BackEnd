from datetime import datetime
from factory import DjangoModelFactory, SubFactory, LazyAttribute
from faker import Faker
from sme_ptrf_apps.core.models.analise_prestacao_conta import AnalisePrestacaoConta
from .prestacao_conta_factory import PrestacaoContaFactory
fake = Faker("pt_BR")


class AnalisePrestacaoContaFactory(DjangoModelFactory):
    class Meta:
        model = AnalisePrestacaoConta

    prestacao_conta = SubFactory(PrestacaoContaFactory)
    status = LazyAttribute(lambda x: fake.random_element(
        elements=[choice[0] for choice in AnalisePrestacaoConta.STATUS_CHOICES]))
    status_versao = LazyAttribute(lambda x: fake.random_element(
        elements=[choice[0] for choice in AnalisePrestacaoConta.STATUS_CHOICES_VERSAO]))
    versao = LazyAttribute(lambda x: fake.random_element(
        elements=[choice[0] for choice in AnalisePrestacaoConta.VERSAO_CHOICES]))
    arquivo_pdf_criado_em = datetime.now()
    status_versao_apresentacao_apos_acertos = LazyAttribute(lambda x: fake.random_element(
        elements=[choice[0] for choice in AnalisePrestacaoConta.STATUS_CHOICES_VERSAO]))
    versao_pdf_apresentacao_apos_acertos = LazyAttribute(lambda x: fake.random_element(
        elements=[choice[0] for choice in AnalisePrestacaoConta.VERSAO_CHOICES]))
    arquivo_pdf_apresentacao_apos_acertos_criado_em = datetime.now()

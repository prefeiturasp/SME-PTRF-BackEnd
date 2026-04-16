from factory import Sequence, SubFactory
from factory.django import DjangoModelFactory

from sme_ptrf_apps.core.fixtures.factories.periodo_factory import PeriodoFactory
from sme_ptrf_apps.core.fixtures.factories.unidade_factory import DreFactory
from sme_ptrf_apps.dre.models import ConsolidadoDRE


class ConsolidadoDREFactory(DjangoModelFactory):
    class Meta:
        model = ConsolidadoDRE

    dre = SubFactory(DreFactory)
    periodo = SubFactory(PeriodoFactory)
    eh_parcial = True
    sequencia_de_publicacao = Sequence(lambda n: n + 1)
    status = ConsolidadoDRE.STATUS_GERADOS_PARCIAIS
    versao = ConsolidadoDRE.VERSAO_FINAL
    status_sme = ConsolidadoDRE.STATUS_SME_NAO_PUBLICADO
    sequencia_de_retificacao = 0

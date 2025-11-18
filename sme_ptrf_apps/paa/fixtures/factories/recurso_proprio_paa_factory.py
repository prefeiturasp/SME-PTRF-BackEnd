from factory import SubFactory
from factory.django import DjangoModelFactory
from sme_ptrf_apps.paa.models import RecursoProprioPaa
from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory
from sme_ptrf_apps.paa.fixtures.factories.fonte_recurso_paa_factory import FonteRecursoPaaFactory
from sme_ptrf_apps.paa.fixtures.factories import PaaFactory


class RecursoProprioPaaFactory(DjangoModelFactory):
    class Meta:
        model = RecursoProprioPaa

    paa = SubFactory(PaaFactory)
    fonte_recurso = SubFactory(FonteRecursoPaaFactory)
    associacao = SubFactory(AssociacaoFactory)

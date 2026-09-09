from factory import SubFactory
from factory.django import DjangoModelFactory
from sme_ptrf_apps.paa.models import LogReplicaPaa
from sme_ptrf_apps.paa.fixtures.factories.paa import PaaFactory


class LogReplicaPaaFactory(DjangoModelFactory):
    class Meta:
        model = LogReplicaPaa

    paa = SubFactory(PaaFactory)

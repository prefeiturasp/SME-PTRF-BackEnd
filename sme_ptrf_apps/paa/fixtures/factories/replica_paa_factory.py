from factory import SubFactory
from factory.django import DjangoModelFactory
from sme_ptrf_apps.paa.models import ReplicaPaa
from sme_ptrf_apps.paa.fixtures.factories.paa import PaaFactory


class ReplicaPaaFactory(DjangoModelFactory):
    class Meta:
        model = ReplicaPaa

    paa = SubFactory(PaaFactory)
    historico = {
        'texto_introducao': '',
        'texto_conclusao': '',
        'objetivos': {},
        'receitas_ptrf': {},
        'receitas_pdde': {},
        'receitas_outros_recursos': {},
        'prioridades': {},
    }

from factory import DjangoModelFactory, SubFactory

from sme_ptrf_apps.core.models import RecursoProprioPaa
from .associacao_factory import AssociacaoFactory
from .fonte_recurso_paa_factory import FonteRecursoPaaFactory


class RecursoProprioPaaFactory(DjangoModelFactory):
    class Meta:
        model = RecursoProprioPaa
    
    fonte_recurso = SubFactory(FonteRecursoPaaFactory)
    associacao = SubFactory(AssociacaoFactory)

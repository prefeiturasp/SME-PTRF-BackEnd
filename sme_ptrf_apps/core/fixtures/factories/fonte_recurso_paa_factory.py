from factory import DjangoModelFactory, Sequence, SubFactory
from sme_ptrf_apps.core.models import FonteRecursoPaa


class FonteRecursoPaaFactory(DjangoModelFactory):
    class Meta:
        model = FonteRecursoPaa


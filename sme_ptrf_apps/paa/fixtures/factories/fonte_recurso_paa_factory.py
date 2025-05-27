from factory import DjangoModelFactory
from sme_ptrf_apps.paa.models import FonteRecursoPaa


class FonteRecursoPaaFactory(DjangoModelFactory):
    class Meta:
        model = FonteRecursoPaa

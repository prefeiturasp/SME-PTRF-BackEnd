from sme_ptrf_apps.paa.models import Paa, PeriodoPaa
from sme_ptrf_apps.paa.enums import PaaStatusEnum


class PeriodoPaaService:
    def __init__(self, periodo_paa: PeriodoPaa):
        self.periodo_paa = periodo_paa

    def existe_paas_gerados_no_periodo(self) -> bool:
        return Paa.objects.filter(
            periodo_paa=self.periodo_paa, status=PaaStatusEnum.GERADO.name).exists()

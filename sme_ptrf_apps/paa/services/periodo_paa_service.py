from sme_ptrf_apps.paa.models import Paa, PeriodoPaa


class PeriodoPaaService:
    def __init__(self, periodo_paa: PeriodoPaa):
        self.periodo_paa = periodo_paa

    def existe_paas_gerados_no_periodo(self) -> bool:
        return Paa.objects.filter(
            periodo_paa=self.periodo_paa
        ).paas_gerados().exists()

from sme_ptrf_apps.paa.models import Paa, PeriodoPaa


class PeriodoPaaService:
    def __init__(self, periodo_paa: PeriodoPaa) -> None:
        """Inicializa o service com o período PAA fornecido."""
        self.periodo_paa = periodo_paa

    def existe_paas_gerados_no_periodo(self) -> bool:
        """Verifica se existem PAAs gerados no período."""
        return Paa.objects.filter(
            periodo_paa=self.periodo_paa
        ).paas_gerados().exists()

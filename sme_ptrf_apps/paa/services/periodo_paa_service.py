from sme_ptrf_apps.paa.models import Paa, PeriodoPaa


class PeriodoPaaService:
    def __init__(self, periodo_paa: PeriodoPaa) -> None:
        """Inicializa o service com o período PAA fornecido.

        Args:
            periodo_paa: Período PAA que será utilizado pelo service.
        """
        self.periodo_paa = periodo_paa

    def existe_paas_gerados_no_periodo(self) -> bool:
        """Verifica se existem PAAs gerados no período.

        Returns:
            True se houver ao menos um PAA gerado associado ao período,
            False caso contrário.
        """
        return Paa.objects.filter(
            periodo_paa=self.periodo_paa
        ).paas_gerados().exists()

from datetime import date

from sme_ptrf_apps.paa.models import ParametroPaa


class PaaService:

    @classmethod
    def pode_elaborar_novo_paa(cls):

        mes_atual = date.today().month
        param_paa = ParametroPaa.get()
        assert mes_atual >= param_paa.mes_elaboracao_paa, "Mês não liberado para Elaboração de novo PAA."

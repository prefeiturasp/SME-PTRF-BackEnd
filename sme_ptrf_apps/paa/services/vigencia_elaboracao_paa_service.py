from datetime import date

from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.paa import constantes
from sme_ptrf_apps.paa.models import PeriodoPaa, Paa, ParametroPaa


class VigenciaElaboracaoPaaService:
    """Reúne os critérios usados pelo frontend para deciir o estado do botão de elaboração do PAA"""

    @classmethod
    def obter(cls, associacao: Associacao, proxima_vigencia_habilitada: bool, hoje: date | None = None) -> dict:
        """Retorna as vigências de elaboração da Associação

        Args:
            associacao: Associação consultada.
            proxima_vigencia_habilitada: Se a flag do PAA da próxima vigência foi habilitada.
            hoje: Data de referência.

        Returns:
            Dicionário com as props:
             - `hoje`
             - `mes_elaboracao_paa`
             - `proxima_vigencia_habilitada`
             - `periodos_sobrepostos`
             - `status_vigente_exigidos_para_proxima_vigencia`
             - `periodos`
             Cada Período traz o resumo do PAA da associação ou None se ainda não.
        """
        hoje = hoje or date.today()
        periodos = list(PeriodoPaa.relevantes_para(associacao, hoje))
        vigente, proxima = PeriodoPaa.vigente_e_proxima_vigencia_em(hoje)
        paas_por_periodo = cls._paas_por_periodo(associacao, periodos)

        return {
            "hoje": hoje,
            "mes_elaboracao_paa": ParametroPaa.get().mes_elaboracao_paa,
            "proxima_vigencia_habilitada": proxima_vigencia_habilitada,
            "periodos_sobrepostos": PeriodoPaa.tem_sobreposicao_relevante(hoje),
            "status_vigente_exigidos_para_proxima_vigencia": (
                constantes.STATUS_VIGENTE_EXIGIDOS_PARA_INICIAR_PROXIMA_VIGENCIA
            ),
            "periodos": [
                {
                    "uuid": periodo.uuid,
                    "referencia": periodo.referencia,
                    "data_inicial": periodo.data_inicial,
                    "data_final": periodo.data_final,
                    "vigencia": PeriodoPaa.classificar_vigencia(periodo, vigente, proxima, hoje),
                    "paa": cls._resumo_paa(paas_por_periodo.get(periodo.pk)),
                }
                for periodo in periodos
            ],
        }

    @staticmethod
    def _paas_por_periodo(associacao: Associacao, periodos: list) -> dict[int, Paa | None]:
        """Mapeia o id do período para o PAA da Associação, em uma única lista.

        Args:
            associacao: Associação.
            periodos: Lista de períodos relevantes.

        Returns:
            Dicionário com os PAA por período.
            [{ <id>: <paa> }, ...]
        """
        paas = Paa.objects.filter(associacao=associacao, periodo_paa__in=periodos)
        return {paa.periodo_paa_id: paa for paa in paas}

    @staticmethod
    def _resumo_paa(paa: Paa | None) -> dict | None:
        if not paa:
            return None
        return {
            "uuid": paa.uuid,
            "status": paa.status,
            "status_andamento": paa.get_status_andamento(),
        }

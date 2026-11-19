from sme_ptrf_apps.paa.enums import PaaStatusAndamentoEnum
from sme_ptrf_apps.paa.models import Paa, PeriodoPaa


class PaaAnteriorService:
    """Situação do PAA do período imediatamente anterior e a verificação das exigências parametrizadas sobre ele."""

    @classmethod
    def paa_do_periodo_anterior(cls, paa: Paa) -> Paa | None:
        """Retorna o PAA da mesma associação no período imediatamente anterior ao do PAA, se existir."""
        if not paa.periodo_paa_id or not paa.associacao_id:
            return None

        periodo_anterior = PeriodoPaa.anterior_a(paa.periodo_paa)
        if not periodo_anterior:
            return None

        return Paa.objects.filter(
            associacao_id=paa.associacao_id,
            periodo_paa=periodo_anterior
        ).first()

    @classmethod
    def situacao_do_paa_anterior(cls, paa: Paa) -> str | None:
        """Retorna a situação do PAA anterior (`status_andamento`), ou `None` se não houver PAA anterior."""
        paa_anterior = cls.paa_do_periodo_anterior(paa)
        if not paa_anterior:
            return None

        if paa_anterior.status_em_retificacao:
            return PaaStatusAndamentoEnum.EM_RETIFICACAO.name

        return paa_anterior.get_status_andamento()

    @classmethod
    def atende_exigencia(cls, paa: Paa, situacoes_exigidas: list[str] | None) -> bool:
        """Informa se o PAA anterior está em uma das situações exigidas.

        Não há o que exigir quando a exigência é `None` ou quando não existe PAA anterior.
        """
        if situacoes_exigidas is None:
            return True

        situacao = cls.situacao_do_paa_anterior(paa)
        return situacao is None or situacao in situacoes_exigidas

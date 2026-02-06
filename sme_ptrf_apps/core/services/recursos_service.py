from waffle import get_waffle_flag_model
from sme_ptrf_apps.core.models import Recurso, PeriodoInicialAssociacao
flags = get_waffle_flag_model()


class RecursoService:

    @staticmethod
    def _recursos_base(queryset):
        flag_premio_ativa = flags.objects.filter(name='premio-excelencia', everyone=True).exists()

        recurso_ids = queryset.values_list("recurso_id", flat=True)

        if flag_premio_ativa:
            return (
                Recurso.objects
                .filter(id__in=recurso_ids, ativo=True)
                .distinct()
                .order_by("nome")
            )
        else:
            return Recurso.objects.none()

    @classmethod
    def por_associacao(cls, unidade):
        periodo = PeriodoInicialAssociacao.objects.filter(
            associacao__unidade=unidade
        )

        return cls._recursos_base(periodo)

    @classmethod
    def por_dre(cls, unidade):
        periodo = PeriodoInicialAssociacao.objects.filter(
            associacao__unidade__dre=unidade
        )

        return cls._recursos_base(periodo)

    @classmethod
    def disponiveis_para_unidade(cls, unidade):
        if unidade.tipo_unidade == "DRE":
            return cls.por_dre(unidade)

        return cls.por_associacao(unidade)

from django.db import transaction
from django.db.models import QuerySet, F
from sme_ptrf_apps.paa.models.atividade_estatutaria import AtividadeEstatutaria


class AtividadeEstatutariaOrdenacaoService:

    @classmethod
    def realiza_ordenacao(cls, queryset: QuerySet[AtividadeEstatutaria]) -> None:
        """
            Garante que TODOS os registros possuam ordem válida.
            Executa apenas uma vez quando necessário.
        """
        total = queryset.count()
        com_ordem = queryset.filter(ordem__gt=0).count()

        if total == com_ordem and total > 0:
            return

        with transaction.atomic():
            for index, atividade in enumerate(
                queryset.order_by('mes', 'nome')
            ):
                atividade.ordem = index + 1
                atividade.save(update_fields=['ordem'])

    @classmethod
    def obter_queryset_ordenado(cls) -> QuerySet[AtividadeEstatutaria]:
        queryset = AtividadeEstatutaria.objects.filter(
            paa__isnull=True
        )

        cls.realiza_ordenacao(queryset)
        return queryset.order_by('ordem')

    @classmethod
    def mover(
        cls,
        uuid_origem: str,
        uuid_destino: str,
    ) -> None:
        with transaction.atomic():
            origem = AtividadeEstatutaria.objects.select_for_update().get(
                uuid=uuid_origem
            )
            destino = AtividadeEstatutaria.objects.select_for_update().get(
                uuid=uuid_destino
            )

            if origem.uuid == destino.uuid:
                return

            ordem_origem = origem.ordem
            ordem_destino = destino.ordem

            if ordem_origem < ordem_destino:
                AtividadeEstatutaria.objects.filter(
                    ordem__gt=ordem_origem,
                    ordem__lte=ordem_destino,
                ).exclude(uuid=origem.uuid).update(
                    ordem=F('ordem') - 1
                )
            else:
                AtividadeEstatutaria.objects.filter(
                    ordem__gte=ordem_destino,
                    ordem__lt=ordem_origem,
                ).exclude(uuid=origem.uuid).update(
                    ordem=F('ordem') + 1
                )

            origem.ordem = ordem_destino
            origem.save(update_fields=['ordem'])

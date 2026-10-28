import datetime

from django.db import models
from django.db.models import Q


class AtaPaaQuerySet(models.QuerySet):
    """QuerySet customizado para operações na tabela de Atas do PAA."""

    def com_data_reuniao_na_data_entre(
            self,
            data_inicio_no_cargo: datetime.date,
            data_fim_no_cargo: datetime.date
    ) -> models.QuerySet:
        """Filtra as atas não geradas cujas reuniões ocorreram no intervalo de mandato do cargo.

        Args:
            data_inicio_no_cargo (datetime.date): Data de início do período.
            data_fim_no_cargo (datetime.date): Data de término do período.

        Returns:
            models.QuerySet: Um novo QuerySet contendo apenas as atas que atendem
                ao critério de intervalo de datas estabelecido.
        """
        return self.filter(
            Q(data_reuniao__gte=data_inicio_no_cargo),
            Q(data_reuniao__lte=data_fim_no_cargo),
            status_geracao_pdf=self.model.STATUS_NAO_GERADO,
        )


class AtaPaaManager(models.Manager.from_queryset(AtaPaaQuerySet)):
    """Manager que expõe os métodos do AtaPaaQuerySet diretamente em AtaPaa.objects."""

from datetime import date
from typing import Optional

from django.db.models import Q

from sme_ptrf_apps.core.models import Associacao
from ..models import Mandato


class ServicoMandatoVigenteVacancia:
    """Resolve o mandato vigente na data atual (Histórico de Membros v2)."""

    def get_mandato_vigente(self) -> Optional[Mandato]:
        """Retorna o mandato que cobre hoje (o mais recente, se houver mais de um), ou None."""
        data_atual = date.today()

        # Filtrar os mandatos com data_inicial anterior ou igual à data atual
        qs = Mandato.objects.filter(data_inicial__lte=data_atual)

        # Filtrar os mandatos com data_final posterior ou igual à data atual OU sem data_final definida
        qs = qs.filter(Q(data_final__gte=data_atual) | Q(data_final__isnull=True))

        # Verificar se há mais de um mandato vigente, e caso haja, retornar o último (o mais recente)
        mandato_vigente = qs.last()

        return mandato_vigente


class ServicoMandatoVacancia:
    """Consultas sobre a ordem cronológica dos mandatos e pendências do vigente (v2)."""

    def get_mandato_mais_recente(self) -> Optional[Mandato]:
        """Retorna o mandato de data_inicial mais recente, ou None se não houver nenhum."""
        try:
            return Mandato.objects.latest('data_inicial')
        except Mandato.DoesNotExist:
            return None

    def get_mandato_anterior_ao_mais_recente(self) -> Optional[Mandato]:
        """Retorna o segundo mandato mais recente por data_inicial, ou None."""
        mandato_mais_recente = self.get_mandato_mais_recente()
        if mandato_mais_recente:
            try:
                return Mandato.objects.all().exclude(uuid=mandato_mais_recente.uuid).latest('data_inicial')
            except Mandato.DoesNotExist:
                return None
        return None

    def retorna_se_mandato_vigente_tem_pendencia(self, associacao: Associacao) -> bool:
        """Retorna True se a associação não tem nenhum cargo ocupado no mandato vigente.

        Sem mandato vigente, retorna False (não há pendência a apurar).

        Args:
            associacao: associação a verificar.
        """
        from ..models import CargoComposicaoVacancia

        service = ServicoMandatoVigenteVacancia()
        mandato_vigente = service.get_mandato_vigente()

        if not mandato_vigente:
            return False

        cargos = CargoComposicaoVacancia.objects.filter(
            composicao__mandato=mandato_vigente,
            composicao__associacao=associacao,
            ocupante_do_cargo__isnull=False
        )

        return not cargos.exists()

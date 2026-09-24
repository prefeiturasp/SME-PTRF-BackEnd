import logging
from typing import Any

from sme_ptrf_apps.paa.models import Paa

logger = logging.getLogger(__name__)


class PlanoAplicacaoService:
    """Service para agregar e formatar dados do Plano de Aplicação"""
    # Grupos que devem constar no plano de aplicação
    _GRUPOS = [
        # (key, titulo, eh_prioridade, recursos, eh_outros_recursos)
        ('prioridades-ptrf',                'Prioridades PTRF',                True,  ('PTRF',),                           False),  # noqa
        ('prioridades-pdde',                'Prioridades PDDE',                True,  ('PDDE',),                           False),  # noqa
        ('prioridades-outros-recursos',     'Prioridades Outros Recursos',     True,  ('RECURSO_PROPRIO', 'OUTRO_RECURSO'), True),  # noqa
        ('nao-prioridades-ptrf',            'Não Prioridades PTRF',            False, ('PTRF',),                           False),  # noqa
        ('nao-prioridades-pdde',            'Não Prioridades PDDE',            False, ('PDDE',),                           False),  # noqa
        ('nao-prioridades-outros-recursos', 'Não Prioridades Outros Recursos', False, ('RECURSO_PROPRIO', 'OUTRO_RECURSO'), True),  # noqa
    ]

    def __init__(self, paa: Paa, usuario: Any | None = None) -> None:
        """Inicializa o service com o PAA e o usuário opcional.

        Args:
            paa: PAA que será utilizado para construir o plano de aplicação.
            usuario: Usuário associado à requisição, usado para identificar
                alterações da retificação. Padrão None.
        """
        self.paa = paa
        self.usuario = usuario

    def _obter_alteracoes(self) -> dict:
        """Retorna alterações do PAA em relação ao snapshot da retificação (com cache por instância).

        Returns:
            Dicionário com as alterações identificadas pelo
            RetificacaoPaaService, ou um dicionário vazio caso ocorra
            algum erro ao obtê-las.
        """
        if not hasattr(self, '_alteracoes_cache'):
            from sme_ptrf_apps.paa.services.retificacao_paa_service import RetificacaoPaaService
            try:
                self._alteracoes_cache = RetificacaoPaaService(self.paa, self.usuario).identificar_alteracoes()
            except Exception as e:
                logger.warning(f"Erro ao obter alterações do PAA {self.paa.uuid}: {str(e)}")
                self._alteracoes_cache = {}
        return self._alteracoes_cache

    def _obter_prioridades_serializadas(self) -> list:
        """Obtém todas as prioridades do PAA serializadas com contexto de alterações.

        Returns:
            Lista de prioridades do PAA serializadas por
            PrioridadePaaListSerializer, com o contexto de alterações da
            retificação incluído.
        """
        from sme_ptrf_apps.paa.api.serializers.prioridade_paa_serializer import PrioridadePaaListSerializer
        from sme_ptrf_apps.paa.models import PrioridadePaa
        from sme_ptrf_apps.paa.querysets import queryset_prioridades_paa

        qs = queryset_prioridades_paa(PrioridadePaa.objects.filter(paa=self.paa))
        return PrioridadePaaListSerializer(
            qs,
            many=True,
            context={'alteracoes': self._obter_alteracoes()},
        ).data

    def _construir_grupo(self, key: str, titulo: str, itens: list, eh_outros_recursos: bool = False) -> dict:
        """Constrói um grupo com seus itens e a linha de total.

        Args:
            key: Identificador único do grupo.
            titulo: Título de exibição do grupo.
            itens: Lista de prioridades pertencentes ao grupo.
            eh_outros_recursos: Indica se o grupo representa recursos
                próprios ou outros recursos. Padrão False.

        Returns:
            Dicionário com a chave, o título, a flag de outros recursos e
            os dados do grupo (itens mais a linha de total).
        """
        total_do_grupo = sum(float(p['valor_total']) for p in itens if p['valor_total'] is not None)

        # Adiciona a linha de total dos itens
        dados = [
            *itens,
            {
                'key': f'{key}-total',
                'isTotal': True,
                'valor_total': total_do_grupo
            },
        ]
        return {
            'key': key,
            'titulo': titulo,
            'ehOutrosRecursos': eh_outros_recursos,
            'dados': dados,
        }

    def construir_plano_aplicacao(self) -> list:
        """Constrói o plano de aplicação completo com grupos prontos para renderização.

        Returns:
            Lista de grupos (dicionários) contendo os itens de cada grupo
            e a respectiva linha de total, na ordem definida por
            `_GRUPOS`. Grupos sem itens são omitidos.
        """
        prioridades = self._obter_prioridades_serializadas()

        grupos = []
        for key, titulo, eh_prioridade, recursos, eh_outros_recursos in self._GRUPOS:
            itens = [p for p in prioridades if bool(p['prioridade']) == eh_prioridade and p['recurso'] in recursos]
            if itens:
                grupos.append(self._construir_grupo(key, titulo, itens, eh_outros_recursos))

        return grupos

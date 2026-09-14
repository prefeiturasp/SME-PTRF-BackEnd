from enum import Enum
from typing import List
from sme_ptrf_apps.paa.models import Paa
from rest_framework.exceptions import APIException


class TipoBloqueioPaa(Enum):
    """Define as condições usadas para bloquear alterações em um PAA."""

    STATUS_GERADO = "status_gerado"
    ATA_CONCLUIDA = "ata_concluida"


class PaaStatusBloqueiaAlteracaoException(APIException):
    """Exceção retornada quando uma alteração do PAA é bloqueada."""

    status_code = 400

    def __init__(self, mensagem: str) -> None:
        """Inicializa a exceção com a mensagem exibida na resposta da API.

        Args:
            mensagem: Mensagem que explica o motivo do bloqueio.
        """
        self.detail = {
            "mensagem": mensagem
        }


class PaaStatusBloqueiaAlteracaoService:
    """
    Service utilizado para bloquear alterações quando o PAA já tem Documento Final
    Nesta condição, é possível permitir o preenchimento de Atas de Apresentação/Retificação
    """

    @classmethod
    def checar_status_gerado_ou_doc_concluido(cls, paa: Paa) -> None:
        """Bloqueia edições em PAA com documento final.

        Args:
            paa: PAA que será validado.

        Raises:
            PaaStatusBloqueiaAlteracaoException: Se o PAA estiver gerado ou
                possuir documento final concluído.
        """
        if paa.status_gerado:
            raise PaaStatusBloqueiaAlteracaoException(
                'O PAA já foi gerado. Para realizar alterações, '
                'utilize o fluxo de retificação do PAA.'
            )

        if cls.checar_documento_concluido(paa):
            raise PaaStatusBloqueiaAlteracaoException((
                'O Documento Final do PAA já foi gerado. Para realizar alterações, '
                'utilize o fluxo de retificação do PAA.'
            ))

    @classmethod
    def checar_ata_concluida(cls, paa: Paa) -> None:
        """Bloqueia alterações quando a ata final do PAA foi concluída.

        Args:
            paa: PAA que será validado.

        Raises:
            PaaStatusBloqueiaAlteracaoException: Se a ata final estiver
                concluída.
        """
        if paa.status_em_retificacao:
            from sme_ptrf_apps.paa.services.ciclo_retificacao_service import CicloRetificacaoService
            tem_ata = CicloRetificacaoService(paa).tem_ata_concluida
        else:
            tem_ata = paa.get_tem_ata_concluida()

        if tem_ata:
            raise PaaStatusBloqueiaAlteracaoException(
                'A Ata Final do PAA já foi concluida. '
                'Para realizar alterações, utilize o fluxo de retificação.'
            )

    @classmethod
    def checar_documento_concluido(cls, paa: Paa) -> bool:
        """Verifica se o documento final do PAA está concluído.

        Args:
            paa: PAA que será consultado.

        Returns:
            True se o documento final estiver concluído; caso contrário, False.
        """
        if paa.status_em_retificacao:
            from sme_ptrf_apps.paa.services.ciclo_retificacao_service import CicloRetificacaoService
            tem_doc = CicloRetificacaoService(paa).tem_documento_final_concluido
        else:
            tem_doc = paa.get_tem_documento_final_concluido()

        return tem_doc

    @classmethod
    def validar_lista(cls, paas: List[Paa], tipo_bloqueio: TipoBloqueioPaa) -> None:
        """Valida uma lista de Paas dado um tipo bloqueio informado.

        Args:
            paas: PAAs que serão validados.
            tipo_bloqueio: Regra de bloqueio que será aplicada.

        Raises:
            PaaStatusBloqueiaAlteracaoException: Se algum PAA violar a regra
                selecionada.
        """
        for paa in paas:

            if tipo_bloqueio == TipoBloqueioPaa.STATUS_GERADO:
                cls.checar_status_gerado_ou_doc_concluido(paa)

            elif tipo_bloqueio == TipoBloqueioPaa.ATA_CONCLUIDA:
                cls.checar_ata_concluida(paa)

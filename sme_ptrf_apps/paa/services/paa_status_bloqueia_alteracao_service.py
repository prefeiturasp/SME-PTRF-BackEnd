from enum import Enum
from typing import List
from sme_ptrf_apps.paa.models import Paa
from rest_framework.exceptions import APIException


class TipoBloqueioPaa(Enum):
    STATUS_GERADO = "status_gerado"
    ATA_CONCLUIDA = "ata_concluida"


class PaaStatusBloqueiaAlteracaoException(APIException):
    status_code = 400

    def __init__(self, mensagem):
        self.detail = {
            "mensagem": mensagem
        }


class PaaStatusBloqueiaAlteracaoService:
    """
    Service utilizado para bloquear alterações quando o PAA já tem Documento Final
    Nesta condição, é possível permitir o preenchimento de Atas de Apresentação/Retificação
    """

    @classmethod
    def checar_status_gerado(cls, paa: Paa):
        """ Bloqueia edições em PAA com documento final. """
        if paa.status_gerado:
            raise PaaStatusBloqueiaAlteracaoException(
                'O PAA já foi gerado. Para realizar alterações, '
                'utilize o fluxo de retificação do PAA.'
            )

    @classmethod
    def checar_ata_concluida(cls, paa: Paa):
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
    def validar_lista(cls, paas: List[Paa], tipo_bloqueio: TipoBloqueioPaa):
        """
        Valida uma lista de Paas dado um tipo bloqueio informado
        """
        for paa in paas:

            if tipo_bloqueio == TipoBloqueioPaa.STATUS_GERADO:
                cls.checar_status_gerado(paa)

            elif tipo_bloqueio == TipoBloqueioPaa.ATA_CONCLUIDA:
                cls.checar_ata_concluida(paa)

from enum import Enum
from typing import List
from sme_ptrf_apps.paa.models import Paa
from rest_framework.exceptions import APIException


class TipoBloqueioPaa(Enum):
    DOCUMENTO_FINAL = "documento_final"
    STATUS_GERADO = "status_gerado"


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
    def checar_documento_final(cls, paa: Paa):
        if paa.documento_final:
            raise PaaStatusBloqueiaAlteracaoException(
                'O Documento Final do PAA já foi gerado. '
                'Para realizar alterações, utilize o fluxo de retificação.'
            )

    @classmethod
    def validar_lista(cls, paas: List[Paa], tipo_bloqueio: TipoBloqueioPaa):
        """
        Valida uma lista de Paas dado um tipo bloqueio informado
        """
        for paa in paas:
            if tipo_bloqueio == TipoBloqueioPaa.DOCUMENTO_FINAL:
                cls.checar_documento_final(paa)

            elif tipo_bloqueio == TipoBloqueioPaa.STATUS_GERADO:
                cls.checar_status_gerado(paa)

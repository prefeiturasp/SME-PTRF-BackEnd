from ..models.paa import Paa
from rest_framework.exceptions import ValidationError
from ..services.paa_status_bloqueia_alteracao_service import (
    PaaStatusBloqueiaAlteracaoService,
    TipoBloqueioPaa
)


class PaaBloqueiaAlteracaoMixin:
    """
    Mixin responsável por aplicar regras de bloqueio de alteração do PAA
    em ViewSets do DRF.
    """

    tipo_bloqueio_paa: TipoBloqueioPaa | None = None

    def get_paa(self):
        """
        Resolve o PAA dependendo do contexto:
        - CREATE: vem do request.data
        - OUTROS: vem do objeto
        """

        # CREATE (POST sem objeto ainda)
        if self.action == "create":
            paa_uuid = self.request.data.get("paa")

            if not paa_uuid:
                raise ValidationError({
                    "mensagem": "PAA não informado no payload."
                })

            paa = Paa.objects.filter(uuid=paa_uuid).first()

            if not paa:
                raise ValidationError({"mensagem": "PAA inválido"})

            return paa

        # UPDATE / DELETE / DETAIL
        return self.get_object().paa

    def validar_paa_permite_alteracao(self):
        if not self.tipo_bloqueio_paa:
            return  # se não configurou, não aplica regra

        paa = self.get_paa()

        if self.tipo_bloqueio_paa == TipoBloqueioPaa.DOCUMENTO_FINAL:
            PaaStatusBloqueiaAlteracaoService.checar_documento_final(paa)

        elif self.tipo_bloqueio_paa == TipoBloqueioPaa.STATUS_GERADO:
            PaaStatusBloqueiaAlteracaoService.checar_status_gerado(paa)

    def perform_create(self, serializer):
        self.validar_paa_permite_alteracao()
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        self.validar_paa_permite_alteracao()
        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        self.validar_paa_permite_alteracao()
        return super().perform_destroy(instance)

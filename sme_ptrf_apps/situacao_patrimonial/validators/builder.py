from typing import Any

from .context import BemProduzidoDtoContext


class BemProduzidoContextBuilder:
    """Constrói o BemProduzidoDtoContext a partir do objeto de negócio e do contexto de request."""

    @staticmethod
    def build(
        bem_produzido=None,
        validated_data: dict = None,
        recurso: str = None,
        associacao: Any = None,
        status: str = None,
        periodos: list = [],
        saldos: dict = None,
        observacoes: str = None,
    ) -> BemProduzidoDtoContext:

        validated_data = validated_data or {}

        def get(field: str):
            if field in validated_data:
                return validated_data[field]
            if bem_produzido is not None:
                return getattr(bem_produzido, field, None)
            return None

        return BemProduzidoDtoContext(
            is_create=bem_produzido is None,
            bem_produzido=bem_produzido,
            associacao=associacao or get("associacao"),
            status=status or get("status"),
            recurso=bem_produzido.recurso or get("recurso"),
            periodos=periodos,
            saldos=saldos or {},
            observacoes=observacoes or get("observacoes"),
        )

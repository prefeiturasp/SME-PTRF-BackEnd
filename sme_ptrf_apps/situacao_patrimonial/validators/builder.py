from .context import BemProduzidoDtoContext


class BemProduzidoContextBuilder:
    """Constrói o BemProduzidoDtoContext a partir do objeto de negócio e do contexto de request."""

    @staticmethod
    def build(
        bem_produzido=None,  # Instancia
        validated_data: dict = None,
        periodos: list = [],
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
            associacao=get("associacao"),
            status=get("status"),
            recurso=get("recurso"),
            periodos=periodos,
        )

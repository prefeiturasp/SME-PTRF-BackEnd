from .base import AbstractBemProduzidoValidator, SituacaoPatrimonialValidationError
from .context import BemProduzidoDtoContext


class BemProduzidoPossuiAssociacaoValidator(AbstractBemProduzidoValidator):
    """Exige que o bem produzido esteja vinculado a uma associação."""

    def validate(self, bem_produzido_context: BemProduzidoDtoContext) -> BemProduzidoDtoContext:
        if not bem_produzido_context.associacao:
            raise SituacaoPatrimonialValidationError({
                "titulo": "Bem produzido sem associação",
                "mensagem": "O bem produzido deve possuir uma associação.",
                "validator": self.__class__.__name__
            })

        return bem_produzido_context

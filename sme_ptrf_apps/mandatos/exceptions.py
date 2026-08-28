from typing import Union


class CargoComposicaoVacanciaValidationError(Exception):
    """ Erro de validação de negócio do histórico de cargos, desacoplado de DRF.

    Atributos:
        detail: mensagem de erro - string ou dict (formato aceito pelo
                `serializers.ValidationError` do DRF)
    """

    def __init__(self, detail: Union[str, dict]) -> None:
        self.detail = detail
        super().__init__(str(detail))

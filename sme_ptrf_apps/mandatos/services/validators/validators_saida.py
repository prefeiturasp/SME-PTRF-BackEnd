from datetime import date
from sme_ptrf_apps.mandatos.exceptions import CargoComposicaoVacanciaValidationError
from sme_ptrf_apps.mandatos.models import CargoComposicaoVacancia, Mandato


class ValidatorSaidaOcupanteVigente:
    """ Datas dentro do intervalo do mandato"""

    @staticmethod
    def validar(cargo_composicao_vacancia: CargoComposicaoVacancia) -> None:
        """ Para realizar a saída, a vacancia deve estar ocupada e vigente
        Ocupante preenchido e `data_fim_no_cargo` igual a `mandato.data_final`

        Args:
            cargo_composicao_vacancia: vacancia a ser validada

        Raises:
            CargoComposicaoVacanciaValidationError: se não há ocupante ou
            a data fim do cargo for diferente da data fim do mandato
        """
        if cargo_composicao_vacancia.ocupante_do_cargo_id is None or \
            cargo_composicao_vacancia.data_fim_no_cargo != cargo_composicao_vacancia.composicao.mandato.data_final:  # noqa
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "O registro informado não está ocupado e vigente."
            })


class ValidatorSaidaDataNaoPosteriorAoMandato:
    """ Valida que data não é posterior a hoje """

    @staticmethod
    def validar(data_saida: date, mandato: Mandato) -> None:
        """ Valida que data não é posterior ao Mandato

        Args:
            data_saida (date): data a ser validada
            mandato: mandato de referencia

        Raises:
            CargoComposicaoVacanciaValidationError
        """
        if data_saida > mandato.data_final:
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "Não é permitido informar data de saída posterior à data final do mandato."
            })


class ValidatorSaidaDataNaoAnteriorAoCargo:
    """ Valida que data não é anterior ao início do cargo """

    @staticmethod
    def validar(data_saida: date, cargo_composicao_vacancia: CargoComposicaoVacancia) -> None:
        """ Valida que data de saída não pode ser anterior à data inicial do cargo

        Args:
            data_saida (date): data a ser validada (Considerar D-N)
            cargo_composicao_vacancia: registro de vacancia

        Raises:
            CargoComposicaoVacanciaValidationError
        """
        if data_saida < cargo_composicao_vacancia.data_inicio_no_cargo:
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "A data de saída é anterior ou igual à data de início no cargo."
            })


class ValidatorSaidaDataNaoFutura:
    """ Valida que data não é futura """

    @staticmethod
    def validar(data_saida: date, mandato: Mandato) -> None:
        """ Valida que data de saída não é futura

        Args:
            data_saida (date): data a ser validada
            mandato: mandato de referencia

        Raises:
            CargoComposicaoVacanciaValidationError
        """
        data_futura = data_saida > date.today()
        data_difere_fim_mandato = data_saida != mandato.data_final
        if data_futura and data_difere_fim_mandato:
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "Não é permitido informar data futura."
            })


class ValidatorSaidaCancelarSaidaRegistroEncerrado:
    """ Só faz sentido cancelar a saída de um registro que de fato já saiu.
     não há nada a cancelar num registro que já está vigente. """

    @staticmethod
    def validar(cargo_composicao_vacancia: CargoComposicaoVacancia, mandato: Mandato) -> None:
        """
        Args:
            `cargo_composicao_vacancia`: registro cuja saída se deseja cancelar
            `mandato`: mandato de referencia

        Raises:
            CargoComposicaoVacanciaValidationError: se o registro já está vigente

        """
        if cargo_composicao_vacancia.data_fim_no_cargo == mandato.data_final:
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "Este registro está vigente, não há saída para cancelar."
            })


class ValidatorSaidaCancelarSaidaSemSucessor:
    """ não pode cancelar uma saída se já existe um sucessor direto (substituido_por preenchido)
        reativar o registro criaria dois ocupantes vigentes para o mesmo cargo, violando as regras de único registro

    """
    @staticmethod
    def validar(cargo_composicao_vacancia: CargoComposicaoVacancia) -> None:
        """
            Args:
                `cargo_composicao_vacancia`: registro do cargo

            Raises:
                CargoComposicaoVacanciaValidationError: se já existe substituido_por
        """
        if cargo_composicao_vacancia.substituido_por_id is not None:
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "Não é possível cancelar a saída, já existe um substituto registrado para este cargo."
            })

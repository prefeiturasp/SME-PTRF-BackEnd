from datetime import date

from sme_ptrf_apps.mandatos.exceptions import CargoComposicaoVacanciaValidationError
from sme_ptrf_apps.mandatos.models import CargoComposicaoVacancia, Mandato


class ValidatorSaidaOcupanteVigente:
    """Exige que o registro esteja ocupado e vigente para permitir a saída."""

    @staticmethod
    def validar(cargo_composicao_vacancia: CargoComposicaoVacancia) -> None:
        """Valida que o registro está ocupado e vigente.

        Vigente = ocupante preenchido e ``data_fim_no_cargo`` igual à ``data_final`` do mandato.

        Args:
            cargo_composicao_vacancia: registro a ser validado.

        Raises:
            CargoComposicaoVacanciaValidationError: se não há ocupante, ou se a data
                de fim do cargo difere da data de fim do mandato.
        """
        if cargo_composicao_vacancia.ocupante_do_cargo_id is None or \
            cargo_composicao_vacancia.data_fim_no_cargo != cargo_composicao_vacancia.composicao.mandato.data_final:  # noqa
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "O registro informado não está ocupado e vigente."
            })


class ValidatorSaidaDataNaoPosteriorAoMandato:
    """Exige que a data de saída não ultrapasse a data final do mandato."""

    @staticmethod
    def validar(data_saida: date, mandato: Mandato) -> None:
        """Valida que a data de saída não é posterior à data final do mandato.

        Args:
            data_saida: data a ser validada.
            mandato: mandato de referência.

        Raises:
            CargoComposicaoVacanciaValidationError: se ``data_saida`` for posterior a
                ``mandato.data_final``.
        """
        if data_saida > mandato.data_final:
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "Não é permitido informar data de saída posterior à data final do mandato."
            })


class ValidatorSaidaDataNaoAnteriorAoCargo:
    """Exige que a data de saída não seja anterior ao início do cargo."""

    @staticmethod
    def validar(data_saida: date, cargo_composicao_vacancia: CargoComposicaoVacancia) -> None:
        """Valida que a data de saída não é anterior à data inicial do cargo.

        Args:
            data_saida: data a ser validada (já considerando o D-N).
            cargo_composicao_vacancia: registro de vacância.

        Raises:
            CargoComposicaoVacanciaValidationError: se ``data_saida`` for anterior a
                ``data_inicio_no_cargo``.
        """
        if data_saida < cargo_composicao_vacancia.data_inicio_no_cargo:
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "A data de saída é anterior ou igual à data de início no cargo."
            })


class ValidatorSaidaDataNaoFutura:
    """Exige que a data de saída não seja futura."""

    @staticmethod
    def validar(data_saida: date, mandato: Mandato) -> None:
        """Valida que a data de saída não é futura.

        A data final do mandato é a única exceção: pode coincidir com uma data futura.

        Args:
            data_saida: data a ser validada.
            mandato: mandato de referência.

        Raises:
            CargoComposicaoVacanciaValidationError: se ``data_saida`` for posterior a
                hoje e diferente da data final do mandato.
        """
        data_futura = data_saida > date.today()
        data_difere_fim_mandato = data_saida != mandato.data_final
        if data_futura and data_difere_fim_mandato:
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "Não é permitido informar data futura."
            })


class ValidatorSaidaCancelarSaidaRegistroEncerrado:
    """Só permite cancelar a saída de um registro que de fato já saiu.

    Não há nada a cancelar num registro que ainda está vigente.
    """

    @staticmethod
    def validar(cargo_composicao_vacancia: CargoComposicaoVacancia, mandato: Mandato) -> None:
        """Valida que o registro está encerrado (já teve saída).

        Args:
            cargo_composicao_vacancia: registro cuja saída se deseja cancelar.
            mandato: mandato de referência.

        Raises:
            CargoComposicaoVacanciaValidationError: se o registro ainda está vigente
                (``data_fim_no_cargo`` igual à data final do mandato).
        """
        if cargo_composicao_vacancia.data_fim_no_cargo == mandato.data_final:
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "Este registro está vigente, não há saída para cancelar."
            })


class ValidatorSaidaCancelarSaidaSemSucessor:
    """Impede cancelar uma saída quando já existe um sucessor direto.

    Reativar o registro criaria dois ocupantes vigentes para o mesmo cargo, violando
    a regra de registro vigente único.
    """

    @staticmethod
    def validar(cargo_composicao_vacancia: CargoComposicaoVacancia) -> None:
        """Valida que o registro não tem sucessor direto vinculado.

        Args:
            cargo_composicao_vacancia: registro do cargo.

        Raises:
            CargoComposicaoVacanciaValidationError: se ``substituido_por`` estiver preenchido.
        """
        if cargo_composicao_vacancia.substituido_por_id is not None:
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "Não é possível cancelar a saída, já existe um substituto registrado para este cargo."
            })

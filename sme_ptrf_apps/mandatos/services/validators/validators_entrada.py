from datetime import date
from sme_ptrf_apps.mandatos.exceptions import CargoComposicaoVacanciaValidationError
from sme_ptrf_apps.mandatos.models import (
    Mandato, CargoComposicaoVacancia, OcupanteCargo, ComposicaoVacancia
)


class ValidatorEntradaDatasDentroDoMandato:
    """ Datas dentro do intervalo do mandato"""

    @staticmethod
    def validar(mandato, data_inicio):
        """ Valida que `data_inicio` está dentro do
            intervalo `[mandato.data_inicial, mandato.data_final]`

        Args:
            mandato: mandato de referencia
            data_inicio: data de inicio a validar

        Raises:
            CargoComposicaoVacanciaValidationError: se qualquer data estiver fora do intervalo
        """
        if data_inicio < mandato.data_inicial:
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "Não é permitido informar data de início anterior ao início do mandato."
            })
        if data_inicio > mandato.data_final:
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "Não é permitido informar data de início posterior ao fim do mandato."
            })


class ValidatorEntradaDataNaoFutura:
    """ Valida que data não é posterior a hoje """

    @staticmethod
    def validar(data_entrada: date) -> None:
        """ Valida que data não é futura

        Args:
            data (date): data a ser validada

        Raises:
            CargoComposicaoVacanciaValidationError
        """
        if data_entrada > date.today():
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "Não é permitido informar data futura."
            })


class ValidatorEntradaCargoSemOcupanteVigente:
    """ Não pode existir outro registro ocupado e vigente para o mesmo cargo

    Sem constraint de banco, por isso, ao registrar uma entrada é importante considerar o uso
    de `select_for_update()` na query para evitar corrida entre duas entradas concorrentes.
    """

    @staticmethod
    def validar(registros_do_cargo, mandato: Mandato) -> None:
        """ Valida que não há registro ocupado e vigente no cargo associacao

        Args:
            `registros_do_cargo`: queryset de `CargoComposicaoVacancia` já filtrado por
            `composicao_vacancia` + `cargo_associacao` (travado por select_for_update()
            antes de chamar o validator).
            mandato: mandato de referência - define o sentinela de considerá-lo como "vigente"
            quando `data_fim_no_cargo` é igual à data fim do mandato `mandato.data_final`

        Raises:
            CargoComposicaoVacanciaValidationError: se já existir um registro ocupado e vigente no cargo.
        """
        existe_vigente = registros_do_cargo.filter(
            ocupante_do_cargo__isnull=False,
            data_fim_no_cargo=mandato.data_final
        ).exists()
        if existe_vigente:
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "Já existe um ocupante ativo para este cargo."
            })


class ValidatorEntradaSemConflitoDeDatas:
    """ O intervalo do novo registro não pode conflitar com nehum registro OCUPADO
    já existente do mesmo cargo (vigente ou histórico). Sobrepor uma vacancia aberta(Vacancia sem ocupante no cargo)
    é o caso normal de preencher um gap """

    @staticmethod
    def validar(registros_do_cargo, data_inicio: date, data_fim: date) -> None:
        """
            Valida ausência de sobreposição contra registros ocupados do mesmo cargo.

            Args:
                `registros_do_cargo`: queryset de `CargoComposicaoVacancia` já filtrado por
                    `composicao` + `cargo_associacao` (travado por select_for_update() antes de chamar o validator).
                `data_inicio`: data de inicio a validar
                `data_fim`: data de término a validar

            Raises:
                CargoComposicaoVacanciaValidationError: se houver sobreposição com um
                    registro ocupado (vigente ou histórico).
        """
        conflito = registros_do_cargo.filter(
            ocupante_do_cargo__isnull=False,
            data_inicio_no_cargo__lte=data_fim,
            data_fim_no_cargo__gte=data_inicio,
        ).exists()
        if conflito:
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "O período informado conflita com um período ocupado."
            })


class ValidatorEntradaOcupanteNaoEstaEmOutroCargo:
    """ O mesmo ocupante não pode estar ativo, no mesmo período, em um cargo DIFERENTE dentro da mesma composição.
    Pode voltar a ocupar o MESMO cargo em um período diferente, por isso o cargo atual é excluído da checagem."""

    @staticmethod
    def validar(composicao_vacancia: ComposicaoVacancia,
                ocupante_do_cargo: OcupanteCargo,
                cargo_associacao: str,
                data_inicio: date,
                data_fim: date) -> None:
        """ Valida que o ocupante não está em outro cargo, sobreposto no tempo.

        Args:
            `composicao_vacancia`: composição onde o novo registro será inserido
            `ocupante_do_cargo`: pessoa sendo lançada no cargo.
            `cargo_associacao`: cargo sendo preenchido agora (excluído da checagem).
            `data_inicio`: início do intervalo do novo registro
            `data_fim`: fim do intervalo do novo registro

        Raises:
            CargoComposicaoVacanciaValidationError: se o ocupante já estiver em outro cargo, com período sobresposto,
            na mesma composição.
        """
        conflito = CargoComposicaoVacancia.objects.filter(
            composicao=composicao_vacancia,
            ocupante_do_cargo=ocupante_do_cargo,
            data_inicio_no_cargo__lte=data_fim,
            data_fim_no_cargo__gte=data_inicio,
        ).exclude(cargo_associacao=cargo_associacao).exists()
        if conflito:
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "Este ocupante já está em outro cargo neste período."
            })


class ValidatorEntradaSemDuplicidadeDeOcupante:
    """ Não podem existir dois OcupanteCargo distintos, ambos ocupados e vigentes na mesma composição, com o mesmo
        `codigo_identificacao`ou o mesmo `cpf_responsavel`.

        Escopo restrito a registros OCUPADOS e VIGENTES. Históricos encerrados não contam
        permitindo reentrada da mesma pessoa em outro período.
        O próprio `ocupante_do_cargo` é excluído da comparação.
    """

    @staticmethod
    def validar(composicao_vacancia: ComposicaoVacancia, ocupante_do_cargo: OcupanteCargo, mandato: Mandato) -> None:
        """ Valida ausência de outro OcupanteCargo vigente com o mesmo `codigo_identificador/cpf_responsavel`.
            Args:
                `composicao_vacancia`: composição onde o novo registro sera inserido.
                `ocupante_do_cargo`: pessoa sendo lançada no cargo. (excluída da checagem)
                `mandato`: mandato de referência para verificar quando `data_fim_no_cargo` é igual à
                            data fim do mandato `mandato.data_final`
            Raises:
                CargoComposicaoVacanciaValidationError: se outro ocupante vigente com o mesmo
                `codigo_identificador/cpf_responsavel` com `ocupante_do_cargo`.
        """
        vigentes = CargoComposicaoVacancia.objects.filter(
            composicao=composicao_vacancia,
            ocupante_do_cargo__isnull=False,
            data_fim_no_cargo=mandato.data_final,
        ).exclude(ocupante_do_cargo=ocupante_do_cargo)

        if ocupante_do_cargo.codigo_identificacao:
            conflito = vigentes.filter(
                ocupante_do_cargo__codigo_identificacao=ocupante_do_cargo.codigo_identificacao
            ).exists()
            if conflito:
                raise CargoComposicaoVacanciaValidationError({
                    "mensagem": "Já existe um membro vigente nesta composição com o mesmo Código de Identificação."
                })

        if ocupante_do_cargo.cpf_responsavel:
            conflito = vigentes.filter(
                ocupante_do_cargo__cpf_responsavel=ocupante_do_cargo.cpf_responsavel
            ).exists()
            if conflito:
                raise CargoComposicaoVacanciaValidationError({
                    "mensagem": "Já existe um membro vigente nesta composição com o mesmo CPF."
                })

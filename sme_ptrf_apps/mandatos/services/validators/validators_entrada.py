from datetime import date

from django.db.models import QuerySet

from sme_ptrf_apps.mandatos.exceptions import CargoComposicaoVacanciaValidationError
from sme_ptrf_apps.mandatos.models import (
    Mandato, CargoComposicaoVacancia, OcupanteCargo, ComposicaoVacancia
)


class ValidatorEntradaDatasDentroDoMandato:
    """Exige que a data de início esteja dentro do intervalo do mandato."""

    @staticmethod
    def validar(mandato: Mandato, data_inicio: date) -> None:
        """Valida que data_inicio está no intervalo [mandato.data_inicial, mandato.data_final].

        Args:
            mandato: mandato de referência.
            data_inicio: data de início a validar.

        Raises:
            CargoComposicaoVacanciaValidationError: se data_inicio estiver fora do intervalo.
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
    """Exige que a data de entrada não seja futura."""

    @staticmethod
    def validar(data_entrada: date) -> None:
        """Valida que a data de entrada não é posterior a hoje.

        Args:
            data_entrada: data a ser validada.

        Raises:
            CargoComposicaoVacanciaValidationError: se data_entrada for posterior a hoje.
        """
        if data_entrada > date.today():
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "Não é permitido informar data futura."
            })


class ValidatorEntradaCargoSemOcupanteVigente:
    """Impede um segundo registro ocupado e vigente para o mesmo cargo.

    Não há constraint de banco para isso; ao registrar uma entrada, a query dos registros
    do cargo deve ser travada com select_for_update() para evitar corrida entre duas
    entradas concorrentes.
    """

    @staticmethod
    def validar(registros_do_cargo: QuerySet, mandato: Mandato) -> None:
        """Valida que não há registro ocupado e vigente no cargo.

        Args:
            registros_do_cargo: queryset de CargoComposicaoVacancia já filtrado por
                composição + cargo_associacao (travado por select_for_update() antes
                de chamar o validator).
            mandato: mandato de referência. Um registro é vigente quando data_fim_no_cargo
                é igual a mandato.data_final.

        Raises:
            CargoComposicaoVacanciaValidationError: se já existir um registro ocupado e
                vigente no cargo.
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
    """Impede que o novo registro se sobreponha a um registro ocupado do mesmo cargo.

    Vale para registros ocupados vigentes ou históricos. Sobrepor uma vacância aberta
    (registro sem ocupante) é o caso normal de preencher um gap e não é conflito.
    """

    @staticmethod
    def validar(registros_do_cargo: QuerySet, data_inicio: date, data_fim: date) -> None:
        """Valida ausência de sobreposição contra registros ocupados do mesmo cargo.

        Args:
            registros_do_cargo: queryset de CargoComposicaoVacancia já filtrado por
                composição + cargo_associacao (travado por select_for_update() antes
                de chamar o validator).
            data_inicio: data de início a validar.
            data_fim: data de término a validar.

        Raises:
            CargoComposicaoVacanciaValidationError: se houver sobreposição com um registro
                ocupado (vigente ou histórico).
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
    """Impede o mesmo ocupante ativo, no mesmo período, em outro cargo da mesma composição.

    O ocupante pode voltar a ocupar o mesmo cargo em um período diferente, por isso o
    cargo atual é excluído da checagem.
    """

    @staticmethod
    def validar(composicao_vacancia: ComposicaoVacancia,
                ocupante_do_cargo: OcupanteCargo,
                cargo_associacao: str,
                data_inicio: date,
                data_fim: date) -> None:
        """Valida que o ocupante não está em outro cargo com período sobreposto.

        Args:
            composicao_vacancia: composição onde o novo registro será inserido.
            ocupante_do_cargo: pessoa sendo lançada no cargo.
            cargo_associacao: cargo sendo preenchido agora (excluído da checagem).
            data_inicio: início do intervalo do novo registro.
            data_fim: fim do intervalo do novo registro.

        Raises:
            CargoComposicaoVacanciaValidationError: se o ocupante já estiver em outro cargo,
                com período sobreposto, na mesma composição.
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
    """Impede dois OcupanteCargo distintos, ocupados e vigentes na mesma composição, com o
    mesmo codigo_identificacao ou o mesmo cpf_responsavel.

    Escopo restrito a registros ocupados e vigentes: históricos encerrados não contam,
    permitindo reentrada da mesma pessoa em outro período. O próprio ocupante_do_cargo
    é excluído da comparação.
    """

    @staticmethod
    def validar(composicao_vacancia: ComposicaoVacancia, ocupante_do_cargo: OcupanteCargo, mandato: Mandato) -> None:
        """Valida ausência de outro ocupante vigente com o mesmo codigo_identificacao/cpf_responsavel.

        Args:
            composicao_vacancia: composição onde o novo registro será inserido.
            ocupante_do_cargo: pessoa sendo lançada no cargo (excluída da checagem).
            mandato: mandato de referência. Um registro é vigente quando data_fim_no_cargo
                é igual a mandato.data_final.

        Raises:
            CargoComposicaoVacanciaValidationError: se outro ocupante vigente tiver o mesmo
                codigo_identificacao ou o mesmo cpf_responsavel.
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

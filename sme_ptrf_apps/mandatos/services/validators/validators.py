from datetime import timedelta
from sme_ptrf_apps.mandatos.exceptions import CargoComposicaoVacanciaValidationError
from sme_ptrf_apps.mandatos.models import (
    Mandato, CargoComposicaoVacancia, ComposicaoVacancia
)


class ValidatorCargoVazio:
    """Exige que o cargo não esteja vazio (sem ocupante)."""

    @staticmethod
    def validar(cargo_composicao_vacancia: CargoComposicaoVacancia) -> None:
        """Valida que o registro tem ocupante definido.

        Args:
            cargo_composicao_vacancia: registro sendo editado.

        Raises:
            CargoComposicaoVacanciaValidationError: se o cargo estiver vazio.
        """
        if cargo_composicao_vacancia.ocupante_do_cargo_id is None:
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": "Ocupante no cargo não está definido."
            })


class ValidatorSemGapNaTimelineDoCargo:
    """Confirma que a timeline de um cargo cobre o mandato inteiro, sem buraco nem sobreposição.

    Todo dia do mandato tem exatamente um registro (ocupado ou vago). Roda defensivamente
    ao final de qualquer operação que crie ou altere CargoComposicaoVacancia (entrada,
    saída, cancelamento): se detectar inconsistência, levanta erro e a transação
    (@transaction.atomic do método chamador) é revertida por completo.
    """

    @staticmethod
    def validar(composicao_vacancia: ComposicaoVacancia, cargo_associacao: str, mandato: Mandato) -> None:
        """Confere a timeline completa de um cargo dentro de uma composição.

        Args:
            composicao_vacancia: composição a verificar.
            cargo_associacao: cargo cuja timeline será verificada.
            mandato: mandato de referência, que define o intervalo total esperado.

        Raises:
            CargoComposicaoVacanciaValidationError: se existir algum trecho do mandato
                sem nenhum registro (ocupado ou vago) para o cargo, ou sobreposição.
        """
        registros = list(
            CargoComposicaoVacancia.objects.filter(
                composicao=composicao_vacancia,
                cargo_associacao=cargo_associacao,
            ).order_by('data_inicio_no_cargo')
        )

        if not registros:
            # cargo nunca teve nenhum registro - nada a verificar (ninguém nunca ocupou)
            return

        # primeiramente, verifica se o primeiro registro começa no início do mandato
        if registros[0].data_inicio_no_cargo != mandato.data_inicial:
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": f"Inconsistência na timeline do cargo {cargo_associacao}: "
                            f"o primeiro registro não começa no início do mandato."
            })

        # a partir do próximo, verifica se houve gap ou sobreposição
        # primeiro parâmetro do zip: o anterior(inicia no índice 0), segundo parâmetro: o atual (inicia no índice 1)
        for anterior, atual in zip(registros, registros[1:]):
            if atual.data_inicio_no_cargo != anterior.data_fim_no_cargo + timedelta(days=1):
                raise CargoComposicaoVacanciaValidationError({
                    "mensagem": f"Inconsistência na timeline do cargo {cargo_associacao}: "
                                f"gap ou sobreposição entre {anterior.data_fim_no_cargo} "
                                f"e {atual.data_inicio_no_cargo}."
                })

        # verifica se o ultimo registro termina no fim do mandato
        if registros[-1].data_fim_no_cargo != mandato.data_final:
            raise CargoComposicaoVacanciaValidationError({
                "mensagem": f"Inconsistência na timeline do cargo {cargo_associacao}: "
                            f"o último registro não termina no fim do mandato."
            })

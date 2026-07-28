from abc import ABC, abstractmethod

from .context import BemProduzidoDtoContext


class PipelineConfigurationError(Exception):
    """Erro de configuração do pipeline — detectado em tempo de construção.

    Indica que o pipeline foi montado de forma incorreta (ex.: ordem de validators
    incompatível com dependências entre regras). É um erro de programação,
    não um erro de validação de negócio.
    """


class SituacaoPatrimonialValidationError(Exception):
    """Erro de validação de negócio desacoplado de DRF.

    `detail` pode ser string ou dict (espelhando a estrutura de serializers.ValidationError).
    No ponto de integração com o serializer, converta para serializers.ValidationError:

        try:
            pipeline.run(ctx)
        except DespesaValidationError as exc:
            raise serializers.ValidationError(exc.detail)
    """

    def __init__(self, title: str, detail: str):
        self.title = title
        self.detail = detail
        super().__init__(detail)


class AbstractBemProduzidoValidator(ABC):
    """Interface base para todos os validators do pipeline de despesa.

    Flags de controle:
    - `applies_to_create`: se False, o validator é ignorado no pipeline de criação.
    - `applies_to_update`: se False, o validator é ignorado no pipeline de edição.
    """

    applies_to_create: bool = True
    applies_to_update: bool = True

    @abstractmethod
    def validate(self, ctx: BemProduzidoDtoContext) -> BemProduzidoDtoContext:
        """Fase 1 — valida o contexto e o retorna (possivelmente enriquecido).

        Levanta DespesaValidationError se a regra for violada.
        Nunca faz mutações em dados de negócio — apenas enriquece ctx com informações
        derivadas (ex.: periodo, saldos) usadas por validators subsequentes.
        """
        ...

    def apply(self, ctx: BemProduzidoDtoContext) -> BemProduzidoDtoContext:
        """Fase 2 — mutações de negócio derivadas desta regra.

        Chamado somente se TODAS as validações (fase 1) passaram.
        Padrão: no-op. Sobrescreva apenas quando esta regra implica uma mutação
        de estado (ex.: limpar campos incompatíveis, zerar motivos antecipados).
        """
        return ctx

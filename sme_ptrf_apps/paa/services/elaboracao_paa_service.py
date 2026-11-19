from datetime import date

from waffle import flag_is_active, get_waffle_flag_model

from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.paa import constantes
from sme_ptrf_apps.paa.constantes import FLAG_PAA_PROXIMA_VIGENCIA
from sme_ptrf_apps.paa.models import Paa, ParametroPaa, PeriodoPaa


class PeriodoInvalidoParaElaboracaoException(Exception):
    """Exceção lançada quando o período do PAA não é válido para elaboração."""


def proxima_vigencia_habilitada(request=None) -> bool:
    """Verifica se a flag de próxima vigência do PAA está habilitada.

    Args:
        request: requisição atual, quando houver"""

    if request:
        return flag_is_active(request, FLAG_PAA_PROXIMA_VIGENCIA)
    return get_waffle_flag_model().objects.filter(
        name=FLAG_PAA_PROXIMA_VIGENCIA,
        everyone=True
    ).exists()


# Mensagem de cada regra violada, indexada pelo motivo
MENSAGENS = {
    'periodo_encerrado': (
        'O período informado já foi encerrado.'),
    'periodos_sobrepostos': (
        'Há períodos de PAA sobrepostos. Procure a SME para regularizar o cadastro de períodos.'),
    'mes_nao_liberado_igual': (
        'A elaboração do PAA só pode ser iniciada no mês parametrizado.'),
    'mes_nao_liberado_a_partir_de': (
        'A elaboração do PAA só pode ser iniciada a partir do mês parametrizado.'),
    'periodo_fora_da_vigencia': (
        'Só é possível elaborar o PAA do período vigente ou da próxima vigência.'),
    'proxima_vigencia_desabilitada': (
        'A elaboração do PAA da próxima vigência não está disponível.'),
    'paa_vigente_fora_da_situacao_exigida': (
        'O PAA anterior ainda não está na situação exigida para iniciar o da próxima vigência.'),
    'paa_vigente_inexistente': (
        'O PAA vigente ainda não foi iniciado.')
}


class ElaboracaoPaaService:
    """Garante  as regras de negócio da criação de um PAA.

    Cada validação é um método com uma única responsabilidade.
    `validar_periodo_para_criacao` apenas encadeia, na ordem em que a mensagem de erro é identificada
    """

    @classmethod
    def validar_periodo_para_criacao(cls, associacao: Associacao, periodo: PeriodoPaa,
                                     proxima_vigencia_habilitada: bool,
                                     hoje: date | None = None) -> None:
        """Valida se a associação pode iniciar o PAA no período informado.

        Args:
            associacao: Associação que criará o PAA.
            periodo: Período do PAA a criar.
            proxima_vigencia_habilitada: Se a flag do PAA da próxima vigência está ativa.
            hoje: Data de referência.

        Raises:
            PeriodoInvalidoParaElaboracaoException: Se o período não é válido para elaboração.
        """
        hoje = hoje or date.today()

        cls._validar_periodo_nao_encerrado(periodo, hoje)
        cls._validar_sem_periodos_sobrepostos(hoje)
        cls._validar_mes_de_elaboracao(hoje)

        vigente = PeriodoPaa.vigente_em(hoje)
        if periodo == vigente:
            return

        cls._validar_periodo_e_a_proxima_vigencia(periodo, hoje)
        cls._validar_proxima_vigencia_habilitada(proxima_vigencia_habilitada)
        cls._validar_situacao_exigida_do_paa_vigente(associacao, vigente)

    @staticmethod
    def _recusar(motivo: str) -> None:
        """interrompe a validação com a mensagem do motivo

        Args:
            motivo: chave do dicionário de mensagens de erro.

        Raises:
            PeriodoInvalidoParaElaboracaoException.
        """
        raise PeriodoInvalidoParaElaboracaoException(MENSAGENS[motivo])

    @classmethod
    def _validar_periodo_nao_encerrado(cls, periodo: PeriodoPaa, hoje: date) -> None:
        """Recusa período cuja data final já passou: não se inicia PAA em período encerrado.

        Args:
            periodo: Período do PAA a criar.

        Raises:
            PeriodoInvalidoParaElaboracaoException: Se o período está encerrado.
        """
        if periodo.data_final < date.today():
            cls._recusar('periodo_encerrado')

    @classmethod
    def _validar_sem_periodos_sobrepostos(cls, hoje: date) -> None:
        """Recusa a criação do PAA se houver períodos sobrepostos envolvendo o vigente ou o próxima.
        Com sobreposição a vigência fica ambígua e o PAA poderia ser criado no período errado.

        Args:
            hoje: Data de referência.

        Raises:
            PeriodoInvalidoParaElaboracaoException: Se há períodos sobrepostos.
        """
        if PeriodoPaa.tem_sobreposicao_relevante(hoje):
            cls._recusar('periodos_sobrepostos')

    @classmethod
    def _validar_mes_de_elaboracao(cls, hoje: date) -> None:
        """Recusa a criação do PAA fora do mês parametrizado para a elaboração.

        Args:
            hoje: Data de referência.

        Raises:
            PeriodoInvalidoParaElaboracaoException: Se o mês atual não é o mês de elaboração.
        """
        mes_parametrizado = ParametroPaa.get().mes_elaboracao_paa

        if constantes.MODO_MES_ELABORACAO == constantes.MES_ELABORACAO_IGUAL:
            liberado, motivo = hoje.month == mes_parametrizado, 'mes_nao_liberado_igual'
        elif constantes.MODO_MES_ELABORACAO == constantes.MES_ELABORACAO_A_PARTIR_DE:
            liberado, motivo = hoje.month >= mes_parametrizado, 'mes_nao_liberado_a_partir_de'
        else:
            raise ValueError('Modo de validação de mês de elaboração desconhecido.')

        if not liberado:
            cls._recusar(motivo)

    @classmethod
    def _validar_periodo_e_a_proxima_vigencia(cls, periodo: PeriodoPaa, hoje: date) -> None:
        """Recusa a criação do PAA quando o período não é o vigente e nem o primeiro após o vigente(proxima vigência).

        Chamado só quando o período não é o vigente. Impede, por exemplo, iniciar um PAA dois períodos à frente.

        Args:
            periodo: Período do PAA a criar.
            hoje: Data de referência.

        Raises:
            PeriodoInvalidoParaElaboracaoException: Se o período não é o vigente nem o próxima vigência.
        """
        if periodo != PeriodoPaa.proxima_vigencia_em(hoje):
            cls._recusar('periodo_fora_da_vigencia')

    @classmethod
    def _validar_proxima_vigencia_habilitada(cls, habilitada: bool) -> None:
        """Recusa a criação do PAA da próxima vigência quando a flag não está habilitada.

        Args:
            habilitada: Se a flag do PAA da próxima vigência está ativa.

        Raises:
            PeriodoInvalidoParaElaboracaoException: Se a flag não está habilitada.
        """
        if not habilitada:
            cls._recusar('proxima_vigencia_desabilitada')

    @classmethod
    def _validar_situacao_exigida_do_paa_vigente(cls, associacao: Associacao, vigente: PeriodoPaa | None) -> None:
        """Aplica a exigência configurada sobre a situação do PAA vigente para iniciar a próxima vigência.

        Sem exigência (None), não há o que verificar.
        Com exigência (tupla de status), o PAA vigente da associação precisa existir e estar em uma das situações
        listadas. Sem período vigente ou sem PAA nele, a criação é recusada.

        Args:
            associacao: Associação que criará o PAA.
            vigente: Período vigente na data de referência, se houver

        Raises:
            PeriodoInvalidoParaElaboracaoException: Se o PAA vigente não está na situação exigida ou não existe.
        """
        exigidos = constantes.STATUS_VIGENTE_EXIGIDOS_PARA_INICIAR_PROXIMA_VIGENCIA
        if exigidos is None:
            return

        paa_vigente = (
            Paa.objects
            .filter(associacao=associacao, periodo_paa=vigente)
            .first() if vigente else None
        )
        if paa_vigente is None:
            cls._recusar('paa_vigente_inexistente')

        if paa_vigente.get_status_andamento() not in exigidos:
            cls._recusar('paa_vigente_fora_da_situacao_exigida')

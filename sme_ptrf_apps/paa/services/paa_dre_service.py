
from typing import Dict, List, Optional, Tuple
from django.db.models import QuerySet
from sme_ptrf_apps.core.models import Associacao, Unidade
from sme_ptrf_apps.paa.models import Paa, PeriodoPaa
from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.core.choices.tipos_unidade import TIPOS_CHOICE
from sme_ptrf_apps.paa.api.serializers.paa_serializer import PaaDreSerializer, PeriodoPaaSimplesSerializer
from rest_framework import serializers


class ValidacaoPaaDre(serializers.ValidationError):
    """ Raises para Validação PaaDre """
    def __init__(self, detail):
        self.detail = detail


class PaaDreService:

    @staticmethod
    def _obter_dre(unidade_dre_uuid: str) -> Unidade:
        """
        Obtém a unidade DRE pelo UUID.

        Args:
            unidade_dre_uuid (str): UUID da unidade DRE.

        Returns:
            Unidade: Objeto da unidade DRE encontrada.

        Raises:
            ValidacaoPaaDre: Caso a DRE não seja encontrada.
        """
        try:
            return Unidade.dres.get(uuid=unidade_dre_uuid)
        except Unidade.DoesNotExist:
            raise ValidacaoPaaDre({
                'erro': 'DRE não encontrada',
                'mensagem': f"DRE {unidade_dre_uuid} não encontrada."
            })

    @staticmethod
    def _valida_status(raw_status: Optional[List[str]]) -> Optional[List[str]]:
        """
        Valida os status informados na query.

        Args:
            raw_status (Optional[List[str]]): Lista de status recebidos.

        Returns:
            Optional[List[str]]: Lista validada ou None.

        Raises:
            ValidacaoPaaDre: Caso exista algum status inválido.
        """
        if not raw_status:
            return None

        status_validos = {s.name for s in PaaStatusEnum}
        invalidos = [s for s in raw_status if s not in status_validos]

        if invalidos:
            raise ValidacaoPaaDre({
                "status": f"Inválidos: {invalidos}. Permitidos: {list(status_validos)}"
            })

        return raw_status

    @staticmethod
    def _get_associacoes(dre: Unidade, filtros: Dict) -> QuerySet[Associacao]:
        """
        Retorna queryset de associações da DRE aplicando filtros.
        """
        qs: QuerySet[Associacao] = (
            Associacao.ativas
            .filter(unidade__dre=dre)
            .select_related('unidade')
        )

        if filtros.get('unidade'):
            qs = qs.filter(unidade__uuid__in=filtros['unidade'])

        if filtros.get('tipo_unidade'):
            qs = qs.filter(unidade__tipo_unidade=filtros['tipo_unidade'])

        return qs

    @staticmethod
    def _get_periodos(filtros: Dict) -> QuerySet[PeriodoPaa]:
        """
        Retorna queryset de períodos aplicando filtros.
        """
        qs: QuerySet[PeriodoPaa] = PeriodoPaa.objects.all()

        if filtros.get('periodo'):
            qs = qs.filter(uuid__in=filtros['periodo'])

        return qs

    @staticmethod
    def _get_paas(
        associacoes: QuerySet[Associacao],
        periodos: QuerySet[PeriodoPaa],
        filtro_status: Optional[List[str]]
    ) -> QuerySet[Paa]:
        """
        Retorna queryset de PAAs filtrados.
        """
        qs: QuerySet[Paa] = (
            Paa.objects
            .filter(associacao__in=associacoes, periodo_paa__in=periodos)
            .select_related('associacao', 'periodo_paa')
        )

        if filtro_status:
            qs = qs.filter(status__in=filtro_status)

        return qs

    @staticmethod
    def _mapear_paas(paas: QuerySet[Paa]) -> Dict[Tuple[int, int], Paa]:
        """
        Cria um mapa de PAAs para acesso rápido.
        """
        return {
            (p.associacao_id, p.periodo_paa_id): p
            for p in paas
        }

    @staticmethod
    def _build_nao_iniciado(
        associacao: Associacao,
        periodo: PeriodoPaa
    ) -> Dict:
        """
        Monta estrutura de resposta para PAA não iniciado.
        """
        return {
            'uuid': None,
            'periodo_paa': {
                'uuid': periodo.uuid,
                'id': periodo.id,
                'referencia': periodo.referencia,
                'data_inicial': periodo.data_inicial,
                'data_final': periodo.data_final,
                'ano_inicial_final': periodo.ano_inicial_final
            },
            'unidade': {
                'uuid': associacao.unidade.uuid,
                'unidade_educacional': associacao.unidade.nome_com_tipo,
                'codigo_eol': associacao.unidade.codigo_eol,
                'nome': associacao.unidade.nome,
                'tipo_unidade': associacao.unidade.tipo_unidade
            },
            'saldo_congelado_em': None,
            'status': PaaStatusEnum.NAO_INICIADO.name,
            'status_display': PaaStatusEnum.NAO_INICIADO.value,
            'tem_documentos': False,
        }

    @staticmethod
    def _deve_incluir_nao_iniciado(filtro_status: Optional[List[str]]) -> bool:
        """
        Define se deve incluir registros de PAA não iniciado.
        """
        return not filtro_status or PaaStatusEnum.NAO_INICIADO.name in filtro_status

    @classmethod
    def listar_paas(
        cls,
        unidade_dre_uuid: str,
        filtros: Optional[Dict[str, List[str]]] = None
    ) -> List[Dict]:
        """
        Lista os PAAs por DRE, incluindo unidades sem PAA (Não Iniciado).

        Args:
            unidade_dre_uuid (str): UUID da Unidade DRE.
            filtros (Optional[Dict[str, List[str]]]): Filtros da requisição.

        Returns:
            List[Dict]: Lista de PAAs serializados.
        """
        filtros = filtros or {}

        filtro_status = cls._valida_status(filtros.get('status'))
        dre = cls._obter_dre(unidade_dre_uuid)

        associacoes = cls._get_associacoes(dre, filtros)
        periodos = cls._get_periodos(filtros)
        paas = cls._get_paas(associacoes, periodos, filtro_status)

        mapa_paa = cls._mapear_paas(paas)
        incluir_nao_iniciado = cls._deve_incluir_nao_iniciado(filtro_status)

        resultado: List[Dict] = []

        for periodo in periodos:
            for associacao in associacoes:
                key = (associacao.id, periodo.id)
                paa = mapa_paa.get(key)

                if paa:
                    resultado.append(PaaDreSerializer(paa).data)
                elif incluir_nao_iniciado:
                    resultado.append(
                        cls._build_nao_iniciado(associacao, periodo)
                    )

        return resultado

    @staticmethod
    def _listar_periodos() -> List[Dict]:
        return PeriodoPaaSimplesSerializer(PeriodoPaa.objects.all().order_by("-referencia"), many=True).data

    @staticmethod
    def _listar_unidades(dre: Unidade) -> List[Dict]:
        """
        Lista unidades da DRE a partir das associações ativas.
        """
        qs = (
            Associacao.ativas
            .filter(unidade__dre=dre)
            .values(
                "unidade__uuid",
                "unidade__nome",
                "unidade__tipo_unidade",
            )
            .distinct()
            .order_by("unidade__nome")
        )

        return [
            {
                "uuid": item["unidade__uuid"],
                "nome": item["unidade__nome"],
                "tipo_unidade": item["unidade__tipo_unidade"],
                "unidade_educacional": f"{item["unidade__tipo_unidade"]} {item["unidade__nome"]}"
            }
            for item in qs
        ]

    @staticmethod
    def _listar_tipos_unidade() -> List[Dict]:
        return [
            {"id": key, "nome": value}
            for key, value in TIPOS_CHOICE
        ]

    @staticmethod
    def _listar_status() -> List[Dict]:
        return [
            {"id": status.name, "nome": status.value}
            for status in PaaStatusEnum
        ]

    @classmethod
    def obter_tabelas(cls, unidade_dre_uuid: str) -> Dict:
        """
        Retorna dados auxiliares para filtros da tela.

        Args:
            unidade_dre_uuid (str): UUID da Unidade DRE

        Returns:
            Dict: Estrutura com períodos, unidades, tipos e status
        """

        dre = cls._obter_dre(unidade_dre_uuid)

        return {
            "periodos": cls._listar_periodos(),
            "unidades": cls._listar_unidades(dre),
            "tipos_unidade": cls._listar_tipos_unidade(),
            "status": cls._listar_status(),
        }

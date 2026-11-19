from rest_framework import serializers
from rest_framework.exceptions import NotFound

from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.paa import constantes
from sme_ptrf_apps.users.services.unidades_acessiveis_service import usuario_pode_acessar_associacao


class VigenciaElaboracaoQuerySerializer(serializers.Serializer):
    """Valida os parâmetros de query para consulta das vigênciaa de elaboração do PAA e acesso à associação."""
    associacao_uuid = serializers.UUIDField()

    def validate(self, atributos: dict) -> dict:
        """Resolve a Associação e exige que o usuário possa acessar a unidade
        Associação inexistente e associação inacessível respondem igual (404)

        Raises:
            NotFound: Se a associação não existir ou não for acessível ao usuário.
        """
        usuario = self.context['request'].user
        associacao = (
            Associacao.objects
            .select_related('unidade')
            .filter(uuid=atributos['associacao_uuid'])
            .first()
        )
        if not associacao or not usuario_pode_acessar_associacao(usuario, associacao):
            raise NotFound("Associação não encontrada.")

        atributos['associacao'] = associacao
        return atributos


class PaaResumoSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    status = serializers.CharField()
    status_andamento = serializers.CharField()


class PeriodoElaboracaoSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    referencia = serializers.CharField()
    data_inicial = serializers.DateField()
    data_final = serializers.DateField()
    vigencia = serializers.ChoiceField(choices=[
        constantes.VIGENCIA_VIGENTE,
        constantes.VIGENCIA_PROXIMA_VIGENCIA,
        constantes.VIGENCIA_ENCERRADO,
        constantes.VIGENCIA_FUTURO,
    ])
    paa = PaaResumoSerializer(allow_null=True)


class PeriodosPaginadosSerializer(serializers.Serializer):
    links = serializers.DictField()
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = PeriodoElaboracaoSerializer(many=True)


class VigenciaElaboracaoSerializer(serializers.Serializer):
    hoje = serializers.DateField()
    mes_elaboracao_paa = serializers.IntegerField(allow_null=True)
    proxima_vigencia_habilitada = serializers.BooleanField()
    periodos_sobrepostos = serializers.BooleanField()
    status_vigente_exigidos_para_proxima_vigencia = serializers.ListField(
        child=serializers.CharField(),
        allow_null=True,
    )
    periodos = PeriodosPaginadosSerializer()

from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST

from ...models import Mandato, Composicao
from ...services.composicao_service import ServicoComposicaoVigente, ServicoCriaComposicaoVigenteDoMandato


class CustomError(APIException):
    """Readers error class"""

    def __init__(self, msg):
        APIException.__init__(self, msg)
        self.status_code = HTTP_400_BAD_REQUEST
        self.message = msg


class MandatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mandato
        fields = ('id', 'uuid', 'referencia_mandato', 'data_inicial', 'data_final')

    def validate(self, data):
        data_inicial = data.get('data_inicial')
        data_final = data.get('data_final')

        # Verificar se a data final é menor que a data inicial
        if data_final < data_inicial:
            raise CustomError({"detail": "A data final não pode ser menor que a data inicial"})

        # Verificar se a data inicial está dentro de outro mandato existente
        if data_inicial and data_final:
            mandatos = Mandato.objects.filter(data_inicial__lte=data_inicial, data_final__gte=data_inicial)

            if self.instance:
                mandatos = mandatos.exclude(
                    uuid=self.instance.uuid)  # Excluir o próprio objeto atual ao verificar colisões

            if mandatos.exists():
                raise CustomError({"detail": "A data inicial informada é de vigência de outro mandato cadastrado."})

        return data


class MandatoVigenteComComposicoesSerializer(serializers.ModelSerializer):
    composicoes = serializers.SerializerMethodField('get_composicoes')

    def get_composicoes(self, obj):
        from sme_ptrf_apps.mandatos.api.serializers.composicao_serializer import ComposicaoComCargosSerializer
        associacao = self.context.get("associacao")

        composicoes_list = []

        servico_composicao_vigente = ServicoComposicaoVigente(associacao=associacao, mandato=obj)
        composicao_vigente = servico_composicao_vigente.get_composicao_vigente()

        if not composicao_vigente:
            servico_cria_composicao_vigente = ServicoCriaComposicaoVigenteDoMandato(associacao=associacao,
                                                                                    mandato=obj)
            composicao_vigente = servico_cria_composicao_vigente.cria_composicao_vigente()

        # Seta a Composição Vigente como primeira da lista
        composicoes_list.append(composicao_vigente)

        qs = Composicao.objects.filter(mandato=obj, associacao=associacao).exclude(
            uuid=composicao_vigente.uuid).order_by('-data_inicial')

        # Acrescenta as demais composições a lista
        for q in qs:
            composicoes_list.append(q)

        return ComposicaoComCargosSerializer(composicoes_list, many=True).data

    class Meta:
        model = Mandato
        fields = ('id', 'uuid', 'referencia_mandato', 'data_inicial', 'data_final', 'composicoes',)


class MandatoComComposicoesSerializer(serializers.ModelSerializer):
    composicoes = serializers.SerializerMethodField('get_composicoes')

    def get_composicoes(self, obj):
        from sme_ptrf_apps.mandatos.api.serializers.composicao_serializer import ComposicaoComCargosSerializer
        associacao = self.context.get("associacao")

        qs = Composicao.objects.filter(mandato=obj, associacao=associacao).order_by('-data_inicial')

        return ComposicaoComCargosSerializer(qs, many=True).data

    class Meta:
        model = Mandato
        fields = ('id', 'uuid', 'referencia_mandato', 'data_inicial', 'data_final', 'composicoes',)

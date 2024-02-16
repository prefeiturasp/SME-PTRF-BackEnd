from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST

from ...models import Mandato, Composicao
from ...services import ServicoMandato
from ...services.composicao_service import ServicoComposicaoVigente, ServicoCriaComposicaoVigenteDoMandato

from datetime import timedelta


class CustomError(APIException):
    """Readers error class"""

    def __init__(self, msg):
        APIException.__init__(self, msg)
        self.status_code = HTTP_400_BAD_REQUEST
        self.message = msg


class MandatoSerializer(serializers.ModelSerializer):
    editavel = serializers.SerializerMethodField('get_editavel')
    data_inicial_proximo_mandato = serializers.SerializerMethodField('get_data_inicial_proximo_mandato')
    data_final_mandato_anterior_ao_mais_recente = serializers.SerializerMethodField('get_data_final_mandato_anterior_ao_mais_recente')
    limite_min_data_inicial = serializers.SerializerMethodField('get_limite_min_data_inicial')

    def get_editavel(self, obj):
        return obj.eh_mandato_vigente() or obj.eh_mandato_futuro()

    def get_data_inicial_proximo_mandato(self, obj):
        servico_mandato = ServicoMandato()
        mandato_mais_recente = servico_mandato.get_mandato_mais_recente()
        if obj == mandato_mais_recente:
            return obj.data_final + timedelta(days=1)
        else:
            return None

    def get_data_final_mandato_anterior_ao_mais_recente(self, obj):
        servico_mandato = ServicoMandato()
        mandato_anterior_ao_mais_recente = servico_mandato.get_mandato_anterior_ao_mais_recente()
        result = None
        if mandato_anterior_ao_mais_recente:
            result = mandato_anterior_ao_mais_recente.data_final + timedelta(days=1)
        return result

    def get_limite_min_data_inicial(self, obj):

        mandato_anterior = Mandato.objects.filter(data_final__lt=obj.data_inicial).order_by('id').last()

        result = None
        if mandato_anterior:
            result = mandato_anterior.data_final + timedelta(days=1)

        return result

    def update(self, instance, validated_data):
        data_inicial = validated_data["data_inicial"]
        data_final = validated_data["data_final"]
        referencia_mandato = validated_data["referencia_mandato"]

        if instance.data_inicial != data_inicial:
            instance.att_data_inicio_composicoes_e_cargos_composicoes(
                data_inicial=instance.data_inicial,
                nova_data=data_inicial
            )

        if instance.data_final != data_final:
            instance.att_data_fim_composicoes_e_cargos_composicoes(
                data_final=instance.data_final,
                nova_data=data_final
            )

        instance.data_inicial = data_inicial
        instance.data_final = data_final
        instance.referencia_mandato = referencia_mandato
        instance.save()

        return instance

    class Meta:
        model = Mandato
        fields = ('id', 'uuid', 'referencia_mandato', 'data_inicial', 'data_final', 'editavel', 'data_inicial_proximo_mandato', 'data_final_mandato_anterior_ao_mais_recente', 'limite_min_data_inicial')

    def validate(self, data):
        data_inicial = data.get('data_inicial')
        data_final = data.get('data_final')

        servico_mandato = ServicoMandato()
        mandato_mais_recente = servico_mandato.get_mandato_mais_recente()

        if self.instance:
            if self.instance.possui_composicoes_com_data_final_maior_que_a_informada(data=data_final):
                raise CustomError({"detail": "Não é possível editar a data final do mandato pois existe composição de membros registrada."})

        # Verificar se a data inicial é maior que a data final do mandato mais recente no caso de uma inclusão
        if data_inicial and not self.instance and mandato_mais_recente:
            data_final_mandato_recente = mandato_mais_recente.data_final
            if data_inicial <= data_final_mandato_recente:
                raise CustomError({"detail": "A data inicial do período de mandato deve ser maior que a data final do mandato anterior"})

        # Verificar se a data final é menor que a data inicial
        if data_inicial and data_final and data_final < data_inicial:
            raise CustomError({"detail": "A data final não pode ser menor que a data inicial"})

        # Verificar se a data inicial está dentro de outro mandato existente
        if data_inicial and data_final:
            mandatos = Mandato.objects.filter(data_inicial__lte=data_inicial, data_final__gte=data_inicial)

            if self.instance:
                mandatos = mandatos.exclude(uuid=self.instance.uuid)  # Excluir o próprio objeto atual ao verificar colisões

            if mandatos.exists():
                raise CustomError({"detail": "A data inicial informada é de vigência de outro mandato cadastrado."})

            # Verificar se as datas estão dentro do intervalo de outros mandatos
            overlapped_mandatos = Mandato.objects.filter(data_inicial__lte=data_final, data_final__gte=data_inicial)

            if self.instance:
                overlapped_mandatos = overlapped_mandatos.exclude(uuid=self.instance.uuid)  # Exclui o próprio mandato atual, caso esteja sendo atualizado

            if overlapped_mandatos.exists():
                raise CustomError({"detail": "As datas do mandato se sobrepõem com outros mandatos já cadastrados."})

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

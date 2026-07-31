from django.db import transaction
from rest_framework import serializers
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.paa.models import FonteRecursoPaa, RecursoProprioPaa, Paa
from sme_ptrf_apps.paa.api.serializers.fonte_recurso_paa_serializer import FonteRecursoPaaSerializer


class RecursoProprioPaaCreateSerializer(serializers.ModelSerializer):
    """
    Serializer responsável por validar, criar, atualizar e serializar
    os dados de um RecursoProprioPaaCreateSerializer.

    Além dos campos do modelo, expõe campos calculados para apresentação.
    """
    paa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Paa.objects.all()
    )

    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Associacao.objects.all()
    )

    fonte_recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=FonteRecursoPaa.objects.all()
    )
    confirmar_limpeza_prioridades_paa = serializers.BooleanField(
        required=False,
        default=False,
        write_only=True,
        help_text='Se True, confirma a limpeza do valor das prioridades do PAA impactadas.'
    )

    class Meta:
        model = RecursoProprioPaa
        fields = ('id', 'paa', 'uuid', 'associacao', 'fonte_recurso', 'data_prevista', 'descricao', 'valor',
                  'confirmar_limpeza_prioridades_paa')

    def validate(self, attrs: dict) -> dict:
        """
        Valida os dados para criação de um RecursoProprioPaa.

        Realiza as seguintes verificações na ordem a seguir:

        1. Verifica se não foi informado o paa, se não, retorna ValidationError;
        2. Bloqueia edição quando o documento final do ciclo atual já foi gerado;
        3. Verificar prioridades do paa impactadas.

        Args:
            attrs (dict): Dados RecursoProprioPaa
            para realizar as operações.

        Returns:
            dict: Dados validados.

        Raises:
            serializers.ValidationError: Caso o alguma validação não passe.
        """
        if not attrs.get('paa') and not self.instance:
            raise serializers.ValidationError({'paa': 'PAA não informado.'})

        paa = attrs.get('paa') or (self.instance.paa if self.instance else None)

        # Resolve paa quando é string UUID
        if paa and isinstance(paa, str):
            try:
                paa = Paa.by_uuid(paa)
            except Paa.DoesNotExist:
                raise serializers.ValidationError({'mensagem': 'PAA não encontrado!'})

        # Bloqueia edição quando o documento final do ciclo atual foi gerado
        if paa.status_em_retificacao:
            from sme_ptrf_apps.paa.services.ciclo_retificacao_service import CicloRetificacaoService
            tem_doc_final = CicloRetificacaoService(paa).tem_documento_final_concluido
        else:
            tem_doc_final = paa.get_tem_documento_final_concluido()

        if tem_doc_final:
            raise serializers.ValidationError({
                'mensagem': (
                    'Não é possível editar receitas previstas de Recurso Próprio após a '
                    'geração do documento final do PAA.')
            })

        # Verifica prioridades do PAA impactadas
        self._verificar_prioridades_paa_impactadas(attrs, self.instance)
        return super().validate(attrs)

    def _verificar_prioridades_paa_impactadas(self, attrs: dict, instance: RecursoProprioPaa) -> list:
        """
        Verifica se há prioridades do PAA que serão impactadas.
        """
        from sme_ptrf_apps.paa.services import PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService

        confirmar_limpeza = attrs.get('confirmar_limpeza_prioridades_paa', False)

        prioridades_impactadas = []
        service = PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService(attrs, instance)
        prioridades = service.verificar_prioridades_impactadas()
        prioridades_impactadas.extend(prioridades)

        if prioridades_impactadas and not confirmar_limpeza:
            raise serializers.ValidationError({
                "confirmar": (
                    "Existem prioridades cadastradas que utilizam o valor da receita prevista. "
                    "Será necessário revisar as prioridades para atualizar o valor total.")
            })

    def _limpar_prioridades_paa(self, recurso_attrs: dict, instance_despesa: RecursoProprioPaa) -> None:
        """
        Limpa o valor_total das prioridades do PAA impactadas.
        """
        from sme_ptrf_apps.paa.services import PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService

        service = PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService(
            recurso_attrs, instance_despesa)
        service.limpar_valor_prioridades_impactadas()

    @transaction.atomic
    def update(self, instance: RecursoProprioPaa, validated_data: dict) -> RecursoProprioPaa:
        """
        Atualiza uma instância de RecursoProprioPaa.

        Verificação:
            1. Verifica se é para realizar limpeza na prioridade, se sim,
                limpa prioridades do PAA, com dados e instance antes de salvar.

        Args:
            instance: (RecursoProprioPaa): Instâcia do RecursoProprioPaa.
            validated_data: Dados validados para ser feito a atualização.

        Returns:
            RecursoProprioPaa: Instância do RecursoProprioPaa atualizada.
        """
        # Remove flag de confirmação do validated_data (não é campo do model)
        confirmar_limpeza_prioridades = validated_data.pop('confirmar_limpeza_prioridades_paa', False)

        # Limpa prioridades do PAA se confirmado, com dados e instance antes de salvar
        if confirmar_limpeza_prioridades:
            self._limpar_prioridades_paa(validated_data, instance)

        return super().update(instance, validated_data)

    def create(self, validated_data: dict) -> RecursoProprioPaa:
        """
        Cria uma nova instância de RecursoProprioPaa.

        Verificação:
            1. Retira a confirmação de limpar prioridades do PAA antes de salvar.

        Args:
            validated_data (dict): Dados validados para criação da RecursoProprioPaa.

        Returns:
            RecursoProprioPaa: Instância do RecursoProprioPaa criada.
        """
        validated_data.pop('confirmar_limpeza_prioridades_paa', False)
        return super().create(validated_data)


class RecursoProprioPaaListSerializer(serializers.ModelSerializer):
    """
    Serializer responsável por serializar
    os dados de um RecursoProprioPaaListSerializer.

    Além dos campos do modelo, expõe campos calculados para apresentação.
    """
    paa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Paa.objects.all()
    )
    fonte_recurso = FonteRecursoPaaSerializer()
    valor = serializers.FloatField()
    associacao = serializers.SerializerMethodField('get_associacao_uuid')
    alteracao = serializers.SerializerMethodField()

    def get_alteracao(self, obj: RecursoProprioPaa) -> str:
        """
        Retorna a ação de alteração associada ao objeto.

        A ação é obtida a partir do contexto do serializer, considerando a
        seção correspondente às atividades estatutárias globais ou do PAA.

        Args:
            obj: Instância da atividade estatutária.

        Returns:
            str | None: A ação registrada para o objeto ou ``None`` caso não
            exista.
        """
        alteracoes = self.context.get('alteracoes', {})
        if not alteracoes:
            return None
        secao_key = 'receitas_recurso_proprio'
        print(alteracoes.get(secao_key, {}))
        item = alteracoes.get(secao_key, {}).get(str(obj.uuid))
        return item.get('acao') if item else None

    def get_associacao_uuid(self, obj) -> str:
        """retorna o UUID da associação associado ao RecursoProprioPaa"""
        return obj.associacao.uuid

    class Meta:
        model = RecursoProprioPaa
        fields = (
            'id', 'paa', 'uuid', 'associacao', 'fonte_recurso', 'data_prevista', 'descricao', 'valor', 'alteracao'
        )


class RecursoProprioPaaListDocumentoPaaSerializer(serializers.ModelSerializer):
    """
    Serializer responsável por serializar os dados de um RecursoProprioPaa.

    Além dos campos do modelo, expõe campos calculados para apresentação.
    """
    data_prevista = serializers.SerializerMethodField()
    paa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Paa.objects.all()
    )
    fonte_recurso = FonteRecursoPaaSerializer()
    valor = serializers.FloatField()
    associacao = serializers.SerializerMethodField('get_associacao_uuid')

    def get_data_prevista(self, obj: RecursoProprioPaa) -> str:
        """Retorna a data prevista no formado DD/MM/YYYY"""
        return obj.data_prevista.strftime("%d/%m/%Y")

    def get_associacao_uuid(self, obj: RecursoProprioPaa) -> str:
        """Retorna o UUID da associação"""
        return obj.associacao.uuid

    class Meta:
        model = RecursoProprioPaa
        fields = ('id', 'paa', 'uuid', 'associacao', 'fonte_recurso', 'data_prevista', 'descricao', 'valor')

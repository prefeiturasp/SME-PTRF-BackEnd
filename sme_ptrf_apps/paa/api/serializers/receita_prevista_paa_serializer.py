from rest_framework import serializers
from django.db import transaction
from sme_ptrf_apps.paa.models import ReceitaPrevistaPaa, Paa
from sme_ptrf_apps.core.models import AcaoAssociacao


class ReceitaPrevistaPaaSerializer(serializers.ModelSerializer):
    """
    Serializer responsável por validar, criar, atualizar e serializar
    os dados de uma Receita Prevista PAA.

    Além dos campos do modelo, expõe campos calculados para apresentação.
    """
    paa = serializers.SlugRelatedField(queryset=Paa.objects.all(), slug_field='uuid')
    acao_associacao = serializers.SlugRelatedField(queryset=AcaoAssociacao.objects.all(), slug_field='uuid')
    acao_associacao_objeto = serializers.SerializerMethodField()
    confirmar_limpeza_prioridades_paa = serializers.BooleanField(
        required=False,
        default=False,
        write_only=True,
        help_text='Se True, confirma a limpeza do valor das prioridades do PAA impactadas.'
    )

    def get_acao_associacao_objeto(self, obj: ReceitaPrevistaPaa) -> dict | None:
        """Monta um objeto com as informações da ação associação e retorna o objeto"""
        if obj.acao_associacao:
            acao = {
                'uuid': str(obj.acao_associacao.acao.uuid),
                'id': obj.acao_associacao.acao.id,
                'nome': obj.acao_associacao.acao.nome,
            }
            return {
                'uuid': obj.acao_associacao.uuid,
                'id': obj.acao_associacao.id,
                'acao_id': obj.acao_associacao.acao_id,
                'associacao_id': obj.acao_associacao.associacao_id,
                'status': obj.acao_associacao.status,
                'acao_objeto': acao,
            }
        return None

    class Meta:
        model = ReceitaPrevistaPaa
        fields = ('id', 'uuid', 'paa', 'acao_associacao', 'acao_associacao_objeto',
                  'previsao_valor_capital', 'previsao_valor_custeio', 'previsao_valor_livre',
                  'saldo_congelado_custeio', 'saldo_congelado_capital', 'saldo_congelado_livre',
                  'confirmar_limpeza_prioridades_paa')
        read_only_fields = ('uuid', 'saldo_congelado_custeio', 'saldo_congelado_capital',
                            'saldo_congelado_livre', 'acao_associacao_objeto', 'criado_em', 'alterado_em',
                            'confirmar_limpeza_prioridades_paa')

    def validate(self, attrs: dict) -> dict:
        """
        Valida os dados para criação de um PAA.

        Realiza as seguintes verificações na ordem a seguir:

        1. Verifica se não foi informado o paa, se não, retorna ValidationError;
        2. Verifica se não foi informado a ação associação, se não, retorna ValidationError;
        3. Bloqueia edição quando o documento final do ciclo atual foi gerado;
        4. Verifica prioridades do PAA impactadas;

        Args:
            attrs (dict): Dados ReceitaPrevistaOutroRecursoPeriodo
            para realizar as operações.

        Returns:
            dict: Dados validados.

        Raises:
            serializers.ValidationError: Caso o Paa não seja informado.
        """
        if not attrs.get('paa') and not self.instance:
            # Valida se paa foi informada no create
            raise serializers.ValidationError({'paa': 'O campo PAA é obrigatório.'})

        if not attrs.get('acao_associacao') and not self.instance:
            # Valida se acao_associacao foi informada no create
            raise serializers.ValidationError({'acao_associacao': 'O campo Ação de Associação é obrigatório.'})

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
                'mensagem': 'Não é possível editar receitas previstas após a geração do documento final do PAA.'
            })

        # Verifica prioridades do PAA impactadas
        self._verificar_prioridades_paa_impactadas(attrs, self.instance)

        return super().validate(attrs)

    def _verificar_prioridades_paa_impactadas(self, attrs: dict, instance: ReceitaPrevistaPaa) -> list:
        """
        Verifica se há prioridades do PAA que serão impactadas.
        """
        from sme_ptrf_apps.paa.services import PrioridadesPaaImpactadasReceitasPrevistasPTRFService

        confirmar_limpeza = attrs.get('confirmar_limpeza_prioridades_paa', False)

        prioridades_impactadas = []
        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(attrs, instance)
        prioridades = service.verificar_prioridades_impactadas()
        prioridades_impactadas.extend(prioridades)

        if prioridades_impactadas and not confirmar_limpeza:
            raise serializers.ValidationError({
                "confirmar": (
                    "Existem prioridades cadastradas que utilizam o valor da receita prevista. "
                    "Será necessário revisar as prioridades para atualizar o valor total.")
            })

    def _limpar_prioridades_paa(self, receita_prevista_attrs: dict, instance_despesa: ReceitaPrevistaPaa) -> None:
        """
        Limpa o valor_total das prioridades do PAA impactadas pelos rateios da despesa.
        """
        from sme_ptrf_apps.paa.services import PrioridadesPaaImpactadasReceitasPrevistasPTRFService

        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(receita_prevista_attrs, instance_despesa)
        service.limpar_valor_prioridades_impactadas()

    @transaction.atomic
    def update(self, instance: ReceitaPrevistaPaa, validated_data: dict) -> ReceitaPrevistaPaa:
        """
        Atualiza uma nova instância de ReceitaPrevistaPaa.

        Args:
            instance: (ReceitaPrevistaOutroRecursoPeriodo): Instâcia da Receita Prevista do Outro Recurso de um Período.
            validated_data (dict): Dados validados para atualização do ReceitaPrevistaPaa.

        Returns:
            ReceitaPrevistaOutroRecursoPeriodo: Instância do ReceitaPrevistaOutroRecursoPeriodo atualizada.
        """
        # Remove flag de confirmação do validated_data (não é campo do model)
        confirmar_limpeza_prioridades = validated_data.pop('confirmar_limpeza_prioridades_paa', False)

        # Limpa prioridades do PAA se confirmado, com dados e instance antes de salvar
        if confirmar_limpeza_prioridades:
            self._limpar_prioridades_paa(validated_data, instance)

        return super().update(instance, validated_data)

    def create(self, validated_data: dict) -> ReceitaPrevistaPaa:
        """
        Atualiza uma nova instância de ReceitaPrevistaOutroRecursoPeriodo.

        Args:
            validated_data (dict): Dados validados para criação do PAA.

        Returns:
            ReceitaPrevistaOutroRecursoPeriodo: Instância do ReceitaPrevistaOutroRecursoPeriodo criada.
        """
        validated_data.pop('confirmar_limpeza_prioridades_paa', False)
        return super().create(validated_data)

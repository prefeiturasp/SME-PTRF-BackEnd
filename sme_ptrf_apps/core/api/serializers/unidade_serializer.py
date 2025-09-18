from rest_framework import serializers

from ...models import Unidade


class DreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidade
        fields = ('uuid', 'codigo_eol', 'tipo_unidade', 'nome', 'sigla')


class UnidadeLookUpSerializer(serializers.ModelSerializer):
    dre = DreSerializer()

    class Meta:
        model = Unidade
        fields = ('uuid', 'codigo_eol', 'tipo_unidade', 'nome', 'nome_com_tipo', 'sigla', 'dre')


class UnidadeSerializer(serializers.ModelSerializer):
    dre = DreSerializer()

    class Meta:
        model = Unidade
        fields = (
            'uuid',
            'codigo_eol',
            'tipo_unidade',
            'nome',
            'sigla',
            'dre',
            'email',
            'telefone',
            'tipo_logradouro',
            'logradouro',
            'numero',
            'complemento',
            'bairro',
            'cep',
            'qtd_alunos',
            'diretor_nome',
            'dre_cnpj',
            'dre_diretor_regional_rf',
            'dre_diretor_regional_nome',
            'dre_designacao_portaria',
            'dre_designacao_ano',
            'observacao'
        )


class UnidadeInfoAtaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidade
        fields = ('tipo_unidade', 'nome')


class UnidadeListEmAssociacoesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidade
        fields = ('uuid', 'codigo_eol', 'nome_com_tipo', 'nome_dre')


class UnidadeListSerializer(serializers.ModelSerializer):
    associacao_uuid = serializers.SerializerMethodField('get_associacao_uuid')
    associacao_nome = serializers.SerializerMethodField('get_associacao_nome')
    visao = serializers.SerializerMethodField('get_visao')
    data_de_encerramento_associacao = serializers.SerializerMethodField('get_data_de_encerramento_associacao')

    informacoes = serializers.SerializerMethodField(method_name='get_tags_da_associacao', required=False)

    def get_associacao_uuid(self, obj):
        return obj.associacoes.first().uuid if obj.associacoes.exists() else ''

    def get_associacao_nome(self, obj):
        return obj.associacoes.first().nome if obj.associacoes.exists() else ''

    def get_visao(self, obj):
        return 'DRE' if obj.tipo_unidade == 'DRE' else 'UE'

    def get_data_de_encerramento_associacao(self, obj):
        return obj.associacoes.first().data_de_encerramento if obj.associacoes.exists() else None

    def get_tags_da_associacao(self, obj):
        return obj.associacoes.first().tags_de_informacao if obj.associacoes.exists() else []

    class Meta:
        model = Unidade
        fields = (
            'uuid',
            'codigo_eol',
            'nome_com_tipo',
            'nome_dre',
            'nome',
            'tipo_unidade',
            'associacao_uuid',
            'associacao_nome',
            'visao',
            'data_de_encerramento_associacao',
            'tooltip_associacao_encerrada',
            'informacoes'
        )


class UnidadeCreateSerializer(serializers.ModelSerializer):
    nome_dre = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)
    
    class Meta:
        model = Unidade
        fields = ('codigo_eol', 'nome', 'email', 'telefone', 'numero',
                  'tipo_logradouro', 'logradouro', 'bairro', 'cep', 'tipo_unidade', 'observacao', 'nome_dre')
    
    def to_internal_value(self, data):
        # Garantir que o campo nome_dre seja preservado
        internal_value = super().to_internal_value(data)
        if 'nome_dre' in data:
            internal_value['nome_dre'] = data['nome_dre']
        return internal_value
    
    def create(self, validated_data):
        nome_dre = validated_data.pop('nome_dre', None)
        
        # Buscar DRE pelo nome se fornecido
        dre = None
        if nome_dre:
            try:
                # Busca exata primeiro
                dre = Unidade.dres.filter(nome__iexact=nome_dre).first()
                
                # Se não encontrar, busca por contém (case insensitive)
                if not dre:
                    dre = Unidade.dres.filter(nome__unaccent__icontains=nome_dre).first()
                    
            except Exception:
                # Se houver erro na busca, continua sem DRE
                pass
        
        unidade = Unidade.objects.create(**validated_data)
        
        # Vincular DRE se encontrada
        if dre:
            unidade.dre = dre
            unidade.save()
            
        return unidade

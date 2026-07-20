from rest_framework import serializers

from ...models import TipoAcertoDocumento, Recurso, SolicitacaoAcertoDocumento
from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict
from .tipo_documento_prestacao_conta_serializer import TipoDocumentoPrestacaoContaSerializer


class TipoAcertoDocumentoListaSerializer(serializers.ModelSerializer):
    tipos_documento_prestacao = TipoDocumentoPrestacaoContaSerializer(many=True)
    recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Recurso.objects.all()
    )

    class Meta:
        model = TipoAcertoDocumento
        fields = ('id', 'uuid', 'nome', 'categoria', 'ativo',
                  'tipos_documento_prestacao', 'pode_alterar_saldo_conciliacao', 'recurso')


class TipoAcertoDocumentoSerializer(serializers.ModelSerializer):
    recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Recurso.objects.all()
    )

    def create(self, validated_data):
        nome = validated_data['nome']
        recurso = validated_data.get('recurso', None)
        categoria = validated_data.get('categoria', None)
        nome_ja_cadastrado = TipoAcertoDocumento.objects.filter(
            nome__iexact=nome,
            categoria=categoria,
            recurso=recurso,
        ).all()

        if nome_ja_cadastrado:
            raise serializers.ValidationError(
                {"detail": "Já existe um tipo de acerto de documento com esse nome e categoria para esse recurso."}
            )

        try:
            tipos_documentos_prestacao = validated_data.pop("tipos_documento_prestacao")
        except KeyError:
            tipos_documentos_prestacao = []

        tipo_documento_criado = TipoAcertoDocumento.objects.create(**validated_data)

        if not tipos_documentos_prestacao:
            raise serializers.ValidationError({
                "detail": ("Para salvar um tipo de acerto de documento é necessário informar "
                           "pelo menos um documento relacionado")
            })
        tipo_documento_criado.adiciona_tipos_documentos_prestacao(tipos_documentos_prestacao)

        return tipo_documento_criado

    def update(self, instance, validated_data):
        # Validar se houve alguma mudança
        houve_alteracao = self._verifica_alteracoes(instance, validated_data)

        if not houve_alteracao:
            return instance

        nome = validated_data.get("nome", None)
        categoria = validated_data.get("categoria", None)
        recurso = validated_data.get('recurso', None)

        if nome:
            nome_ja_cadastrado = TipoAcertoDocumento.objects.filter(
                nome__iexact=nome,
                categoria=categoria,
                recurso=recurso
            ).exclude(id=instance.id).exists()

            if nome_ja_cadastrado:
                raise serializers.ValidationError(
                    {"non_field_errors": "Já existe um tipo de acerto de documento com esse nome e categoria para esse recurso."}
                )

        possui_tipos_documentos_prestacao = validated_data.get("tipos_documento_prestacao", None)
        if possui_tipos_documentos_prestacao:
            tipos_documentos_prestacao = validated_data.pop("tipos_documento_prestacao")
            instance.adiciona_tipos_documentos_prestacao(tipos_documentos_prestacao)

        if categoria != instance.categoria:
            exists = SolicitacaoAcertoDocumento.objects.filter(
                tipo_acerto=instance
            ).exclude(id=instance.id).exists()
   
            if exists:
                raise serializers.ValidationError(
                    {"non_field_errors": "Não é permitido alterar. Pois existem solicitações de acertos vinculadas."}
                )

        update_instance_from_dict(instance, validated_data, save=True)

        return instance

    def _verifica_alteracoes(self, instance, validated_data):
        """
        Verifica se houve alguma alteração nos dados.
        Retorna True se houve alteração, False caso contrário.
        """
        campos_verificar = ['nome', 'categoria', 'ativo', 'pode_alterar_saldo_conciliacao', 'recurso', 'tipos_documento_prestacao']
 
        for campo in campos_verificar:
            if campo not in validated_data:
                continue
         
            valor_novo = validated_data[campo]
            
            if campo == 'tipos_documento_prestacao':
                # Comparar muitos-para-muitos
                ids_atuais = set(instance.tipos_documento_prestacao.values_list('id', flat=True))
                ids_novos = set([doc.id for doc in valor_novo]) if valor_novo else set()
                if ids_atuais != ids_novos:
                    return True
            elif campo == 'recurso':
                # Comparar recurso por UUID
                if instance.recurso != valor_novo:
                    return True
            else:
                # Comparar campos simples
                valor_atual = getattr(instance, campo)
                if valor_atual != valor_novo:
                    return True
        
        return False

    class Meta:
        model = TipoAcertoDocumento
        fields = ('id', 'uuid', 'nome', 'categoria', 'ativo',
                  'tipos_documento_prestacao', 'pode_alterar_saldo_conciliacao', 'recurso')

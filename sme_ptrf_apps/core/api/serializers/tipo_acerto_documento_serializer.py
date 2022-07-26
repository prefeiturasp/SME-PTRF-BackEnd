from rest_framework import serializers

from ...models import TipoAcertoDocumento, TipoDocumentoPrestacaoConta
from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict
from .tipo_documento_prestacao_conta_serializer import TipoDocumentoPrestacaoContaSerializer


class TipoAcertoDocumentoListaSerializer(serializers.ModelSerializer):
    tipos_documento_prestacao = TipoDocumentoPrestacaoContaSerializer(many=True)

    class Meta:
        model = TipoAcertoDocumento
        fields = ('id', 'uuid', 'nome', 'categoria', 'ativo', 'tipos_documento_prestacao')


class TipoAcertoDocumentoSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        nome = validated_data['nome']
        nome_ja_cadastrado = TipoAcertoDocumento.objects.filter(nome=nome).all()

        if nome_ja_cadastrado:
            raise serializers.ValidationError(
                {"detail": "Já existe um tipo de acerto de documento com esse nome."}
            )

        try:
            tipos_documentos_prestacao = validated_data.pop("tipos_documento_prestacao")
        except KeyError:
            tipos_documentos_prestacao = []

        tipo_documento_criado = TipoAcertoDocumento.objects.create(**validated_data)

        if not tipos_documentos_prestacao:
            raise serializers.ValidationError({
                "detail": "Para salvar um tipo de acerto de documento é necessário informar pelo menos um documento relacionado"
            })
        tipo_documento_criado.adiciona_tipos_documentos_prestacao(tipos_documentos_prestacao)

        return tipo_documento_criado

    def update(self, instance, validated_data):
        nome = validated_data.get("nome", None)

        if nome:
            nome_ja_cadastrado = TipoAcertoDocumento.objects.filter(nome=nome).all()

            if nome_ja_cadastrado:
                raise serializers.ValidationError(
                    {"detail": "Já existe um tipo de acerto de documento com esse nome."}
                )

        possui_tipos_documentos_prestacao = validated_data.get("tipos_documento_prestacao", None)
        if possui_tipos_documentos_prestacao:
            tipos_documentos_prestacao = validated_data.pop("tipos_documento_prestacao")
            instance.adiciona_tipos_documentos_prestacao(tipos_documentos_prestacao)

        update_instance_from_dict(instance, validated_data, save=True)

        return instance

    class Meta:
        model = TipoAcertoDocumento
        fields = ('id', 'uuid', 'nome', 'categoria', 'ativo', 'tipos_documento_prestacao')

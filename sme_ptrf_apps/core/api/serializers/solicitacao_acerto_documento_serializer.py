from rest_framework import serializers

from ...models import SolicitacaoAcertoDocumento, AnaliseDocumentoPrestacaoConta
from ..serializers.tipo_acerto_documento_serializer import TipoAcertoDocumentoSerializer


class SolicitacaoAcertoDocumentoRetrieveSerializer(serializers.ModelSerializer):
    analise_documento = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AnaliseDocumentoPrestacaoConta.objects.all()
    )

    tipo_acerto = TipoAcertoDocumentoSerializer(many=False)

    class Meta:
        model = SolicitacaoAcertoDocumento
        fields = ('analise_documento', 'tipo_acerto', 'detalhamento', 'id', 'uuid', 'copiado', 'status_realizacao',
                  'justificativa', 'esclarecimentos', 'texto_do_acerto_do_tipo_edicao_de_informacao')

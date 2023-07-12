from rest_framework import mixins, status

from rest_framework.permissions import IsAuthenticated

from rest_framework.viewsets import GenericViewSet

from ..serializers.tipo_conta_serializer import TipoContaSerializer
from ...models import TipoConta
from ...models import ContaAssociacao

from rest_framework.response import Response

class TiposContaViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        GenericViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = TipoConta.objects.all().order_by('nome')
    serializer_class = TipoContaSerializer
    
    def get_queryset(self):
        qs = TipoConta.objects.all()

        nome = self.request.query_params.get('nome')
        
        if nome is not None:
            qs = qs.filter(nome__unaccent__icontains=nome)
            
        return qs.order_by('nome')
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        tem_cadastrada_com_esse_tipo = ContaAssociacao.objects.filter(tipo_conta=instance).exists()
        if tem_cadastrada_com_esse_tipo:
            return Response({"erro": "Essa operação não pode ser realizada. Há associações cadastradas com esse tipo de conta."}, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_destroy(instance)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

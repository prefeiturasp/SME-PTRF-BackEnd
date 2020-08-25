from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from ...models import FaqCategoria

from ..serializers.faq_categoria_serializer import FaqCategoriaSerializer


class FaqCategoriasViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    queryset = FaqCategoria.objects.all()
    serializer_class = FaqCategoriaSerializer

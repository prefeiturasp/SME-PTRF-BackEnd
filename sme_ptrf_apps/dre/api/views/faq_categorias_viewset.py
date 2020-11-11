from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ...models import FaqCategoria

from ..serializers.faq_categoria_serializer import FaqCategoriaSerializer


class FaqCategoriasViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = FaqCategoria.objects.all()
    serializer_class = FaqCategoriaSerializer

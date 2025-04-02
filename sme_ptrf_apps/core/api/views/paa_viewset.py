from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from sme_ptrf_apps.core.services.paa_service import gerar_arquivo_pdf_levantamento_prioridades_paa
from datetime import datetime

from sme_ptrf_apps.core.models import Associacao

from sme_ptrf_apps.users.permissoes import (
    PermissaoApiUe,
    PermissaoAPITodosComLeituraOuGravacao,
    PermissaoAPITodosComGravacao
)

from django.shortcuts import render

import logging
logger = logging.getLogger(__name__)

class PaaViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]

    @action(
      detail=False,
      methods=['get'],
      url_path='download-pdf-levantamento-prioridades',
      permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao]
    )
    def download_levantamento_prioridades_paa(self, request):
      
      associacao_uuid = self.request.query_params.get('associacao_uuid')
      associacao = Associacao.objects.filter(uuid=associacao_uuid).first()
      if associacao:
        nome_unidade = associacao.unidade.nome
        tipo_unidade = associacao.unidade.tipo_unidade
        associacao_nome = associacao.nome
      else:
        nome_unidade = None
        tipo_unidade = None
        associacao_nome = None

      dados = {
                "nome_associacao": associacao_nome,
                "nome_unidade": nome_unidade, 
                "tipo_unidade": tipo_unidade, 
                "username": request.user.username, 
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "ano": datetime.now().year
              }
      return gerar_arquivo_pdf_levantamento_prioridades_paa(dados)
    
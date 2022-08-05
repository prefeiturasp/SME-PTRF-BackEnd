import logging

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.models import Periodo, TipoConta, TipoDevolucaoAoTesouro, Unidade
from sme_ptrf_apps.receitas.models import DetalheTipoReceita
from sme_ptrf_apps.users.permissoes import (
    PermissaoApiDre,
    PermissaoAPIApenasDreComGravacao,
    PermissaoAPIApenasDreComLeituraOuGravacao
)

from ...models import RelatorioConsolidadoDRE, ConsolidadoDRE
from ...services import (
    informacoes_devolucoes_a_conta_ptrf,
    informacoes_devolucoes_ao_tesouro,
    informacoes_execucao_financeira,
    informacoes_execucao_financeira_unidades,
    status_de_geracao_do_relatorio,
    update_observacao_devolucao,
    retorna_informacoes_execucao_financeira_todas_as_contas
)
from ...tasks import gerar_lauda_txt_async

logger = logging.getLogger(__name__)


class RelatoriosConsolidadosDREViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    queryset = RelatorioConsolidadoDRE.objects.all()

    @action(detail=False, methods=['get'], url_path='fique-de-olho',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def fique_de_olho(self, request, uuid=None):
        from sme_ptrf_apps.dre.models import ParametroFiqueDeOlhoRelDre
        fique_de_olho = ParametroFiqueDeOlhoRelDre.get().fique_de_olho
        return Response({'detail': fique_de_olho}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='update-fique-de-olho',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def update_fique_de_olho(self, request, uuid=None):

        texto_fique_de_olho = request.data.get('fique_de_olho', None)

        if texto_fique_de_olho is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'update-fique-de-olho',
                'mensagem': 'Faltou informar o campo Fique de Olho.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        from sme_ptrf_apps.dre.models import ParametroFiqueDeOlhoRelDre

        # Pegando o objeto ParametroFiqueDeOlhoPc
        obj_fique_de_olho = ParametroFiqueDeOlhoRelDre.get()

        # Atribuindo ao objeto-> propriedade (fique_de_olho), o request.data.get('fique_de_olho', None)
        obj_fique_de_olho.fique_de_olho = texto_fique_de_olho

        # E por fim Salvando
        obj_fique_de_olho.save()

        return Response({'detail': 'Salvo com sucesso'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='status-relatorio',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def status_relatorio(self, request):
        from rest_framework import status

        # Determina a DRE
        dre_uuid = self.request.query_params.get('dre')

        if not dre_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'status-relatorio',
                'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except Unidade.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o tipo de conta
        tipo_conta_uuid = self.request.query_params.get('tipo_conta')

        if not tipo_conta_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'status-relatorio',
                'mensagem': 'Faltou informar o uuid do tipo de conta. ?tipo_conta=uuid_do_tipo_conta'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            tipo_conta = TipoConta.objects.get(uuid=tipo_conta_uuid)
        except TipoConta.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto tipo de conta para o uuid {tipo_conta_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o período
        periodo_uuid = self.request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'status-relatorio',
                'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        status = status_de_geracao_do_relatorio(dre=dre, periodo=periodo, tipo_conta=tipo_conta)

        return Response(status)

    @action(detail=False, methods=['get'], url_path='info-execucao-financeira',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def info_execucao_financeira(self, request):
        from rest_framework import status

        # Determina a DRE
        dre_uuid = self.request.query_params.get('dre')

        if not dre_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'info-execucao-financeira',
                'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except Unidade.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o período
        periodo_uuid = self.request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'info-execucao-financeira',
                'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina se existe o ConsolidadoDRE
        consolidado_dre_uuid = self.request.query_params.get('consolidado_dre')
        consolidado_dre = None
        if consolidado_dre_uuid:
            try:
                consolidado_dre = ConsolidadoDRE.objects.get(uuid=consolidado_dre_uuid)
            except ConsolidadoDRE.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        info = retorna_informacoes_execucao_financeira_todas_as_contas(dre=dre, periodo=periodo, consolidado_dre=consolidado_dre)

        return Response(info)

    @action(detail=False, methods=['get'], url_path='info-devolucoes-conta',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def info_devolucoes_conta(self, request):
        from rest_framework import status

        # Determina a DRE
        dre_uuid = self.request.query_params.get('dre')

        if not dre_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'info-devolucoes-conta',
                'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except Unidade.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o tipo de conta
        tipo_conta_uuid = self.request.query_params.get('tipo_conta')

        if not tipo_conta_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'info-devolucoes-conta',
                'mensagem': 'Faltou informar o uuid do tipo de conta. ?tipo_conta=uuid_do_tipo_conta'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            tipo_conta = TipoConta.objects.get(uuid=tipo_conta_uuid)
        except TipoConta.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto tipo de conta para o uuid {tipo_conta_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o período
        periodo_uuid = self.request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'info-devolucoes-conta',
                'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        info = informacoes_devolucoes_a_conta_ptrf(dre=dre, periodo=periodo, tipo_conta=tipo_conta)

        return Response(info)

    @action(detail=False, methods=['get'], url_path='info-devolucoes-ao-tesouro',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def info_devolucoes_ao_tesouro(self, request):
        from rest_framework import status

        # Determina a DRE
        dre_uuid = self.request.query_params.get('dre')

        if not dre_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'info-devolucoes-ao-tesouro',
                'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except Unidade.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o tipo de conta
        tipo_conta_uuid = self.request.query_params.get('tipo_conta')

        if not tipo_conta_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'info-devolucoes-ao-tesouro',
                'mensagem': 'Faltou informar o uuid do tipo de conta. ?tipo_conta=uuid_do_tipo_conta'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            tipo_conta = TipoConta.objects.get(uuid=tipo_conta_uuid)
        except TipoConta.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto tipo de conta para o uuid {tipo_conta_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o período
        periodo_uuid = self.request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'info-devolucoes-ao-tesouro',
                'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        info = informacoes_devolucoes_ao_tesouro(dre=dre, periodo=periodo, tipo_conta=tipo_conta)

        return Response(info)

    @action(detail=False, methods=['get'], url_path='info-execucao-financeira-unidades',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def info_execucao_financeira_unidades(self, request):
        from rest_framework import status

        # Determina a DRE
        dre_uuid = self.request.query_params.get('dre')

        if not dre_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'info-execucao-financeira-unidades',
                'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except Unidade.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o tipo de conta
        tipo_conta_uuid = self.request.query_params.get('tipo_conta')

        if not tipo_conta_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'info-execucao-financeira-unidades',
                'mensagem': 'Faltou informar o uuid do tipo de conta. ?tipo_conta=uuid_do_tipo_conta'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            tipo_conta = TipoConta.objects.get(uuid=tipo_conta_uuid)
        except TipoConta.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto tipo de conta para o uuid {tipo_conta_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o período
        periodo_uuid = self.request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'info-execucao-financeira-unidades',
                'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Pega filtros
        nome = self.request.query_params.get('nome')
        tipo_unidade = self.request.query_params.get('tipo_unidade')
        status = self.request.query_params.get('status')

        info = informacoes_execucao_financeira_unidades(
            dre=dre,
            periodo=periodo,
            tipo_conta=tipo_conta,
            filtro_nome=nome,
            filtro_tipo_unidade=tipo_unidade,
            filtro_status=status,
        )

        return Response(info)

    @action(detail=False, methods=['put'], url_path='update-observacao-devolucoes-ao-tesouro',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def update_observacao_devolucoes_ao_tesouro(self, request):
        from rest_framework import status

        # Determina a DRE
        dre_uuid = self.request.query_params.get('dre')

        if not dre_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'update-observacao-devolucoes-ao-tesouro',
                'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except Unidade.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o tipo de conta
        tipo_conta_uuid = self.request.query_params.get('tipo_conta')

        if not tipo_conta_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'update-observacao-devolucoes-ao-tesouro',
                'mensagem': 'Faltou informar o uuid do tipo de conta. ?tipo_conta=uuid_do_tipo_conta'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            tipo_conta = TipoConta.objects.get(uuid=tipo_conta_uuid)
        except TipoConta.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto tipo de conta para o uuid {tipo_conta_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o período
        periodo_uuid = self.request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'update-observacao-devolucoes-ao-tesouro',
                'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o tipo de devolução ao tesouro
        tipo_uuid = self.request.query_params.get('tipo_devolucao')

        if not tipo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'update-observacao-devolucoes-ao-tesouro',
                'mensagem': 'Faltou informar o uuid do tipo de devolução ao tesouro. ?tipo_devolucao=tipo_uuid'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            tipo_devolucao = TipoDevolucaoAoTesouro.objects.get(uuid=tipo_uuid)
        except TipoDevolucaoAoTesouro.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto tipo devolução ao tesouro para o uuid {tipo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        observacao = request.data.get('observacao', '')

        info = update_observacao_devolucao(dre=dre, tipo_conta=tipo_conta, periodo=periodo, tipo_devolucao='TESOURO',
                                           subtipo_devolucao=tipo_devolucao, observacao=observacao)

        return Response(info)

    @action(detail=False, methods=['put'], url_path='update-observacao-devolucoes-a-conta',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def update_observacao_devolucoes_a_conta(self, request):
        from rest_framework import status

        # Determina a DRE
        dre_uuid = self.request.query_params.get('dre')

        if not dre_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'update-observacao-devolucoes-a-conta',
                'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except Unidade.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        tipo_conta_uuid = self.request.query_params.get('tipo_conta')
        # Determina o tipo de conta

        if not tipo_conta_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'update-observacao-devolucoes-a-conta',
                'mensagem': 'Faltou informar o uuid do tipo de conta. ?tipo_conta=uuid_do_tipo_conta'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            tipo_conta = TipoConta.objects.get(uuid=tipo_conta_uuid)
        except TipoConta.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto tipo de conta para o uuid {tipo_conta_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o período
        periodo_uuid = self.request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'update-observacao-devolucoes-a-conta',
                'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o tipo de devolução ao tesouro
        tipo_uuid = self.request.query_params.get('tipo_devolucao')

        if not tipo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'update-observacao-devolucoes-a-conta',
                'mensagem': 'Faltou informar o uuid do tipo de devolução à conta. ?tipo_devolucao=tipo_uuid'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            tipo_devolucao = DetalheTipoReceita.objects.get(uuid=tipo_uuid)
        except DetalheTipoReceita.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto DetalheTipoReceita para o uuid {tipo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        observacao = request.data.get('observacao', '')

        info = update_observacao_devolucao(dre=dre, tipo_conta=tipo_conta, periodo=periodo, tipo_devolucao='CONTA',
                                           subtipo_devolucao=tipo_devolucao, observacao=observacao)

        return Response(info)

    # TODO: Remover este método, pois foi criado o novo gerar_lauda dentro do Consolidado Dre
    @action(detail=False, url_path="gerar-lauda", methods=['post'],
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def gerar_lauda(self, request):
        dados = request.data

        if (
            not dados
            or not dados.get('dre_uuid')
            or not dados.get('periodo_uuid')
            or not dados.get('tipo_conta_uuid')
            or (dados.get('parcial') is None)
        ):
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar os uuids da dre, período, conta e parcial.'
            }
            logger.info('Erro ao gerar lauda: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        dre_uuid, periodo_uuid, tipo_conta_uuid = dados['dre_uuid'], dados['periodo_uuid'], dados['tipo_conta_uuid']

        try:
            Unidade.dres.get(uuid=dre_uuid)
        except Unidade.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            TipoConta.objects.get(uuid=tipo_conta_uuid)
        except TipoConta.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto tipo de conta para o uuid {tipo_conta_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            Periodo.objects.get(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            # gerar_lauda_csv_async.delay(
            #     dre_uuid,
            #     tipo_conta_uuid,
            #     periodo_uuid,
            #     dados['parcial'],
            #     request.user.username
            # )

            gerar_lauda_txt_async.delay(
                dre_uuid,
                tipo_conta_uuid,
                periodo_uuid,
                dados['parcial'],
                request.user.username
            )


        except Exception as err:
            erro = {
                'erro': 'problema_geracao_lauda',
                'mensagem': 'Ao gerar lauda.'
            }
            logger.info("Erro ao gerar lauda: %s", str(err))
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        return Response({"OK": "Lauda na fila para processamento."}, status=status.HTTP_201_CREATED)

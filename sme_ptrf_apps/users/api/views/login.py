import logging

from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from waffle import get_waffle_flag_model

from sme_ptrf_apps.users.api.services import AutenticacaoService
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.users.services.get_unidades_usuario_service import get_unidades_do_usuario
from sme_ptrf_apps.users.services.gestao_usuario_service import GestaoUsuarioService
from sme_ptrf_apps.users.services.login_usuario_service import LoginUsuarioService

User = get_user_model()
logger = logging.getLogger(__name__)


class LoginView(TokenObtainPairView):
    """
    POST auth/login/
    """

    permission_classes = (permissions.AllowAny,)

    # TODO remover antigo processo de login quando as features flags da gestão de usuários forem removidas
    # def post(self, request, *args, **kwargs):
    #     login = request.data.get("login", "")
    #     senha = request.data.get("senha", "")
    #
    #     try:
    #         response = AutenticacaoService.autentica(login, senha)
    #         if response.status_code == 200:
    #             user_dict = response.json()
    #             if 'login' in user_dict.keys():
    #                 try:
    #                     user = User.objects.get(username=user_dict['login'])
    #                     user.name = user_dict['nome']
    #                     user.email = user_dict['email']
    #                     user.set_password(senha)
    #                     user.save()
    #                 except User.DoesNotExist as e:
    #                     logger.info("Usuário %s não encontrado.", login)
    #                     return Response({'data': {'detail': 'Usuário não encontrado.'}},
    #                                     status=status.HTTP_401_UNAUTHORIZED)
    #
    #                 if not user.is_active:
    #                     logger.info("Usuário %s inativo no Admin do sistema.", login)
    #                     return Response({'detail': 'Você está sem autorização de acesso à aplicação no momento. Entre em contato com o administrador do Sig.Escola.'},
    #                                     status=status.HTTP_401_UNAUTHORIZED)
    #
    #                 request._full_data = {'username': user_dict['login'], 'password': senha}
    #                 resp = super().post(request, *args, **kwargs)
    #                 unidades = get_unidades_do_usuario(user)
    #
    #                 if not unidades:
    #                     associacao = Associacao.objects.first()
    #                 else:
    #                     associacao = Associacao.objects.filter(unidade__uuid=unidades[0]['uuid']).first()
    #
    #                 feature_flags = self.get_feature_flags_ativas(user)
    #
    #                 #TODO Rever esse bloco
    #                 # Mantive esse trecho da associação pra não quebrar o front até o mesmo tratar as mudanças de
    #                 # visões. Após o front ficar pronto esse trecho deve ser removido.
    #                 associacao_dict = {
    #                     'uuid': associacao.uuid,
    #                     'nome': associacao.nome,
    #                     'nome_escola': associacao.unidade.nome,
    #                     'tipo_escola': associacao.unidade.tipo_unidade} if associacao else {
    #                     'uuid': '',
    #                     'nome': '',
    #                     'nome_escola': '',
    #                     'tipo_escola': ''}
    #                 user_dict['associacao'] = associacao_dict
    #                 user_dict['unidades'] = unidades
    #                 user_dict['permissoes'] = self.get_user_permissions(user)
    #                 user_dict['feature_flags'] = feature_flags
    #
    #                 # Para manter compatibilidade com o front que espera o token no campo token
    #                 user_dict['token'] = resp.data['access']
    #
    #                 data = {**user_dict, **resp.data}
    #                 return Response(data)
    #         return Response(response.json(), response.status_code)
    #     except Exception as e:
    #         return Response({'data': {'detail': f'ERROR - {e}'}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        flags = get_waffle_flag_model()
        novo_suporte_unidades = flags.objects.filter(name='novo-suporte-unidades', everyone=True).exists()
        suporte = request.data.get("suporte", False)

        logger.info("Verificando se a flag <gestao-usuarios> está ativa...")

        if flags.objects.filter(name='gestao-usuarios', everyone=True).exists():
            logger.info("A flag está ativa, será utilizado o novo processo de login...")

            login = request.data.get("login", "")
            senha = request.data.get("senha", "")

            try:
                response = AutenticacaoService.autentica(login, senha)
                if response.status_code == 200:
                    user_dict = response.json()
                    if 'login' in user_dict.keys():
                        try:
                            user = User.objects.get(username=user_dict['login'])
                            user.name = user_dict['nome']
                            user.email = user_dict['email']
                            user.set_password(senha)
                            user.save()
                        except User.DoesNotExist as e:
                            logger.info("Usuário %s não encontrado.", login)
                            return Response({'data': {'detail': 'Usuário não encontrado.'}},
                                            status=status.HTTP_401_UNAUTHORIZED)

                        if not user.is_active:
                            logger.info("Usuário %s inativo no Admin do sistema.", login)
                            return Response({
                                'detail': 'Você está sem autorização de acesso à aplicação no momento. Entre em contato com o administrador do Sig.Escola.'},
                                status=status.HTTP_401_UNAUTHORIZED)

                        request._full_data = {'username': user_dict['login'], 'password': senha}
                        resp = super().post(request, *args, **kwargs)

                        gestao_usuario = GestaoUsuarioService(usuario=user)
                        
                        if novo_suporte_unidades:
                            login_service = LoginUsuarioService(usuario=user, gestao_usuario=gestao_usuario, suporte=suporte)
                            
                            if suporte:
                                user_dict['visoes'].remove('SME')
                        else:
                            login_service = LoginUsuarioService(usuario=user, gestao_usuario=gestao_usuario)

                        unidades = login_service.unidades_que_usuario_tem_acesso

                        if not unidades:
                            return Response({
                                'detail': 'Você não possui mais acesso ao sistema. Favor entrar em contato com sua escola ou com a DRE.'},
                                status=status.HTTP_401_UNAUTHORIZED)

                        associacao = Associacao.objects.filter(unidade__uuid=unidades[0]['uuid']).first()

                        feature_flags = self.get_feature_flags_ativas(user)

                        # TODO Rever esse bloco
                        # Mantive esse trecho da associação pra não quebrar o front até o mesmo tratar as mudanças de
                        # visões. Após o front ficar pronto esse trecho deve ser removido.
                        associacao_dict = {
                            'uuid': associacao.uuid,
                            'nome': associacao.nome,
                            'nome_escola': associacao.unidade.nome,
                            'tipo_escola': associacao.unidade.tipo_unidade} if associacao else {
                            'uuid': '',
                            'nome': '',
                            'nome_escola': '',
                            'tipo_escola': ''}
                        user_dict['associacao'] = associacao_dict
                        user_dict['unidades'] = unidades
                        user_dict['feature_flags'] = feature_flags
                        
                        if novo_suporte_unidades:
                            user_dict['permissoes'] = self.get_user_permissions(user, suporte)
                        else:
                            user_dict['permissoes'] = self.get_user_permissions(user)

                        perdeu_acesso_dict = {
                            "unidades_que_perdeu_acesso": login_service.unidades_que_perdeu_acesso,
                            "mensagem": login_service.mensagem_perca_acesso,
                            "exibe_modal": login_service.get_exibe_modal()
                        }
                        user_dict["info_perdeu_acesso"] = perdeu_acesso_dict

                        # Para manter compatibilidade com o front que espera o token no campo token
                        user_dict['token'] = resp.data['access']

                        data = {**user_dict, **resp.data}

                        return Response(data)
                return Response(response.json(), response.status_code)
            except Exception as e:
                return Response({'data': {'detail': f'ERROR - {e}'}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.info("A flag NÃO está ativa, será utilizado o antigo processo de login...")

            login = request.data.get("login", "")
            senha = request.data.get("senha", "")

            try:
                response = AutenticacaoService.autentica(login, senha)
                if response.status_code == 200:
                    user_dict = response.json()
                    if 'login' in user_dict.keys():
                        try:
                            user = User.objects.get(username=user_dict['login'])
                            user.name = user_dict['nome']
                            user.email = user_dict['email']
                            user.set_password(senha)
                            user.save()
                        except User.DoesNotExist as e:
                            logger.info("Usuário %s não encontrado.", login)
                            return Response({'data': {'detail': 'Usuário não encontrado.'}},
                                            status=status.HTTP_401_UNAUTHORIZED)

                        if not user.is_active:
                            logger.info("Usuário %s inativo no Admin do sistema.", login)
                            return Response({
                                'detail': 'Você está sem autorização de acesso à aplicação no momento. Entre em contato com o administrador do Sig.Escola.'},
                                status=status.HTTP_401_UNAUTHORIZED)

                        request._full_data = {'username': user_dict['login'], 'password': senha}
                        resp = super().post(request, *args, **kwargs)
                        
                        if novo_suporte_unidades:
                            unidades = get_unidades_do_usuario(user, suporte)
                        else:
                            unidades = get_unidades_do_usuario(user)

                        if not unidades:
                            associacao = Associacao.objects.first()
                        else:
                            associacao = Associacao.objects.filter(unidade__uuid=unidades[0]['uuid']).first()

                        feature_flags = self.get_feature_flags_ativas(user)

                        # TODO Rever esse bloco
                        # Mantive esse trecho da associação pra não quebrar o front até o mesmo tratar as mudanças de
                        # visões. Após o front ficar pronto esse trecho deve ser removido.
                        associacao_dict = {
                            'uuid': associacao.uuid,
                            'nome': associacao.nome,
                            'nome_escola': associacao.unidade.nome,
                            'tipo_escola': associacao.unidade.tipo_unidade} if associacao else {
                            'uuid': '',
                            'nome': '',
                            'nome_escola': '',
                            'tipo_escola': ''}
                        user_dict['associacao'] = associacao_dict
                        user_dict['unidades'] = unidades
                        user_dict['feature_flags'] = feature_flags
                        
                        if novo_suporte_unidades:
                            user_dict['permissoes'] = self.get_user_permissions(user, suporte)
                        else:
                            user_dict['permissoes'] = self.get_user_permissions(user)

                        # Para manter compatibilidade com o front que espera o token no campo token
                        user_dict['token'] = resp.data['access']

                        data = {**user_dict, **resp.data}
                        return Response(data)
                return Response(response.json(), response.status_code)
            except Exception as e:
                return Response({'data': {'detail': f'ERROR - {e}'}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
    def get_user_permissions(self, user, suporte=False):
        flags = get_waffle_flag_model()
        
        novo_suporte_unidades = flags.objects.filter(name='novo-suporte-unidades', everyone=True).exists()
        
        if novo_suporte_unidades:
            perms = []
            
            if suporte:
                groups_suporte = user.groups.filter(grupo__suporte=True)
                for group in groups_suporte:
                    for permission in group.permissions.all():
                        perms.append(permission.codename)
            else:
                groups = user.groups.filter(grupo__suporte=False)
                for group in groups:
                    for permission in group.permissions.all():
                        perms.append(permission.codename)
        else:
            perms = []
            for group in user.groups.all():
                for permission in group.permissions.all():
                    perms.append(permission.codename)
                    
        return perms

    def get_feature_flags_ativas(self, user):
        from django.http import HttpRequest

        # Criando um request com o usuário autenticado para que o waffle possa verificar as flags
        request_com_user = HttpRequest()
        request_com_user.META = self.request.META
        request_com_user.user = user

        Flag = get_waffle_flag_model()
        return [
            flag.name for flag in Flag.get_all()
            if flag.is_active(request_com_user)
        ]

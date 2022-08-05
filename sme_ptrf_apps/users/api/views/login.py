import logging

from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework_jwt.views import ObtainJSONWebToken

from sme_ptrf_apps.users.api.services import AutenticacaoService
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.users.services.get_unidades_usuario_service import get_unidades_do_usuario

User = get_user_model()
logger = logging.getLogger(__name__)


class LoginView(ObtainJSONWebToken):
    """
    POST auth/login/
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
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
                        return Response({'detail': 'Você está sem autorização de acesso à aplicação no momento. Entre em contato com o administrador do Sig.Escola.'},
                                        status=status.HTTP_401_UNAUTHORIZED)

                    request._full_data = {'username': user_dict['login'], 'password': senha}
                    resp = super().post(request, *args, **kwargs)
                    unidades = get_unidades_do_usuario(user)

                    if not unidades:
                        associacao = Associacao.objects.first()
                    else:
                        associacao = Associacao.objects.filter(unidade__uuid=unidades[0]['uuid']).first()

                    #TODO Rever esse bloco
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
                    user_dict['permissoes'] = self.get_user_permissions(user)
                    data = {**user_dict, **resp.data}
                    return Response(data)
            return Response(response.json(), response.status_code)
        except Exception as e:
            return Response({'data': {'detail': f'ERROR - {e}'}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_user_permissions(self, user):
        perms = []
        for group in user.groups.all():
            for permission in group.permissions.all():
                perms.append(permission.codename)

        return perms

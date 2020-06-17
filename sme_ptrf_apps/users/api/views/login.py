import logging
import json

from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework_jwt.views import ObtainJSONWebToken

from sme_ptrf_apps.users.api.services import AutenticacaoService
from sme_ptrf_apps.core.models import Associacao

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
                        return Response({'data': {'detail': 'Usuário não encontrado.'}}, status=status.HTTP_401_UNAUTHORIZED)

                    request._full_data = {'username': user_dict['login'], 'password': senha}
                    resp = super().post(request, *args, **kwargs)
                    associacao = user.associacao #Associacao.objects.filter(usuario=user).first()
                    if not associacao:
                        associacao = Associacao.objects.first()
                    associacao_dict = {'uuid': associacao.uuid, 'nome': associacao.nome} if associacao else {'uuid': '', 'nome': ''}
                    user_dict['associacao'] = associacao_dict
                    data = {**user_dict, **resp.data}
                    return Response(data)
            return Response(response.json(), response.status_code)
        except Exception as e:
            return Response({'data': {'detail': f'ERROR - {e}'}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

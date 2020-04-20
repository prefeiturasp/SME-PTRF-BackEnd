import json

from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework_jwt.views import ObtainJSONWebToken

from sme_ptrf_apps.users.api.services import AutenticacaoService
from sme_ptrf_apps.core.models import Associacao

User = get_user_model()


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
                    user, _ = User.objects.update_or_create(
                        username=user_dict['login'],
                        defaults={'name': user_dict['nome'],
                                  'email': user_dict['email']})
                    user.set_password(senha)
                    user.save()
                    request._full_data = {'username': user_dict['login'], 'password': senha}
                    resp = super().post(request, *args, **kwargs)
                    associacao = user.associacao
                    if not associacao:
                        associacao = Associacao.objects.first()
                    associacao_dict = {'uuid': associacao.uuid, 'nome': associacao.nome} if associacao else {'uuid': '', 'nome': ''}
                    user_dict['associacao'] = associacao_dict
                    data = {**user_dict, **resp.data}
                    return Response(data)
            return Response(response.json(), response.status_code)
        except Exception as e:
            return Response({'data': {'detail': f'ERROR - {e}'}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

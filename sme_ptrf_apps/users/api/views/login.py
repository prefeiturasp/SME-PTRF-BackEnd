import logging
import json
import uuid

from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework_jwt.views import ObtainJSONWebToken

from sme_ptrf_apps.users.api.services import AutenticacaoService
from sme_ptrf_apps.core.models import Associacao

User = get_user_model()
logger = logging.getLogger(__name__)

# Constante que representa o UUID da unidade Secretaria Municipal de Educação
UUID_SME = uuid.uuid4()
UNIDADE_SME = {
    'uuid': UUID_SME,
    'nome': 'Secretaria Municipal de Educação',
    'tipo_unidade': 'SME',
    'associacao': {
        'uuid': '',
        'nome': ''
    }
}


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

                    request._full_data = {'username': user_dict['login'], 'password': senha}
                    resp = super().post(request, *args, **kwargs)
                    unidades = []
                    for unidade in user.unidades.all():
                        associacao = Associacao.objects.filter(unidade__uuid=unidade.uuid).first()
                        unidades.append({
                            'uuid': unidade.uuid,
                            'nome': unidade.nome,
                            'tipo_unidade': unidade.tipo_unidade,
                            'associacao': {
                                'uuid': associacao.uuid if associacao else '',
                                'nome': associacao.nome if associacao else ''
                            }
                        })

                    '''
                    Como a visão SME não tem uma Unidade real, crio a unidade caso o usuário tenha essa visão
                    '''
                    if user.visoes.filter(nome='SME').exists():
                        unidades.append(UNIDADE_SME)

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

import pytest
from model_bakery import baker
from django.contrib.auth.models import Permission
from sme_ptrf_apps.users.models import Grupo
from django.contrib.contenttypes.models import ContentType


@pytest.fixture
def grupo_verificacao_regularidade_documentos():
    return baker.make('GrupoVerificacaoRegularidade', titulo='Documentos')


@pytest.fixture
def lista_verificacao_regularidade_documentos_associacao(grupo_verificacao_regularidade_documentos):
    return baker.make(
        'ListaVerificacaoRegularidade',
        titulo='Documentos da Associação',
        grupo=grupo_verificacao_regularidade_documentos
    )


@pytest.fixture
def item_verificacao_regularidade_documentos_associacao_cnpj(lista_verificacao_regularidade_documentos_associacao):
    return baker.make(
        'ItemVerificacaoRegularidade',
        descricao='CNPJ',
        lista=lista_verificacao_regularidade_documentos_associacao
    )


@pytest.fixture
def verificacao_regularidade_associacao_documento_cnpj(grupo_verificacao_regularidade_documentos, lista_verificacao_regularidade_documentos_associacao,item_verificacao_regularidade_documentos_associacao_cnpj, associacao):
    return baker.make(
        'VerificacaoRegularidadeAssociacao',
        associacao=associacao,
        grupo_verificacao=grupo_verificacao_regularidade_documentos,
        lista_verificacao=lista_verificacao_regularidade_documentos_associacao,
        item_verificacao=item_verificacao_regularidade_documentos_associacao_cnpj,
        regular=True
    )


@pytest.fixture
def tecnico_dre(dre):
    return baker.make(
        'TecnicoDre',
        dre=dre,
        nome='José Testando',
        rf='271170',
        email='tecnico.sobrenome@sme.prefeitura.sp.gov.br',
        telefone='1259275127'
    )


@pytest.fixture
def faq_categoria():
    return baker.make(
        'FaqCategoria',
        nome='Geral'
    )


@pytest.fixture
def faq_categoria_02():
    return baker.make(
        'FaqCategoria',
        nome='Associações'
    )


@pytest.fixture
def faq(faq_categoria):
    return baker.make(
        'Faq',
        pergunta='Pergunta 01 - Cat Geral 01',
        resposta='Esta é a resposta da Pergunta 01',
        categoria=faq_categoria
    )


@pytest.fixture
def faq_02(faq_categoria_02):
    return baker.make(
        'Faq',
        pergunta='Pergunta 02 - Cat Associações 01',
        resposta='Esta é a resposta da Pergunta 02',
        categoria=faq_categoria_02
    )


@pytest.fixture
def atribuicao(tecnico_dre, unidade, periodo):
    return baker.make(
        'Atribuicao',
        tecnico=tecnico_dre,
        unidade=unidade,
        periodo=periodo,
    )


@pytest.fixture
def permissoes_dadosdiretoria_dre():
    permissoes = [
        Permission.objects.create(
            name="visualizar dados diretoria dre", 
            codename='view_dadosdiretoria_dre', 
            content_type=ContentType.objects.filter(app_label="auth").first()
        ),
    ]

    return permissoes

@pytest.fixture
def grupo_dados_diretoria_dre(permissoes_dadosdiretoria_dre):
    g = Grupo.objects.create(name="dados_diretoria_dre")
    g.permissions.add(*permissoes_dadosdiretoria_dre)
    return g


@pytest.fixture
def usuario_permissao_atribuicao(
        unidade,
        grupo_dados_diretoria_dre):

    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_dados_diretoria_dre)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_dre(client, usuario_permissao_atribuicao):
    from unittest.mock import patch

    from rest_framework.test import APIClient
    api_client = APIClient()
    with patch('sme_ptrf_apps.users.api.views.login.AutenticacaoService.autentica') as mock_post:
        data = {
            "nome": "LUCIA HELENA",
            "cpf": "62085077072",
            "email": "luh@gmail.com",
            "login": "7210418"
        }
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = data
        resp = api_client.post('/api/login', {'login': usuario_permissao_atribuicao.username,
                                              'senha': usuario_permissao_atribuicao.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client

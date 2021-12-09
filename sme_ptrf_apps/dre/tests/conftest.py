import pytest
from freezegun import freeze_time
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker
from django.contrib.auth.models import Permission
from sme_ptrf_apps.users.models import Grupo
from django.contrib.contenttypes.models import ContentType

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
def arquivo():
    return SimpleUploadedFile(f'arquivo.txt', bytes(f'CONTEUDO TESTE TESTE TESTE', encoding="utf-8"))


@pytest.fixture
@freeze_time('2020-10-27 13:59:00')
def relatorio_dre_consolidado_gerado_total(periodo, dre, tipo_conta_cartao, arquivo):
    return baker.make(
        'RelatorioConsolidadoDre',
        dre=dre,
        tipo_conta=tipo_conta_cartao,
        periodo=periodo,
        arquivo=arquivo,
        status='GERADO_TOTAL'
    )


@pytest.fixture
def permissoes_dadosdiretoria_dre():
    permissoes = [
        Permission.objects.filter(codename='dre_leitura').first(),
        Permission.objects.filter(codename='dre_gravacao').first()
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


@pytest.fixture
def permissoes_ver_relatorio_consolidado_dre():
    permissoes = [
        Permission.objects.filter(codename='dre_leitura').first(),
        Permission.objects.filter(codename='dre_gravacao').first()
    ]

    return permissoes


@pytest.fixture
def grupo_ver_relatorio_consolidado_dre(permissoes_ver_relatorio_consolidado_dre):
    g = Grupo.objects.create(name="grupo_view_relatorio_consolidado_dre")
    g.permissions.add(*permissoes_ver_relatorio_consolidado_dre)
    return g


@pytest.fixture
def usuario_permissao_ver_relatorio_consolidado(
        unidade,
        grupo_ver_relatorio_consolidado_dre):

    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_ver_relatorio_consolidado_dre)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_relatorio_consolidado(client, usuario_permissao_ver_relatorio_consolidado):
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
        resp = api_client.post('/api/login', {'login': usuario_permissao_ver_relatorio_consolidado.username,
                                              'senha': usuario_permissao_ver_relatorio_consolidado.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client


@pytest.fixture
def justificativa_relatorio_dre_consolidado(periodo, dre, tipo_conta_cartao):
    return baker.make(
        'JustificativaRelatorioConsolidadoDre',
        dre=dre,
        tipo_conta=tipo_conta_cartao,
        texto='Teste'
    )

@pytest.fixture
def tipo_devolucao_ao_tesouro():
    return baker.make('TipoDevolucaoAoTesouro', nome='Teste')


@pytest.fixture
def obs_devolucao_tesouro_relatorio_dre_consolidado(periodo, dre, tipo_conta_cartao, tipo_devolucao_ao_tesouro):
    return baker.make(
        'ObsDevolucaoRelatorioConsolidadoDre',
        dre=dre,
        tipo_conta=tipo_conta_cartao,
        tipo_devolucao='TESOURO',
        tipo_devolucao_ao_tesouro=tipo_devolucao_ao_tesouro,
        observacao='Teste devolução ao tesouro'
    )


@pytest.fixture
def obs_devolucao_conta_relatorio_dre_consolidado(periodo, dre, tipo_conta_cartao, detalhe_tipo_receita):
    return baker.make(
        'ObsDevolucaoRelatorioConsolidadoDre',
        dre=dre,
        tipo_conta=tipo_conta_cartao,
        tipo_devolucao='CONTA',
        tipo_devolucao_a_conta=detalhe_tipo_receita,
        observacao='Teste devolução à conta'
    )


@pytest.fixture
def motivo_aprovacao_ressalva_x():
    return baker.make(
        'MotivoAprovacaoRessalva',
        motivo='X'
    )


@pytest.fixture
def motivo_aprovacao_ressalva_y():
    return baker.make(
        'MotivoAprovacaoRessalva',
        motivo='Y'
    )


@pytest.fixture
def comissao_exame_contas():
    return baker.make('Comissao', nome='Exame de Contas')


@pytest.fixture
def membro_comissao_exame_contas(comissao_exame_contas, dre_ipiranga):
    membro = baker.make(
        'MembroComissao',
        rf='123456',
        nome='Jose Testando',
        email='jose@teste.com',
        dre=dre_ipiranga,
        comissoes=[comissao_exame_contas, ]
    )
    return membro


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
def ano_analise_regularidade_2020():
    return baker.make('AnoAnaliseRegularidade', ano=2020)


@pytest.fixture
def ano_analise_regularidade_2021():
    return baker.make('AnoAnaliseRegularidade', ano=2021)


@pytest.fixture
def analise_regularidade_associacao(
    associacao,
    item_verificacao_regularidade_documentos_associacao_cnpj,
    ano_analise_regularidade_2021
):
    return baker.make(
        'AnaliseRegularidadeAssociacao',
        associacao=associacao,
        ano_analise=ano_analise_regularidade_2021,
        status_regularidade='REGULAR'
    )


@pytest.fixture
def verificacao_regularidade_associacao_documento_cnpj(
    item_verificacao_regularidade_documentos_associacao_cnpj,
    analise_regularidade_associacao
):
    return baker.make(
        'VerificacaoRegularidadeAssociacao',
        analise_regularidade=analise_regularidade_associacao,
        item_verificacao=item_verificacao_regularidade_documentos_associacao_cnpj,
        regular=True
    )


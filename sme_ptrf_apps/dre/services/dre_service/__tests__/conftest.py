import pytest
from model_bakery import baker
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def dre_valida():
    return baker.make('Unidade', codigo_eol='99999', tipo_unidade='DRE', nome='DRE teste', sigla='TT')


@pytest.fixture
def escola(dre_valida):
    return baker.make(
        'Unidade',
        nome='Escola Teste',
        tipo_unidade='CEU',
        codigo_eol='123456',
        dre=dre_valida,
        sigla='ET',
    )


@pytest.fixture
def outra_dre():
    return baker.make('Unidade', codigo_eol='888888', tipo_unidade='DRE', nome='Outra DRE', sigla='OD')


@pytest.fixture
def comissao_contas():
    return baker.make('Comissao', nome='Exame de Contas')


@pytest.fixture
def outra_comissao():
    return baker.make('Comissao', nome='Outra comissão')


@pytest.fixture
def parametros_dre_comissoes(comissao_contas):
    return baker.make(
        'ParametrosDre',
        comissao_exame_contas=comissao_contas
    )


@pytest.fixture
def jose_membro_comissao_exame_contas_da_dre(comissao_contas, dre_valida):
    membro = baker.make(
        'MembroComissao',
        rf='123456',
        nome='Jose Testando',
        email='jose@teste.com',
        cargo='teste',
        dre=dre_valida,
        comissoes=[comissao_contas, ]
    )
    return membro


@pytest.fixture
def ana_membro_comissao_exame_contas_da_dre(comissao_contas, dre_valida):
    membro = baker.make(
        'MembroComissao',
        rf='123457',
        nome='Ana teste',
        email='ana@teste.com',
        cargo='teste',
        dre=dre_valida,
        comissoes=[comissao_contas, ]
    )
    return membro


@pytest.fixture
def pedro_membro_outra_comissao_da_dre(outra_comissao, dre_valida):
    membro = baker.make(
        'MembroComissao',
        rf='123458',
        nome='Pedro So Teste',
        email='pedro@teste.com',
        cargo='teste',
        dre=dre_valida,
        comissoes=[outra_comissao, ]
    )
    return membro


@pytest.fixture
def maria_membro_comissao_exame_contas_de_outra_dre(comissao_contas, outra_dre):
    membro = baker.make(
        'MembroComissao',
        rf='123459',
        nome='Maria Testado',
        email='maria@teste.com',
        cargo='teste',
        dre=outra_dre,
        comissoes=[comissao_contas, ]
    )
    return membro


@pytest.fixture
def usuario_servidor_jose():
    user = User.objects.create_user(
        username='123456',
        password='Sgp8198',
        email='jose@amcom.com.br',
        name="Jose",
        e_servidor=True
    )
    user.save()
    return user


@pytest.fixture
def usuario_servidor_ana():
    user = User.objects.create_user(
        username='123457',
        password='Sgp8198',
        email='ana@amcom.com.br',
        name="Ana",
        e_servidor=True
    )
    user.save()
    return user


@pytest.fixture
def usuario_servidor_pedro():
    user = User.objects.create_user(
        username='123458',
        password='Sgp8198',
        email='pedro@amcom.com.br',
        name="Pedro",
        e_servidor=True
    )
    user.save()
    return user


@pytest.fixture
def usuario_servidor_maria():
    user = User.objects.create_user(
        username='123459',
        password='Sgp8198',
        email='maria@amcom.com.br',
        name="Maria",
        e_servidor=True
    )
    user.save()
    return user


@pytest.fixture
def consolidado_dre_parcial_1_devolvido(
    periodo,
    dre_valida
):
    from sme_ptrf_apps.dre.models import ConsolidadoDRE
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_valida,
        periodo=periodo,
        status=ConsolidadoDRE.STATUS_GERADOS_PARCIAIS,
        eh_parcial=True,
        sequencia_de_publicacao=1
    )

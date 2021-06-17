import pytest

from datetime import date

from django.contrib.auth.models import Permission

from model_bakery import baker

from sme_ptrf_apps.users.models import Grupo


@pytest.fixture
def unidade_a(dre):
    return baker.make(
        'Unidade',
        nome='Escola A',
        tipo_unidade='EMEI',
        codigo_eol='270001',
        dre=dre,
        sigla='EA'
    )


@pytest.fixture
def associacao_a(unidade_a):
    return baker.make(
        'Associacao',
        nome='Associacao 271170',
        cnpj='62.738.735/0001-74',
        unidade=unidade_a,
    )


@pytest.fixture
def visao_ue():
    return baker.make('Visao', nome='UE')


@pytest.fixture
def permissao_recebe_notificacao_proximidade_inicio_pc():
    return Permission.objects.filter(codename='recebe_notificacao_proximidade_inicio_prestacao_de_contas').first()


@pytest.fixture
def permissao_recebe_notificacao_inicio_pc():
    return Permission.objects.filter(codename='recebe_notificacao_inicio_periodo_prestacao_de_contas').first()


@pytest.fixture
def permissao_recebe_notificacao_pendencia_envio_pc():
    return Permission.objects.filter(codename='recebe_notificacao_pendencia_envio_prestacao_de_contas').first()


@pytest.fixture
def permissao_recebe_notificacao_pc_devolvida_para_acertos():
    return Permission.objects.filter(codename='recebe_notificacao_prestacao_de_contas_devolvida_para_acertos').first()


@pytest.fixture
def grupo_notificavel(permissao_recebe_notificacao_proximidade_inicio_pc, permissao_recebe_notificacao_inicio_pc, permissao_recebe_notificacao_pendencia_envio_pc, permissao_recebe_notificacao_pc_devolvida_para_acertos, visao_ue):
    g = Grupo.objects.create(name="grupo_notificavel")
    g.permissions.add(permissao_recebe_notificacao_proximidade_inicio_pc)
    g.permissions.add(permissao_recebe_notificacao_inicio_pc)
    g.permissions.add(permissao_recebe_notificacao_pendencia_envio_pc)
    g.permissions.add(permissao_recebe_notificacao_pc_devolvida_para_acertos)
    g.visoes.add(visao_ue)
    g.descricao = "Grupo que recebe notificações"
    g.save()
    return g


@pytest.fixture
def grupo_nao_notificavel(visao_ue):
    g = Grupo.objects.create(name="grupo_nao_notificavel")
    g.visoes.add(visao_ue)
    g.descricao = "Grupo que não recebe notificações"
    g.save()
    return g


@pytest.fixture
def usuario_notificavel(
        unidade_a,
        grupo_notificavel,
        visao_ue):

    from django.contrib.auth import get_user_model

    senha = 'Sgp0418'
    login = '2711001'
    email = 'notificavel@amcom.com.br'

    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade_a)
    user.groups.add(grupo_notificavel)
    user.visoes.add(visao_ue)
    user.save()
    return user


@pytest.fixture
def usuario_nao_notificavel(
    unidade_a,
    grupo_nao_notificavel,
    visao_ue):
    from django.contrib.auth import get_user_model

    senha = 'Sgp0418'
    login = '2711002'
    email = 'naonotificavel@amcom.com.br'

    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade_a)
    user.groups.add(grupo_nao_notificavel)
    user.visoes.add(visao_ue)
    user.save()
    return user


@pytest.fixture
def periodo_2020_4_pc_2021_01_01_a_2021_01_15():
    return baker.make(
        'Periodo',
        referencia='2020.4',
        data_inicio_realizacao_despesas=date(2020, 10, 1),
        data_fim_realizacao_despesas=date(2020, 12, 31),
        data_prevista_repasse=date(2020, 10, 1),
        data_inicio_prestacao_contas=date(2021, 1, 1),
        data_fim_prestacao_contas=date(2021, 1, 15),
        periodo_anterior=None,
    )


@pytest.fixture
def periodo_2021_1_pc_2021_04_1_a_2021_04_15(periodo_2020_4_pc_2021_01_01_a_2021_01_15):
    return baker.make(
        'Periodo',
        referencia='2021.1',
        data_inicio_realizacao_despesas=date(2021, 1, 1),
        data_fim_realizacao_despesas=date(2021, 3, 31),
        data_prevista_repasse=date(2021, 1, 1),
        data_inicio_prestacao_contas=date(2021, 4, 1),
        data_fim_prestacao_contas=date(2021, 4, 15),
        periodo_anterior=periodo_2020_4_pc_2021_01_01_a_2021_01_15,
    )


@pytest.fixture
def periodo_2021_2_pc_2021_07_01_a_2021_07_15(periodo_2021_1_pc_2021_04_1_a_2021_04_15):
    return baker.make(
        'Periodo',
        referencia='2021.2',
        data_inicio_realizacao_despesas=date(2021, 4, 1),
        data_fim_realizacao_despesas=date(2021, 6, 30),
        data_prevista_repasse=date(2021, 4, 1),
        data_inicio_prestacao_contas=date(2021, 7, 1),
        data_fim_prestacao_contas=date(2021, 7, 15),
        periodo_anterior=periodo_2021_1_pc_2021_04_1_a_2021_04_15,
    )

@pytest.fixture
def periodo_2021_3_pc_2021_06_12_a_2021_06_17(periodo_2021_1_pc_2021_04_1_a_2021_04_15):
    return baker.make(
        'Periodo',
        referencia='2021.3',
        data_inicio_realizacao_despesas=date(2021, 4, 1),
        data_fim_realizacao_despesas=date(2021, 6, 30),
        data_prevista_repasse=date(2021, 4, 1),
        data_inicio_prestacao_contas=date(2021, 6, 12),
        data_fim_prestacao_contas=date(2021, 6, 17),
        periodo_anterior=periodo_2021_1_pc_2021_04_1_a_2021_04_15,
    )

@pytest.fixture
def periodo_2021_4_pc_2021_06_18_a_2021_06_30():
    return baker.make(
        'Periodo',
        referencia='2021.4',
        data_inicio_realizacao_despesas=date(2021, 4, 1),
        data_fim_realizacao_despesas=date(2021, 6, 30),
        data_prevista_repasse=date(2021, 4, 1),
        data_inicio_prestacao_contas=date(2021, 6, 18),
        data_fim_prestacao_contas=date(2021, 6, 30),
        periodo_anterior=None,
        notificacao_inicio_periodo_pc_realizada=False
    )

@pytest.fixture
def periodo_notifica_pendencia_envio_pc():
    return baker.make(
        'Periodo',
        referencia='2021.5',
        data_inicio_realizacao_despesas=date(2021, 4, 1),
        data_fim_realizacao_despesas=date(2021, 6, 15),
        data_prevista_repasse=date(2021, 4, 1),
        data_inicio_prestacao_contas=date(2021, 6, 18),
        data_fim_prestacao_contas=date(2021, 6, 16),
        periodo_anterior=None,
        notificacao_inicio_periodo_pc_realizada=False
    )


@pytest.fixture
def prestacao_nao_notifica_pendencia_envio_pc(periodo_notifica_pendencia_envio_pc, associacao_a):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_notifica_pendencia_envio_pc,
        associacao=associacao_a,
        status="EM_ANALISE"
    )

@pytest.fixture
def prestacao_notifica_pc_devolvida_para_acertos(periodo_notifica_pendencia_envio_pc, associacao_a):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_notifica_pendencia_envio_pc,
        associacao=associacao_a,
        status="DEVOLVIDA"
    )

@pytest.fixture
def parametro_proximidade_inicio_pc_5_dias():
    return baker.make(
        'Parametros',
        dias_antes_inicio_periodo_pc_para_notificacao=5,
    )


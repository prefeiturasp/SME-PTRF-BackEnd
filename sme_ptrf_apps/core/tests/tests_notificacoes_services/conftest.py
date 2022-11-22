import pytest

from datetime import date, datetime, timedelta

from django.contrib.auth.models import Permission
from ....dre.models import TecnicoDre, ConsolidadoDRE

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
def visao_dre():
    return baker.make('Visao', nome='DRE')


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
def permissao_recebe_notificacao_proximidade_fim_pc():
    return Permission.objects.filter(codename='recebe_notificacao_proximidade_fim_periodo_prestacao_de_contas').first()


@pytest.fixture
def permissao_recebe_notificacao_atraso_entrega_ajustes_pc():
    return Permission.objects.filter(codename='recebe_notificacao_atraso_entrega_ajustes_prestacao_de_contas').first()


@pytest.fixture
def permissao_recebe_notificacao_proximidade_fim_entrega_ajustes_pc():
    return Permission.objects.filter(codename='recebe_notificacao_proximidade_fim_prazo_ajustes_prestacao_de_contas').first()


@pytest.fixture
def permissao_recebe_notificacao_pc_aprovada():
    return Permission.objects.filter(codename='recebe_notificacao_aprovacao_pc').first()


@pytest.fixture
def permissao_recebe_notificacao_pc_aprovada_com_ressalvas():
    return Permission.objects.filter(codename='recebe_notificacao_aprovacao_pc').first()


@pytest.fixture
def permissao_recebe_notificacao_pc_reprovada():
    return Permission.objects.filter(codename='recebe_notificacao_reprovacao_pc_incluindo_motivos').first()


@pytest.fixture
def grupo_notificavel(
    permissao_recebe_notificacao_proximidade_inicio_pc,
    permissao_recebe_notificacao_inicio_pc,
    permissao_recebe_notificacao_pendencia_envio_pc,
    permissao_recebe_notificacao_pc_devolvida_para_acertos,
    permissao_recebe_notificacao_proximidade_fim_pc,
    permissao_recebe_notificacao_atraso_entrega_ajustes_pc,
    permissao_recebe_notificacao_proximidade_fim_entrega_ajustes_pc,
    permissao_recebe_notificacao_pc_aprovada,
    permissao_recebe_notificacao_pc_aprovada_com_ressalvas,
    permissao_recebe_notificacao_pc_reprovada,
    visao_ue
):
    g = Grupo.objects.create(name="grupo_notificavel")
    g.permissions.add(permissao_recebe_notificacao_proximidade_inicio_pc)
    g.permissions.add(permissao_recebe_notificacao_inicio_pc)
    g.permissions.add(permissao_recebe_notificacao_pendencia_envio_pc)
    g.permissions.add(permissao_recebe_notificacao_pc_devolvida_para_acertos)
    g.permissions.add(permissao_recebe_notificacao_proximidade_fim_pc)
    g.permissions.add(permissao_recebe_notificacao_atraso_entrega_ajustes_pc)
    g.permissions.add(permissao_recebe_notificacao_proximidade_fim_entrega_ajustes_pc)
    g.permissions.add(permissao_recebe_notificacao_pc_aprovada)
    g.permissions.add(permissao_recebe_notificacao_pc_aprovada_com_ressalvas)
    g.permissions.add(permissao_recebe_notificacao_pc_reprovada)
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
def usuario_tecnico_notificavel():
    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '5047951'
    email = 'notificavel@amcom.com.br'

    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.save()
    return user

@pytest.fixture
def tecnico_notificavel(unidade_a, visao_dre, dre, usuario_tecnico_notificavel):
    email = 'notificavel@amcom.com.br'
    tecnico = TecnicoDre.objects.create(
        nome='MARIA DO CARMO MACHADO LEAL DE GODOY',
        dre=dre,
        rf='5047951',
        email=email,
        telefone='1938342667'
    )
    tecnico.save()
    return tecnico


@pytest.fixture
def periodo_anterior_teste_service_consolidado_dre():
    return baker.make(
        'Periodo',
        referencia='2021.2',
        data_inicio_realizacao_despesas=date(2021, 6, 16),
        data_fim_realizacao_despesas=date(2021, 12, 31),
    )


@pytest.fixture
def periodo_teste_service_consolidado_dre(periodo_anterior_teste_service_consolidado_dre):
    return baker.make(
        'Periodo',
        referencia='2022.1',
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 12, 31),
        periodo_anterior=periodo_anterior_teste_service_consolidado_dre,
    )


@pytest.fixture
def analise_consolidado_dre_01_prazo_acerto_vencido():
    return baker.make(
        'AnaliseConsolidadoDre',
        data_devolucao=datetime.today() - timedelta(days = 1 ),
        data_limite=datetime.today() - timedelta(days = 1 ),
        data_retorno_analise=datetime.today() - timedelta(days = 1 ),
    )


@pytest.fixture
def analise_consolidado_dre_01_dentro_prazo():
    return baker.make(
        'AnaliseConsolidadoDre',
        data_devolucao=datetime.today(),
        data_limite=datetime.today(),
        data_retorno_analise=datetime.today(),
    )


@pytest.fixture
def consolidado_dre_devolucao_apos_acertos(periodo_teste_service_consolidado_dre, dre, analise_consolidado_dre_01_prazo_acerto_vencido, tecnico_notificavel):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre,
        periodo=periodo_teste_service_consolidado_dre,
        status_sme=ConsolidadoDRE.STATUS_SME_DEVOLVIDO,
        analise_atual=analise_consolidado_dre_01_prazo_acerto_vencido,
        eh_parcial=False,
        sequencia_de_publicacao=0
    )


@pytest.fixture
def consolidado_dre_devolucao_apos_acertos_dentro_do_prazo(periodo_teste_service_consolidado_dre, dre, analise_consolidado_dre_01_dentro_prazo, tecnico_notificavel):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre,
        periodo=periodo_teste_service_consolidado_dre,
        status_sme=ConsolidadoDRE.STATUS_SME_DEVOLVIDO,
        analise_atual=analise_consolidado_dre_01_dentro_prazo,
        eh_parcial=False,
        sequencia_de_publicacao=0
    )


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
def periodo_notifica_proximidade_fim_pc():
    return baker.make(
        'Periodo',
        referencia='2021.6',
        data_inicio_realizacao_despesas=date(2021, 4, 1),
        data_fim_realizacao_despesas=date(2021, 6, 15),
        data_prevista_repasse=date(2021, 4, 1),
        data_inicio_prestacao_contas=date(2021, 6, 12),
        data_fim_prestacao_contas=date(2021, 6, 18),
        periodo_anterior=None,
        notificacao_proximidade_fim_pc_realizada=False
    )


@pytest.fixture
def periodo_notifica_pc_aprovada():
    return baker.make(
        'Periodo',
        referencia='2021.2',
        data_inicio_realizacao_despesas=date(2021, 6, 16),
        data_fim_realizacao_despesas=date(2021, 12, 31),
        data_prevista_repasse=date(2022, 1, 1),
        data_inicio_prestacao_contas=date(2021, 12, 25),
        data_fim_prestacao_contas=date(2021, 12, 31),
        periodo_anterior=None,
        notificacao_inicio_periodo_pc_realizada=False
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
def prestacao_notifica_pc_aprovada(periodo_notifica_pc_aprovada, associacao_a):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_notifica_pc_aprovada,
        associacao=associacao_a,
        status="APROVADA"
    )

@pytest.fixture
def prestacao_notifica_pc_aprovada_com_ressalvas(periodo_notifica_pc_aprovada, associacao_a):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_notifica_pc_aprovada,
        associacao=associacao_a,
        status="APROVADA_RESSALVA"
    )


@pytest.fixture
def prestacao_notifica_pc_reprovada(periodo_notifica_pc_aprovada, associacao_a):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_notifica_pc_aprovada,
        associacao=associacao_a,
        status="REPROVADA"
    )


@pytest.fixture
def motivo_aprovacao_ressalva_x():
    return baker.make(
        'dre.MotivoAprovacaoRessalva',
        motivo='X'
    )

@pytest.fixture
def motivo_reprovacao_x():
    return baker.make(
        'dre.MotivoReprovacao',
        motivo='X'
    )


@pytest.fixture
def devolucao_notifica_atraso_entrega_ajustes_pc(prestacao_notifica_pc_devolvida_para_acertos):
    return baker.make(
        'DevolucaoPrestacaoConta',
        prestacao_conta=prestacao_notifica_pc_devolvida_para_acertos,
        data=date(2021, 6, 1),
        data_limite_ue=date(2021, 6, 18),
    )


@pytest.fixture
def devolucao_nao_notifica_atraso_entrega_ajustes_pc(prestacao_nao_notifica_pendencia_envio_pc):
    return baker.make(
        'DevolucaoPrestacaoConta',
        prestacao_conta=prestacao_nao_notifica_pendencia_envio_pc,
        data=date(2021, 6, 1),
        data_limite_ue=date(2021, 6, 18),
    )


@pytest.fixture
def devolucao_notifica_proximidade_fim_entrega_ajustes_pc(prestacao_notifica_pc_devolvida_para_acertos):
    return baker.make(
        'DevolucaoPrestacaoConta',
        prestacao_conta=prestacao_notifica_pc_devolvida_para_acertos,
        data=date(2021, 6, 1),
        data_limite_ue=date(2021, 6, 26),
    )


@pytest.fixture
def devolucao_nao_notifica_proximidade_fim_entrega_ajustes_pc_em_analise(prestacao_nao_notifica_pendencia_envio_pc):
    return baker.make(
        'DevolucaoPrestacaoConta',
        prestacao_conta=prestacao_nao_notifica_pendencia_envio_pc,
        data=date(2021, 6, 1),
        data_limite_ue=date(2021, 6, 26),
    )

@pytest.fixture
def parametro_proximidade_inicio_pc_5_dias():
    return baker.make(
        'Parametros',
        dias_antes_inicio_periodo_pc_para_notificacao=5,
    )


@pytest.fixture
def parametro_proximidade_fim_pc_5_dias():
    return baker.make(
        'Parametros',
        dias_antes_fim_periodo_pc_para_notificacao=5,
    )

@pytest.fixture
def parametro_proximidade_fim_entrega_ajustes_5_dias():
    return baker.make(
        'Parametros',
        dias_antes_fim_prazo_ajustes_pc_para_notificacao=5,
    )

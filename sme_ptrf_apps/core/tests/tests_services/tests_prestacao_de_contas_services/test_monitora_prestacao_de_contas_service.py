import time
from datetime import date

import pytest
from model_bakery import baker

from sme_ptrf_apps.core.models import PrestacaoConta

pytestmark = pytest.mark.django_db

from sme_ptrf_apps.core.services.prestacao_contas_services import concluir_prestacao_de_contas


@pytest.mark.django_db(True)
@pytest.fixture
def create_user(django_user_model):
    def make_user(**kwargs):
        return django_user_model.objects.create_user(**kwargs)

    return make_user


@pytest.fixture
def usuario_notificavel():
    from django.contrib.auth import get_user_model

    senha = 'Sgp0418'
    login = '2711001'
    email = 'notificavel@amcom.com.br'

    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.save()
    return user


@pytest.mark.django_db(True)
@pytest.fixture
def periodo_anterior():
    return baker.make(
        'Periodo',
        referencia='2019.1',
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 8, 31),
    )


@pytest.mark.django_db(True)
@pytest.fixture
def periodo(periodo_anterior):
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 9, 1),
        data_fim_realizacao_despesas=date(2019, 11, 30),
        data_prevista_repasse=date(2019, 10, 1),
        data_inicio_prestacao_contas=date(2019, 12, 1),
        data_fim_prestacao_contas=date(2019, 12, 5),
        periodo_anterior=periodo_anterior,
    )


@pytest.fixture
def devolucao_prestacao_conta_2020_1_monitora_pc(prestacao_conta_com_analise_nao_apresentada):
    return baker.make(
        'DevolucaoPrestacaoConta',
        prestacao_conta=prestacao_conta_com_analise_nao_apresentada,
        data=date(2020, 7, 1),
        data_limite_ue=date(2020, 8, 1),
        data_retorno_ue=None
    )


@pytest.mark.django_db(True)
@pytest.fixture
def analise_prestacao_conta_2020_1_monitora_pc(prestacao_conta_com_analise_nao_apresentada,
                                               devolucao_prestacao_conta_2020_1_monitora_pc):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_com_analise_nao_apresentada,
        devolucao_prestacao_conta=devolucao_prestacao_conta_2020_1_monitora_pc
    )


@pytest.mark.django_db(True)
@pytest.fixture
def prestacao_conta_com_analise_nao_apresentada(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        data_ultima_analise=date(2020, 10, 1),
        status='NAO_APRESENTADA',
    )


@pytest.mark.django_db(True)
@pytest.fixture
def prestacao_conta_com_analise_nao_apresentada_02(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        status='NAO_APRESENTADA',
    )


@pytest.fixture
def parametros_monitora_pc():
    return baker.make(
        'Parametros',
        tempo_aguardar_conclusao_pc=1,
        permite_saldo_conta_negativo=True,
        fique_de_olho='',
        fique_de_olho_relatorio_dre='',
        texto_pagina_suporte_dre='Teste DRE',
        texto_pagina_suporte_sme='Teste SME',
        texto_pagina_valores_reprogramados_ue='Teste UE',
        texto_pagina_valores_reprogramados_dre='Teste DRE'
    )


@pytest.mark.django_db(True)
def test_monitora_pc_deve_passar_pc_para_devolvida(
    prestacao_conta_com_analise_nao_apresentada,
    analise_prestacao_conta_2020_1_monitora_pc,
    devolucao_prestacao_conta_2020_1_monitora_pc,
    periodo,
    associacao,
    usuario_notificavel,
    parametros_monitora_pc,
):
    uuid_pc = prestacao_conta_com_analise_nao_apresentada.uuid

    pc = PrestacaoConta.by_uuid(uuid_pc)

    assert pc.status == 'NAO_APRESENTADA'

    concluir_prestacao_de_contas(
        associacao=associacao,
        periodo=periodo,
        usuario=usuario_notificavel,
        monitoraPc=True,
    )
    time.sleep(10)

    pc = PrestacaoConta.by_uuid(uuid_pc)

    assert pc.status == 'DEVOLVIDA'


@pytest.mark.django_db(True)
def test_monitora_pc_deve_reabrir_pc(
    periodo,
    associacao,
    usuario_notificavel,
    parametros_monitora_pc,
):
    concluir_prestacao_de_contas(
        associacao=associacao,
        periodo=periodo,
        usuario=usuario_notificavel,
        monitoraPc=True,
    )

    assert PrestacaoConta.objects.filter(
        associacao=associacao,
        periodo=periodo,
    ).exists()

    time.sleep(10)

    assert not PrestacaoConta.objects.filter(
        associacao=associacao,
        periodo=periodo,
    ).exists()

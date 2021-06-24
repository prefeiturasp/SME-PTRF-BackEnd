from datetime import date

import pytest
from model_bakery import baker

from ....models import PrestacaoConta
from ....services import concluir_prestacao_de_contas


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures('celery_session_app')
@pytest.mark.usefixtures('celery_session_worker')
def test_prestacao_de_contas_deve_ser_criada(associacao, periodo, settings):
    prestacao = concluir_prestacao_de_contas(associacao=associacao, periodo=periodo)

    assert prestacao.status == PrestacaoConta.STATUS_EM_PROCESSAMENTO, "A PC deveria estar como Em_processamento."


@pytest.mark.django_db(transaction=False)
def test_fechamentos_devem_ser_criados_por_acao(associacao,
                                                periodo_2020_1,
                                                receita_2020_1_role_repasse_custeio_conferida,
                                                receita_2020_1_ptrf_repasse_capital_conferida,
                                                receita_2020_1_role_repasse_capital_nao_conferida,
                                                receita_2019_2_role_repasse_capital_conferida,
                                                receita_2020_1_role_repasse_capital_conferida,
                                                receita_2020_1_role_rendimento_custeio_conferida,
                                                despesa_2020_1,
                                                rateio_despesa_2020_role_custeio_conferido,
                                                rateio_despesa_2020_role_custeio_nao_conferido,
                                                rateio_despesa_2020_role_capital_conferido,
                                                despesa_2019_2,
                                                rateio_despesa_2019_role_conferido,
                                                acao_associacao_ptrf,
                                                settings):
    from sme_ptrf_apps.core.tasks import concluir_prestacao_de_contas_async
    from celery.result import EagerResult

    settings.CELERY_TASK_ALWAYS_EAGER = True
    task_result = concluir_prestacao_de_contas_async.delay(periodo_2020_1.uuid, associacao.uuid)
    assert isinstance(task_result, EagerResult)
    prestacao = PrestacaoConta.objects.filter(periodo=periodo_2020_1, associacao=associacao).first()
    assert prestacao
    assert prestacao.fechamentos_da_prestacao.count() == 2, "Deveriam ter sido criados dois fechamentos, um por ação."


@pytest.mark.django_db(transaction=False)
def test_deve_sumarizar_transacoes_incluindo_nao_conferidas(associacao,
                                                            periodo_2020_1,
                                                            receita_2020_1_role_repasse_custeio_conferida,
                                                            receita_2020_1_role_repasse_capital_nao_conferida,
                                                            receita_2019_2_role_repasse_capital_conferida,
                                                            receita_2020_1_role_repasse_capital_conferida,
                                                            receita_2020_1_role_rendimento_custeio_conferida,
                                                            despesa_2020_1,
                                                            rateio_despesa_2020_role_custeio_conferido,
                                                            rateio_despesa_2020_role_custeio_nao_conferido,
                                                            rateio_despesa_2020_role_capital_conferido,
                                                            despesa_2019_2,
                                                            rateio_despesa_2019_role_conferido,
                                                            settings):
    from sme_ptrf_apps.core.tasks import concluir_prestacao_de_contas_async
    from celery.result import EagerResult

    settings.CELERY_TASK_ALWAYS_EAGER = True
    task_result = concluir_prestacao_de_contas_async.delay(periodo_2020_1.uuid, associacao.uuid)
    assert isinstance(task_result, EagerResult)
    prestacao = PrestacaoConta.objects.filter(periodo=periodo_2020_1, associacao=associacao).first()
    assert prestacao

    assert prestacao.fechamentos_da_prestacao.count() == 1, "Deveriam ter sido criado apenas um fechamento."

    fechamento = prestacao.fechamentos_da_prestacao.first()

    total_receitas_capital_esperado = receita_2020_1_role_repasse_capital_conferida.valor + \
                                      receita_2020_1_role_repasse_capital_nao_conferida.valor
    assert fechamento.total_receitas_capital == total_receitas_capital_esperado
    assert fechamento.total_receitas_nao_conciliadas_capital == receita_2020_1_role_repasse_capital_nao_conferida.valor

    total_repasses_capital_esperado = receita_2020_1_role_repasse_capital_conferida.valor + \
                                      receita_2020_1_role_repasse_capital_nao_conferida.valor
    assert fechamento.total_repasses_capital == total_repasses_capital_esperado

    total_receitas_custeio_esperado = receita_2020_1_role_rendimento_custeio_conferida.valor + \
                                      receita_2020_1_role_repasse_custeio_conferida.valor
    assert fechamento.total_receitas_custeio == total_receitas_custeio_esperado
    assert fechamento.total_receitas_nao_conciliadas_custeio == 0

    total_repasses_custeio_esperado = receita_2020_1_role_repasse_custeio_conferida.valor
    assert fechamento.total_repasses_custeio == total_repasses_custeio_esperado

    total_despesas_capital = rateio_despesa_2020_role_capital_conferido.valor_rateio
    assert fechamento.total_despesas_capital == total_despesas_capital
    assert fechamento.total_despesas_nao_conciliadas_capital == 0

    total_despesas_custeio = rateio_despesa_2020_role_custeio_conferido.valor_rateio + \
                             rateio_despesa_2020_role_custeio_nao_conferido.valor_rateio
    assert fechamento.total_despesas_custeio == total_despesas_custeio
    assert fechamento.total_despesas_nao_conciliadas_custeio == rateio_despesa_2020_role_custeio_nao_conferido.valor_rateio


@pytest.fixture
def _periodo_2019_2(periodo):
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 6, 1),
        data_fim_realizacao_despesas=date(2019, 12, 30),
        data_prevista_repasse=date(2019, 6, 1),
        data_inicio_prestacao_contas=date(2020, 1, 1),
        data_fim_prestacao_contas=date(2020, 1, 10),
        periodo_anterior=periodo
    )


@pytest.fixture
def _periodo_2020_1(_periodo_2019_2):
    return baker.make(
        'Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=date(2020, 1, 1),
        data_fim_realizacao_despesas=date(2020, 6, 30),
        data_prevista_repasse=date(2020, 1, 1),
        data_inicio_prestacao_contas=date(2020, 7, 1),
        data_fim_prestacao_contas=date(2020, 7, 10),
        periodo_anterior=_periodo_2019_2
    )


@pytest.fixture
def _fechamento_2019_2(_periodo_2019_2, associacao, conta_associacao, acao_associacao, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=_periodo_2019_2,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=500,
        total_repasses_capital=450,
        total_despesas_capital=400,
        total_receitas_custeio=1000,
        total_repasses_custeio=900,
        total_despesas_custeio=800,
    )


@pytest.fixture
def _receita_2020_1(associacao, conta_associacao, acao_associacao, tipo_receita_rendimento):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita_rendimento,
        conferido=True,
    )


@pytest.mark.django_db(transaction=False)
def test_fechamentos_devem_ser_vinculados_a_anteriores(_fechamento_2019_2,
                                                       associacao,
                                                       _periodo_2019_2,
                                                       _periodo_2020_1,
                                                       _receita_2020_1,
                                                       acao_associacao,
                                                       settings):
    from sme_ptrf_apps.core.tasks import concluir_prestacao_de_contas_async
    from celery.result import EagerResult

    settings.CELERY_TASK_ALWAYS_EAGER = True
    task_result = concluir_prestacao_de_contas_async.delay(_periodo_2020_1.uuid, associacao.uuid)
    assert isinstance(task_result, EagerResult)
    prestacao = PrestacaoConta.objects.filter(periodo=_periodo_2020_1, associacao=associacao).first()
    assert prestacao

    fechamento = prestacao.fechamentos_da_prestacao.first()

    assert fechamento.fechamento_anterior == _fechamento_2019_2, "Deveria apontar para o fechamento anterior."


@pytest.mark.django_db(transaction=False)
def test_deve_gravar_lista_de_especificacoes_despesas(associacao,
                                                      periodo_2020_1,
                                                      despesa_2020_1,
                                                      rateio_despesa_2020_role_custeio_conferido,
                                                      rateio_despesa_2020_role_custeio_nao_conferido,
                                                      rateio_despesa_2020_role_capital_conferido,
                                                      despesa_2019_2,
                                                      rateio_despesa_2019_role_conferido,
                                                      settings):
    from sme_ptrf_apps.core.tasks import concluir_prestacao_de_contas_async
    from celery.result import EagerResult

    settings.CELERY_TASK_ALWAYS_EAGER = True
    task_result = concluir_prestacao_de_contas_async.delay(periodo_2020_1.uuid, associacao.uuid)
    assert isinstance(task_result, EagerResult)
    prestacao = PrestacaoConta.objects.filter(periodo=periodo_2020_1, associacao=associacao).first()
    assert prestacao

    assert prestacao.fechamentos_da_prestacao.count() == 1, "Deveriam ter sido criado apenas um fechamento."

    fechamento = prestacao.fechamentos_da_prestacao.first()
    assert fechamento.especificacoes_despesas_capital == ['Ar condicionado', ]
    assert fechamento.especificacoes_despesas_custeio == ['Instalação elétrica', ]


@pytest.mark.django_db(transaction=False)
def test_deve_sumarizar_transacoes_considerando_conta(associacao,
                                                      conta_associacao_cartao,
                                                      conta_associacao_cheque,
                                                      periodo_2020_1,
                                                      receita_2020_1_role_repasse_custeio_conferida,
                                                      receita_2020_1_role_repasse_capital_nao_conferida,
                                                      receita_2019_2_role_repasse_capital_conferida,
                                                      receita_2020_1_role_repasse_capital_conferida,
                                                      receita_2020_1_role_rendimento_custeio_conferida,
                                                      despesa_2020_1,
                                                      rateio_despesa_2020_role_custeio_conferido,
                                                      rateio_despesa_2020_role_custeio_nao_conferido,
                                                      rateio_despesa_2020_role_capital_conferido,
                                                      despesa_2019_2,
                                                      rateio_despesa_2019_role_conferido,
                                                      receita_2020_1_role_repasse_custeio_conferida_outra_conta,
                                                      rateio_despesa_2020_role_custeio_conferido_outra_conta,
                                                      settings):
    from sme_ptrf_apps.core.tasks import concluir_prestacao_de_contas_async
    from celery.result import EagerResult

    settings.CELERY_TASK_ALWAYS_EAGER = True
    task_result = concluir_prestacao_de_contas_async.delay(periodo_2020_1.uuid, associacao.uuid)
    assert isinstance(task_result, EagerResult)
    prestacao = PrestacaoConta.objects.filter(periodo=periodo_2020_1, associacao=associacao).first()
    assert prestacao

    assert prestacao.fechamentos_da_prestacao.count() == 2, "Deveriam ter sido criados dois fechamentos."

    fechamento = prestacao.fechamentos_da_prestacao.filter(conta_associacao=conta_associacao_cartao).first()

    total_receitas_capital_esperado = receita_2020_1_role_repasse_capital_conferida.valor + \
                                      receita_2020_1_role_repasse_capital_nao_conferida.valor
    assert fechamento.total_receitas_capital == total_receitas_capital_esperado
    assert fechamento.total_receitas_nao_conciliadas_capital == receita_2020_1_role_repasse_capital_nao_conferida.valor

    total_repasses_capital_esperado = receita_2020_1_role_repasse_capital_conferida.valor + \
                                      receita_2020_1_role_repasse_capital_nao_conferida.valor
    assert fechamento.total_repasses_capital == total_repasses_capital_esperado

    total_receitas_custeio_esperado = receita_2020_1_role_rendimento_custeio_conferida.valor + \
                                      receita_2020_1_role_repasse_custeio_conferida.valor
    assert fechamento.total_receitas_custeio == total_receitas_custeio_esperado
    assert fechamento.total_receitas_nao_conciliadas_custeio == 0

    total_repasses_custeio_esperado = receita_2020_1_role_repasse_custeio_conferida.valor
    assert fechamento.total_repasses_custeio == total_repasses_custeio_esperado

    total_despesas_capital = rateio_despesa_2020_role_capital_conferido.valor_rateio
    assert fechamento.total_despesas_capital == total_despesas_capital
    assert fechamento.total_despesas_nao_conciliadas_capital == 0

    total_despesas_custeio = rateio_despesa_2020_role_custeio_conferido.valor_rateio + \
                             rateio_despesa_2020_role_custeio_nao_conferido.valor_rateio
    assert fechamento.total_despesas_custeio == total_despesas_custeio
    assert fechamento.total_despesas_nao_conciliadas_custeio == rateio_despesa_2020_role_custeio_nao_conferido.valor_rateio


@pytest.mark.django_db(transaction=False)
def test_demonstrativos_financeiros_devem_ser_criados_por_conta_e_acao(associacao,
                                                                       periodo_2020_1,
                                                                       receita_2020_1_role_repasse_custeio_conferida,
                                                                       receita_2020_1_ptrf_repasse_capital_conferida,
                                                                       receita_2020_1_role_repasse_capital_nao_conferida,
                                                                       receita_2019_2_role_repasse_capital_conferida,
                                                                       receita_2020_1_role_repasse_capital_conferida,
                                                                       receita_2020_1_role_rendimento_custeio_conferida,
                                                                       receita_2020_1_role_repasse_custeio_conferida_outra_conta,
                                                                       despesa_2020_1,
                                                                       rateio_despesa_2020_role_custeio_conferido,
                                                                       rateio_despesa_2020_role_custeio_nao_conferido,
                                                                       rateio_despesa_2020_role_capital_conferido,
                                                                       despesa_2019_2,
                                                                       rateio_despesa_2019_role_conferido,
                                                                       acao_associacao_ptrf,
                                                                       settings):
    from sme_ptrf_apps.core.tasks import concluir_prestacao_de_contas_async
    from celery.result import EagerResult

    settings.CELERY_TASK_ALWAYS_EAGER = True
    task_result = concluir_prestacao_de_contas_async.delay(periodo_2020_1.uuid, associacao.uuid, criar_arquivos=False)
    assert isinstance(task_result, EagerResult)
    prestacao = PrestacaoConta.objects.filter(periodo=periodo_2020_1, associacao=associacao).first()
    assert prestacao
    assert prestacao.demonstrativos_da_prestacao.count() == 2, "Deveriam ter sido criados 2(contas)."


@pytest.mark.django_db(transaction=False)
def test_relacoes_de_bens_devem_ser_criadas_por_conta(associacao,
                                                      periodo_2020_1,
                                                      receita_2020_1_role_repasse_custeio_conferida,
                                                      receita_2020_1_ptrf_repasse_capital_conferida,
                                                      receita_2020_1_role_repasse_capital_nao_conferida,
                                                      receita_2019_2_role_repasse_capital_conferida,
                                                      receita_2020_1_role_repasse_capital_conferida,
                                                      receita_2020_1_role_rendimento_custeio_conferida,
                                                      receita_2020_1_role_repasse_custeio_conferida_outra_conta,
                                                      despesa_2020_1,
                                                      rateio_despesa_2020_role_custeio_conferido,
                                                      rateio_despesa_2020_role_custeio_nao_conferido,
                                                      rateio_despesa_2020_role_capital_conferido,
                                                      despesa_2019_2,
                                                      rateio_despesa_2019_role_conferido,
                                                      acao_associacao_ptrf,
                                                      settings):
    from sme_ptrf_apps.core.tasks import concluir_prestacao_de_contas_async
    from celery.result import EagerResult

    settings.CELERY_TASK_ALWAYS_EAGER = True
    task_result = concluir_prestacao_de_contas_async.delay(periodo_2020_1.uuid, associacao.uuid, criar_arquivos=False)
    assert isinstance(task_result, EagerResult)
    prestacao = PrestacaoConta.objects.filter(periodo=periodo_2020_1, associacao=associacao).first()
    assert prestacao

    assert prestacao.relacoes_de_bens_da_prestacao.count() == 1, "Deveriam ter sido criados uma, 1 contas."

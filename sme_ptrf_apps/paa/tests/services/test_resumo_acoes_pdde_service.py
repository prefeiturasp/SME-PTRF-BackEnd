import pytest

from sme_ptrf_apps.paa.models import AcaoPdde
from sme_ptrf_apps.paa.services.acoes_pdde_service import ResumoAcoesPddeService


def node_programa(dados, uuid):
    return next(node for node in dados if node['key'] == str(uuid))


def node_total(dados):
    return next(node for node in dados if node['key'] == 'total-pdde')


@pytest.mark.django_db
def test_resumo_por_programa_sem_acoes(paa):
    dados = ResumoAcoesPddeService(paa).resumo_por_programa()

    assert len(dados) == 1
    total = dados[0]
    assert total['key'] == 'total-pdde'
    assert total['nome'] == 'Total do PDDE'
    assert total['level'] == 0
    assert total['custeio'] == 0
    assert total['capital'] == 0
    assert total['livre_aplicacao'] == 0
    assert 'children' not in total


@pytest.mark.django_db
def test_resumo_por_programa_acao_sem_receita_prevista(paa, acao_pdde):
    dados = ResumoAcoesPddeService(paa).resumo_por_programa()
    PREFIXO = "PDDE"
    SUFIXO = "Total"
    programa = node_programa(dados, acao_pdde.programa.uuid)
    assert programa['nome'] == f'{PREFIXO} {acao_pdde.programa.nome} {SUFIXO}', programa['nome']
    assert programa['level'] == 0
    assert programa['custeio'] == 0
    assert programa['capital'] == 0
    assert programa['livre_aplicacao'] == 0
    assert len(programa['children']) == 1

    node_acao = programa['children'][0]
    assert node_acao['key'] == str(acao_pdde.uuid)
    assert node_acao['nome'] == f'{PREFIXO} {acao_pdde.nome}'
    assert node_acao['level'] == 1
    assert node_acao['aceita_custeio'] == acao_pdde.aceita_custeio
    assert node_acao['aceita_capital'] == acao_pdde.aceita_capital
    assert node_acao['aceita_livre_aplicacao'] == acao_pdde.aceita_livre_aplicacao
    assert node_acao['custeio'] == 0
    assert node_acao['capital'] == 0
    assert node_acao['livre_aplicacao'] == 0
    assert node_acao['acao']['receitas_previstas_pdde_valores'] is None

    total = node_total(dados)
    assert total['custeio'] == 0
    assert total['capital'] == 0
    assert total['livre_aplicacao'] == 0


@pytest.mark.django_db
def test_resumo_por_programa_acao_com_receita_prevista(paa, acao_pdde, receita_prevista_pdde_factory):
    receita = receita_prevista_pdde_factory.create(
        paa=paa,
        acao_pdde=acao_pdde,
        previsao_valor_custeio=100,
        previsao_valor_capital=200,
        previsao_valor_livre=300,
        saldo_custeio=10,
        saldo_capital=20,
        saldo_livre=30,
    )

    dados = ResumoAcoesPddeService(paa).resumo_por_programa()

    programa = node_programa(dados, acao_pdde.programa.uuid)
    node_acao = programa['children'][0]

    assert node_acao['custeio'] == 110
    assert node_acao['capital'] == 220
    assert node_acao['livre_aplicacao'] == 330

    receita_serializada = node_acao['acao']['receitas_previstas_pdde_valores']
    assert receita_serializada['uuid'] == str(receita.uuid)
    assert receita_serializada['previsao_valor_custeio'] == 100
    assert receita_serializada['previsao_valor_capital'] == 200
    assert receita_serializada['previsao_valor_livre'] == 300
    assert receita_serializada['saldo_custeio'] == 10
    assert receita_serializada['saldo_capital'] == 20
    assert receita_serializada['saldo_livre'] == 30

    assert programa['custeio'] == 110
    assert programa['capital'] == 220
    assert programa['livre_aplicacao'] == 330

    total = node_total(dados)
    assert total['custeio'] == 110
    assert total['capital'] == 220
    assert total['livre_aplicacao'] == 330


@pytest.mark.django_db
def test_resumo_por_programa_agrega_acoes_do_mesmo_programa(
    paa, programa_pdde, acao_pdde_factory, receita_prevista_pdde_factory
):
    acao_1 = acao_pdde_factory.create(programa=programa_pdde)
    acao_2 = acao_pdde_factory.create(programa=programa_pdde)

    receita_prevista_pdde_factory.create(
        paa=paa, acao_pdde=acao_1,
        previsao_valor_custeio=100, previsao_valor_capital=0, previsao_valor_livre=0,
        saldo_custeio=0, saldo_capital=0, saldo_livre=0,
    )
    receita_prevista_pdde_factory.create(
        paa=paa, acao_pdde=acao_2,
        previsao_valor_custeio=50, previsao_valor_capital=0, previsao_valor_livre=0,
        saldo_custeio=0, saldo_capital=0, saldo_livre=0,
    )

    dados = ResumoAcoesPddeService(paa).resumo_por_programa()

    programa = node_programa(dados, programa_pdde.uuid)
    assert len(programa['children']) == 2
    assert programa['custeio'] == 150

    total = node_total(dados)
    assert total['custeio'] == 150


@pytest.mark.django_db
def test_resumo_por_programa_com_programas_diferentes(paa, acao_pdde_factory, programa_pdde_factory):
    programa_1 = programa_pdde_factory.create()
    programa_2 = programa_pdde_factory.create()
    acao_pdde_factory.create(programa=programa_1)
    acao_pdde_factory.create(programa=programa_2)

    dados = ResumoAcoesPddeService(paa).resumo_por_programa()

    # 2 programas + node "Total do PDDE"
    assert len(dados) == 3
    assert node_programa(dados, programa_1.uuid)
    assert node_programa(dados, programa_2.uuid)
    assert node_total(dados)


@pytest.mark.django_db
def test_resumo_por_programa_ignora_acao_sem_programa(paa, acao_pdde_factory):
    acao_pdde_factory.create(programa=None)

    dados = ResumoAcoesPddeService(paa).resumo_por_programa()

    assert len(dados) == 1
    assert node_total(dados)['custeio'] == 0


@pytest.mark.django_db
def test_resumo_por_programa_ignora_acao_inativa(paa, acao_pdde_factory, programa_pdde):
    acao_pdde_factory.create(programa=programa_pdde, status=AcaoPdde.STATUS_INATIVA)

    dados = ResumoAcoesPddeService(paa).resumo_por_programa()

    assert len(dados) == 1
    assert node_total(dados)


@pytest.mark.django_db
def test_resumo_por_programa_ignora_receita_de_outro_paa(
    paa, acao_pdde, paa_factory, receita_prevista_pdde_factory
):
    outro_paa = paa_factory.create()
    receita_prevista_pdde_factory.create(
        paa=outro_paa, acao_pdde=acao_pdde,
        previsao_valor_custeio=999,
    )

    dados = ResumoAcoesPddeService(paa).resumo_por_programa()

    programa = node_programa(dados, acao_pdde.programa.uuid)
    node_acao = programa['children'][0]

    assert node_acao['acao']['receitas_previstas_pdde_valores'] is None
    assert node_acao['custeio'] == 0

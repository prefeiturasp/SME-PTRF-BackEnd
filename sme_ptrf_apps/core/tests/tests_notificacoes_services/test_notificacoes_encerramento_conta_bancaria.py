from types import SimpleNamespace
from unittest.mock import patch

import pytest
from model_bakery import baker

from ...models import Notificacao
from sme_ptrf_apps.core.services.notificacao_services import notificar_encerramento_conta_bancaria

pytestmark = pytest.mark.django_db

PATH_PAINEL = (
    'sme_ptrf_apps.core.services.notificacao_services'
    '.notificacao_encerramento_conta_bancaria_service'
    '.PainelResumoRecursosService.painel_resumo_recursos'
)


@pytest.fixture
def mock_painel_saldo_zerado():
    with patch(PATH_PAINEL) as mock:
        mock.return_value = SimpleNamespace(info_conta=SimpleNamespace(saldo_atual_total=0))
        yield mock


@pytest.fixture
def mock_painel_saldo_nao_zerado():
    with patch(PATH_PAINEL) as mock:
        mock.return_value = SimpleNamespace(info_conta=SimpleNamespace(saldo_atual_total=100))
        yield mock


@pytest.fixture
def periodo_inicial_associacao_encerramento_conta(associacao_encerramento_conta, periodo_2020_1, recurso_legado):
    return baker.make(
        'PeriodoInicialAssociacao',
        associacao=associacao_encerramento_conta,
        periodo_inicial=periodo_2020_1,
        recurso=recurso_legado,
    )


def test_deve_notificar_usuarios_encerramento_conta(
    periodo_2021_1,
    periodo_2020_2,
    periodo_inicial_associacao_encerramento_conta,
    parametro_numero_periodos_consecutivos,
    conta_associacao_encerramento_conta,
    usuario_notificavel,
    mock_painel_saldo_zerado,
):
    assert not Notificacao.objects.exists()
    notificar_encerramento_conta_bancaria(enviar_email=False)
    assert Notificacao.objects.count() == 1
    notificacao = Notificacao.objects.first()

    assert notificacao.tipo == Notificacao.TIPO_NOTIFICACAO_AVISO
    assert notificacao.categoria == Notificacao.CATEGORIA_NOTIFICACAO_ENCERRAMENTO_CONTA_BANCARIA
    assert notificacao.remetente == Notificacao.REMETENTE_NOTIFICACAO_SISTEMA
    assert notificacao.titulo == "Encerramento de Conta Bancária"
    assert (
        f"O saldo da conta bancária {conta_associacao_encerramento_conta.tipo_conta.nome} está zerada"
        in notificacao.descricao
    )
    assert "Recurso:" in notificacao.descricao
    assert notificacao.usuario == usuario_notificavel


def test_nao_deve_notificar_usuarios_sem_permissao_encerramento_conta(
    periodo_2021_1,
    periodo_2020_2,
    periodo_inicial_associacao_encerramento_conta,
    parametro_numero_periodos_consecutivos,
    conta_associacao_encerramento_conta,
    usuario_nao_notificavel,
    mock_painel_saldo_zerado,
):
    assert not Notificacao.objects.exists()
    notificar_encerramento_conta_bancaria(enviar_email=False)
    assert Notificacao.objects.count() == 0


def test_nao_deve_notificar_usuarios_que_tipo_conta_nao_permite_inativacao(
    periodo_2021_1,
    periodo_2020_2,
    periodo_inicial_associacao_encerramento_conta,
    parametro_numero_periodos_consecutivos,
    conta_associacao_encerramento_conta,
    conta_associacao_sem_permissao_encerramento_conta,
    usuario_notificavel,
    mock_painel_saldo_zerado,
):
    assert not Notificacao.objects.exists()
    notificar_encerramento_conta_bancaria(enviar_email=False)
    # Apenas uma das contas tem permissão de inativação
    assert Notificacao.objects.count() == 1


def test_nao_deve_notificar_associacoes_que_parametro_e_maior_que_periodos_da_associacao(
    periodo_2021_1,
    parametro_numero_periodos_consecutivos_02,
    conta_associacao_encerramento_conta,
    usuario_notificavel,
    mock_painel_saldo_zerado,
):
    assert not Notificacao.objects.exists()
    notificar_encerramento_conta_bancaria(enviar_email=False)
    assert Notificacao.objects.count() == 0


def test_nao_deve_notificar_associacoes_que_periodos_consecutivos_nao_estao_zerados(
    periodo_2021_1,
    periodo_2020_2,
    periodo_inicial_associacao_encerramento_conta,
    parametro_numero_periodos_consecutivos,
    conta_associacao_encerramento_conta,
    usuario_notificavel,
    mock_painel_saldo_nao_zerado,
):
    assert not Notificacao.objects.exists()
    notificar_encerramento_conta_bancaria(enviar_email=False)
    assert Notificacao.objects.count() == 0


def test_nao_notifica_quando_numero_periodos_consecutivos_e_zero(
    periodo_2021_1,
    periodo_2020_2,
    conta_associacao_encerramento_conta,
    usuario_notificavel,
):
    baker.make('Parametros', numero_periodos_consecutivos=0)

    assert not Notificacao.objects.exists()
    notificar_encerramento_conta_bancaria(enviar_email=False)
    assert Notificacao.objects.count() == 0

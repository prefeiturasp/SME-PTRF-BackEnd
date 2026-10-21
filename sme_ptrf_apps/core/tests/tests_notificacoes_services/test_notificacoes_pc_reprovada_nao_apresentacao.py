import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from ....core.models import Notificacao
from ....users.models import Grupo
from ....core.services.notificacao_services.notificacao_prestacao_de_contas_reprovada_nao_apresentacao import (
    notificar_prestacao_de_contas_reprovada_nao_apresentacao,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def permissao_pc_reprovada_nao_apresentacao():
    return Permission.objects.get(codename='recebe_notificacao_conclusao_reprovada_pc_nao_apresentada')


@pytest.fixture
def grupo_com_permissao_pc_reprovada_nao_apresentacao(permissao_pc_reprovada_nao_apresentacao):
    grupo = Grupo.objects.create(name="grupo_pc_reprovada_nao_apresentacao")
    grupo.permissions.add(permissao_pc_reprovada_nao_apresentacao)
    grupo.descricao = "Grupo de teste"
    grupo.save()
    return grupo


@pytest.fixture
def prestacao_conta_reprovada_nao_apresentacao_teste(associacao, periodo_2020_1):
    from model_bakery import baker
    return baker.make(
        'PrestacaoContaReprovadaNaoApresentacao',
        associacao=associacao,
        periodo=periodo_2020_1,
    )


def _criar_usuario(username, unidades=None, grupos=None, visoes=None):
    User = get_user_model()
    usuario = User.objects.create_user(username=username, password='Sgp0418', email=f'{username}@amcom.com.br')
    for unidade in unidades or []:
        usuario.unidades.add(unidade)
    for grupo in grupos or []:
        usuario.groups.add(grupo)
    for visao in visoes or []:
        usuario.visoes.add(visao)
    usuario.save()
    return usuario


def test_notifica_usuario_elegivel_mas_quebra_por_tipo_de_prestacao_conta_incompativel(
    prestacao_conta_reprovada_nao_apresentacao_teste,
    associacao,
    grupo_com_permissao_pc_reprovada_nao_apresentacao,
    visao_ue,
):
    """Cobre o caminho onde um usuário elegível é encontrado e a notificação é
    montada e disparada.

    BUG conhecido (não corrigido a pedido): o service passa
    `prestacao_conta=prestacao_de_contas` para `Notificacao.notificar(...)`, mas
    `prestacao_de_contas` aqui é uma instância de `PrestacaoContaReprovadaNaoApresentacao`,
    enquanto `Notificacao.prestacao_conta` é FK estrita para `PrestacaoConta`. Isso
    faz `Notificacao.notificar` levantar `ValueError` sempre que há usuário elegível —
    ou seja, em produção esse fluxo nunca notifica ninguém de fato (a exceção é
    engolida pelo try/except genérico da view). Este teste documenta o
    comportamento atual; se o bug for corrigido, ele deve ser atualizado para
    validar a notificação criada normalmente.
    """
    _criar_usuario(
        '2711001',
        unidades=[associacao.unidade],
        grupos=[grupo_com_permissao_pc_reprovada_nao_apresentacao],
        visoes=[visao_ue],
    )

    assert not Notificacao.objects.exists()

    with pytest.raises(ValueError, match='Must be "PrestacaoConta" instance'):
        notificar_prestacao_de_contas_reprovada_nao_apresentacao(
            prestacao_conta_reprovada_nao_apresentacao_teste, enviar_email=False
        )

    assert not Notificacao.objects.exists()


def test_nao_notifica_sem_usuarios_com_permissao(
    prestacao_conta_reprovada_nao_apresentacao_teste,
):
    assert not Notificacao.objects.exists()

    notificar_prestacao_de_contas_reprovada_nao_apresentacao(
        prestacao_conta_reprovada_nao_apresentacao_teste, enviar_email=False
    )

    assert Notificacao.objects.count() == 0


def test_nao_notifica_usuario_com_permissao_mas_sem_visao_ue(
    prestacao_conta_reprovada_nao_apresentacao_teste,
    associacao,
    grupo_com_permissao_pc_reprovada_nao_apresentacao,
    visao_dre,
):
    _criar_usuario(
        '2711002',
        unidades=[associacao.unidade],
        grupos=[grupo_com_permissao_pc_reprovada_nao_apresentacao],
        visoes=[visao_dre],
    )

    assert not Notificacao.objects.exists()

    notificar_prestacao_de_contas_reprovada_nao_apresentacao(
        prestacao_conta_reprovada_nao_apresentacao_teste, enviar_email=False
    )

    assert Notificacao.objects.count() == 0


def test_nao_notifica_usuario_de_outra_unidade(
    prestacao_conta_reprovada_nao_apresentacao_teste,
    grupo_com_permissao_pc_reprovada_nao_apresentacao,
    visao_ue,
    outra_unidade,
):
    _criar_usuario(
        '2711003',
        unidades=[outra_unidade],
        grupos=[grupo_com_permissao_pc_reprovada_nao_apresentacao],
        visoes=[visao_ue],
    )

    assert not Notificacao.objects.exists()

    notificar_prestacao_de_contas_reprovada_nao_apresentacao(
        prestacao_conta_reprovada_nao_apresentacao_teste, enviar_email=False
    )

    assert Notificacao.objects.count() == 0


def test_nao_notifica_usuario_sem_periodo_inicial_no_recurso(
    associacao,
    grupo_com_permissao_pc_reprovada_nao_apresentacao,
    visao_ue,
    periodo_factory,
):
    """Usuário vinculado à unidade certa, mas a associação só tem período
    inicial para o recurso legado — uma PC de outro recurso não deve notificá-lo."""
    from model_bakery import baker

    outro_recurso = baker.make('Recurso', nome_exibicao='Outro Recurso', cor='#01585E')
    periodo_outro_recurso = periodo_factory(referencia='2020.1', recurso=outro_recurso)
    pc_outro_recurso = baker.make(
        'PrestacaoContaReprovadaNaoApresentacao',
        associacao=associacao,
        periodo=periodo_outro_recurso,
    )

    _criar_usuario(
        '2711004',
        unidades=[associacao.unidade],
        grupos=[grupo_com_permissao_pc_reprovada_nao_apresentacao],
        visoes=[visao_ue],
    )

    assert not Notificacao.objects.exists()

    notificar_prestacao_de_contas_reprovada_nao_apresentacao(pc_outro_recurso, enviar_email=False)

    assert Notificacao.objects.count() == 0

import pytest

from freezegun import freeze_time

from ....core.models import Notificacao
from ....core.services.notificacao_services import notificar_pendencia_envio_prestacao_de_contas

pytestmark = pytest.mark.django_db


@freeze_time("2021-06-17")
def test_deve_notificar_usuarios(
    periodo_notifica_pendencia_envio_pc,
    usuario_notificavel,
    associacao_teste_pendencia_envio_pc,
):
    assert not Notificacao.objects.exists()
    notificar_pendencia_envio_prestacao_de_contas(enviar_email=False)
    assert Notificacao.objects.count() == 1
    notificacao = Notificacao.objects.first()

    recurso = periodo_notifica_pendencia_envio_pc.recurso

    assert notificacao.tipo == Notificacao.TIPO_NOTIFICACAO_ALERTA
    assert notificacao.categoria == Notificacao.CATEGORIA_NOTIFICACAO_ELABORACAO_PC
    assert notificacao.remetente == Notificacao.REMETENTE_NOTIFICACAO_SISTEMA
    assert notificacao.titulo == f"Pendência de envio de PC {periodo_notifica_pendencia_envio_pc.referencia}"
    assert notificacao.descricao == (
        f"Terminou o período de prestações de contas para a associação {associacao_teste_pendencia_envio_pc.unidade.codigo_eol} - "
        f"{associacao_teste_pendencia_envio_pc.unidade.nome} e você ainda não enviou sua PC.\n\n"
        f"Recurso: {recurso.nome}\n"
    )
    assert notificacao.usuario == usuario_notificavel


@freeze_time("2021-06-17")
def test_nao_deve_notificar_usuarios_sem_permissao(periodo_notifica_pendencia_envio_pc, usuario_nao_notificavel,
                                                   associacao_a):
    assert not Notificacao.objects.exists()
    notificar_pendencia_envio_prestacao_de_contas()
    assert Notificacao.objects.count() == 0


@freeze_time("2021-06-17")
def test_nao_deve_notificar_usuarios_periodo_invalido(periodo_2021_4_pc_2021_06_18_a_2021_06_30, usuario_notificavel,
                                                      associacao_a):
    assert not Notificacao.objects.exists()
    notificar_pendencia_envio_prestacao_de_contas()
    assert Notificacao.objects.count() == 0


@freeze_time("2021-06-17")
def test_nao_deve_notificar_usuarios_pc_em_analise(periodo_notifica_pendencia_envio_pc,
                                                   prestacao_nao_notifica_pendencia_envio_pc, usuario_notificavel,
                                                   associacao_a):
    assert not Notificacao.objects.exists()
    notificar_pendencia_envio_prestacao_de_contas()
    assert Notificacao.objects.count() == 0

import pytest

from sme_ptrf_apps.core.models import Notificacao

from sme_ptrf_apps.dre.services.dre_service import DreService

pytestmark = pytest.mark.django_db


def test_usuarios_sao_notificados_de_devolucao_para_comissao_contas(
    dre_valida,
    jose_membro_comissao_exame_contas_da_dre,
    ana_membro_comissao_exame_contas_da_dre,
    pedro_membro_outra_comissao_da_dre,
    maria_membro_comissao_exame_contas_de_outra_dre,
    parametros_dre_comissoes,
    usuario_servidor_jose,
    usuario_servidor_ana,
    usuario_servidor_pedro,
    usuario_servidor_maria,
    consolidado_dre_parcial_1_devolvido,
):
    assert not Notificacao.objects.exists()

    dre_service = DreService(dre_valida)
    dre_service.notificar_devolucao_consolidado(consolidado_dre=consolidado_dre_parcial_1_devolvido, enviar_email=False)

    assert Notificacao.objects.count() == 2
    assert Notificacao.objects.filter(usuario=usuario_servidor_jose).exists()
    assert Notificacao.objects.filter(usuario=usuario_servidor_ana).exists()


def test_usuarios_sao_notificados_de_devolucao_ignora_membros_sem_usuario(
    dre_valida,
    jose_membro_comissao_exame_contas_da_dre,
    ana_membro_comissao_exame_contas_da_dre,
    pedro_membro_outra_comissao_da_dre,
    maria_membro_comissao_exame_contas_de_outra_dre,
    parametros_dre_comissoes,
    usuario_servidor_jose,
    usuario_servidor_pedro,
    usuario_servidor_maria,
    consolidado_dre_parcial_1_devolvido,
):
    assert not Notificacao.objects.exists()

    dre_service = DreService(dre_valida)
    dre_service.notificar_devolucao_consolidado(consolidado_dre=consolidado_dre_parcial_1_devolvido, enviar_email=False)

    assert Notificacao.objects.count() == 1



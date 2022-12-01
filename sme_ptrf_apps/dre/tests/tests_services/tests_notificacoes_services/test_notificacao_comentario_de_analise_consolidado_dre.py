from freezegun import freeze_time
import pytest

from sme_ptrf_apps.core.models import Notificacao
from sme_ptrf_apps.dre.models import ComentarioAnaliseConsolidadoDRE

pytestmark = pytest.mark.django_db


@pytest.fixture
def retorna_lista_de_uuids_de_comentarios(
    comentario_analise_consolidado_dre_01
):
    uuid_comentario_01 = f"{comentario_analise_consolidado_dre_01.uuid}"
    lista_de_uuids_de_comentarios = [uuid_comentario_01]

    return lista_de_uuids_de_comentarios


@freeze_time("2022-10-20")
def test_nao_deve_notificar_comentario_de_analise_consolidado_dre_nao_eh_a_dre_do_comentario(
    retorna_lista_de_uuids_de_comentarios,
    comissao_exame_contas_teste_service,
    parametros_dre_teste_service,
    membro_comissao_outra_dre_nao_deve_notificar_teste_service,
    comentario_analise_consolidado_dre_01,
    dre_teste_service_notificacao_analise_consolidado_dre_nao_eh_a_dre_do_membro,
    periodo_teste_api_comentario_analise_consolidado_dre,
    consolidado_dre_teste_api_comentario_analise_consolidado_dre,
    jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre,
):
    from sme_ptrf_apps.dre.services.notificacao_service.class_notificacao_comentario_de_analise_consolidado_dre import \
        NotificacaoComentarioDeAnaliseConsolidadoDre

    NotificacaoComentarioDeAnaliseConsolidadoDre(
        dre=dre_teste_service_notificacao_analise_consolidado_dre_nao_eh_a_dre_do_membro,
        periodo=periodo_teste_api_comentario_analise_consolidado_dre,
        comentarios=retorna_lista_de_uuids_de_comentarios,
        enviar_email=False
    ).notificar()

    assert not Notificacao.objects.exists()
    assert not comentario_analise_consolidado_dre_01.notificado
    assert not comentario_analise_consolidado_dre_01.notificado_em


@freeze_time("2022-10-20")
def test_nao_deve_notificar_comentario_de_analise_consolidado_dre_usuario_nao_membro_comissao_de_exame_de_contas(
    retorna_lista_de_uuids_de_comentarios,
    comissao_exame_contas_teste_service,
    parametros_dre_teste_service,
    nao_membro_comissao_de_exame_teste_service,
    comentario_analise_consolidado_dre_01,
    dre_teste_service_notificacao_analise_consolidado_dre,
    periodo_teste_api_comentario_analise_consolidado_dre,
    consolidado_dre_teste_api_comentario_analise_consolidado_dre,
    jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre,
):
    from sme_ptrf_apps.dre.services.notificacao_service.class_notificacao_comentario_de_analise_consolidado_dre import \
        NotificacaoComentarioDeAnaliseConsolidadoDre

    NotificacaoComentarioDeAnaliseConsolidadoDre(
        dre=dre_teste_service_notificacao_analise_consolidado_dre,
        periodo=periodo_teste_api_comentario_analise_consolidado_dre,
        comentarios=retorna_lista_de_uuids_de_comentarios,
        enviar_email=False
    ).notificar()

    assert not Notificacao.objects.exists()
    assert not comentario_analise_consolidado_dre_01.notificado
    assert not comentario_analise_consolidado_dre_01.notificado_em


@freeze_time("2022-10-20")
def test_notificar_comentario_de_analise_consolidado_dre(
    retorna_lista_de_uuids_de_comentarios,
    comissao_exame_contas_teste_service,
    parametros_dre_teste_service,
    membro_comissao_teste_service,
    comentario_analise_consolidado_dre_01,
    dre_teste_service_notificacao_analise_consolidado_dre,
    periodo_teste_api_comentario_analise_consolidado_dre,
    consolidado_dre_teste_api_comentario_analise_consolidado_dre,
    jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre,
):
    from sme_ptrf_apps.dre.services.notificacao_service.class_notificacao_comentario_de_analise_consolidado_dre import \
        NotificacaoComentarioDeAnaliseConsolidadoDre

    assert not Notificacao.objects.exists()
    assert not comentario_analise_consolidado_dre_01.notificado
    assert not comentario_analise_consolidado_dre_01.notificado_em

    NotificacaoComentarioDeAnaliseConsolidadoDre(
        dre=dre_teste_service_notificacao_analise_consolidado_dre,
        periodo=periodo_teste_api_comentario_analise_consolidado_dre,
        comentarios=retorna_lista_de_uuids_de_comentarios,
        enviar_email=False
    ).notificar()

    uuid = retorna_lista_de_uuids_de_comentarios[0]

    comentario_notificado = ComentarioAnaliseConsolidadoDRE.by_uuid(uuid)
    assert comentario_notificado.notificado
    assert comentario_notificado.notificado_em

    assert Notificacao.objects.count() == 1
    notificacao = Notificacao.objects.first()
    assert notificacao.tipo == Notificacao.TIPO_NOTIFICACAO_AVISO
    assert notificacao.categoria == Notificacao.CATEGORIA_NOTIFICACAO_COMENTARIO_CONSOLIDADO_DRE
    assert notificacao.remetente == Notificacao.REMETENTE_NOTIFICACAO_SME
    assert notificacao.titulo == f"Comentário feito em seu relatório consolidado de {periodo_teste_api_comentario_analise_consolidado_dre.referencia}."
    assert notificacao.descricao == f"{comentario_notificado.comentario}"

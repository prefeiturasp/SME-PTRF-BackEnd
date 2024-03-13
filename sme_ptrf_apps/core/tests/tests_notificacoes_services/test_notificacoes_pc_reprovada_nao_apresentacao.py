import pytest
from datetime import date

from django.contrib.auth.models import Permission

from ....core.models import Notificacao
from ....core.services.notificacao_services.notificacao_prestacao_de_contas_reprovada_nao_apresentacao import notificar_prestacao_de_contas_reprovada_nao_apresentacao

pytestmark = pytest.mark.django_db


def test_deve_notificar_usuarios(
    prestacao_conta_reprovada_nao_apresentacao_factory,
    associacao_factory,
    periodo_factory,
    usuario_factory,
    unidade_factory,
    visao_factory,
    grupo_acesso_factory,
):
    visao_ue = visao_factory.create(nome='UE')
    grupo_ue_1 = grupo_acesso_factory.create(name="ue_nivel1")
    unidade = unidade_factory.create()
    usuario_a_ser_notificado = usuario_factory.create()
    associacao = associacao_factory.create(
        unidade=unidade
    )
    periodo = periodo_factory.create(
        data_inicio_realizacao_despesas=date(2024, 1, 1),
        data_fim_realizacao_despesas=date(2024, 6, 1),
        referencia='2024.1',
    )
    pc = prestacao_conta_reprovada_nao_apresentacao_factory.create(
        periodo=periodo,
        associacao=associacao
    )
    permission_notificacao = Permission.objects.filter(codename='recebe_notificacao_conclusao_reprovada_pc_nao_apresentada').first()

    grupo_ue_1.permissions.add(permission_notificacao)
    usuario_a_ser_notificado.visoes.add(visao_ue)
    usuario_a_ser_notificado.groups.add(grupo_ue_1)
    usuario_a_ser_notificado.unidades.add(unidade)

    assert not Notificacao.objects.exists()

    notificar_prestacao_de_contas_reprovada_nao_apresentacao(pc)

    notificacao = Notificacao.objects.first()

    assert Notificacao.objects.count() == 1
    assert notificacao.tipo == Notificacao.TIPO_NOTIFICACAO_AVISO
    assert notificacao.categoria == Notificacao.CATEGORIA_NOTIFICACAO_CONCLUSAO_PC
    assert notificacao.remetente == Notificacao.REMETENTE_NOTIFICACAO_DRE
    assert notificacao.titulo == "Conclusão da PC como reprovada por não apresentação"
    assert notificacao.descricao == f"A PC {pc.periodo.referencia} foi concluída como reprovada pois não foi apresentada."
    assert notificacao.usuario == usuario_a_ser_notificado


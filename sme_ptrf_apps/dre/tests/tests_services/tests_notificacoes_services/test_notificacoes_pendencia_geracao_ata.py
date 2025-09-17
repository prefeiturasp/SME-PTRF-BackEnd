import pytest
from datetime import date
from django.contrib.auth.models import Permission

from sme_ptrf_apps.core.models import Notificacao
from sme_ptrf_apps.core.services.notificacao_services.notificacao_pendencia_geracao_ata import notificar_pendencia_geracao_ata_apresentacao, notificar_pendencia_geracao_ata_retificacao

pytestmark = pytest.mark.django_db


def test_notifica_pendencia_geracao_ata_apresentacao(visao_factory, grupo_acesso_factory, unidade_factory, usuario_factory, periodo_factory, associacao_factory, prestacao_conta_factory):
    visao_ue = visao_factory.create(nome='UE')
    grupo_ue_1 = grupo_acesso_factory.create(name="ue_nivel1")
    unidade = unidade_factory.create()
    usuario_a_ser_notificado = usuario_factory.create()
    associacao = associacao_factory.create(unidade=unidade)
    periodo_2023_1 = periodo_factory.create(data_inicio_realizacao_despesas=date(2023, 1, 1))
    pc = prestacao_conta_factory.create(periodo=periodo_2023_1, associacao=associacao)

    permission_notificacao = Permission.objects.filter(codename='recebe_notificacao_geracao_ata_apresentacao').first()
    grupo_ue_1.permissions.add(permission_notificacao)
    usuario_a_ser_notificado.visoes.add(visao_ue)
    usuario_a_ser_notificado.groups.add(grupo_ue_1)
    usuario_a_ser_notificado.unidades.add(unidade)

    notificar_pendencia_geracao_ata_apresentacao(pc)

    notificacao = Notificacao.objects.first()

    assert Notificacao.objects.count() == 1
    assert notificacao.tipo == Notificacao.TIPO_NOTIFICACAO_AVISO
    assert notificacao.categoria == Notificacao.CATEGORIA_NOTIFICACAO_GERACAO_ATA
    assert notificacao.remetente == Notificacao.REMETENTE_NOTIFICACAO_DRE
    assert notificacao.titulo == "Geração da ata de apresentação"
    assert notificacao.descricao == f"A ata de apresentação da PC {pc.periodo.referencia} não foi gerada e a DRE {pc.associacao.unidade.formata_nome_dre()} não pode receber a PC. Favor efetuar a geração da ata."
    assert notificacao.usuario == usuario_a_ser_notificado


def test_notifica_pendencia_geracao_ata_retificacao(visao_factory, grupo_acesso_factory, unidade_factory, usuario_factory, periodo_factory, associacao_factory, prestacao_conta_factory):
    visao_ue = visao_factory.create(nome='UE')
    grupo_ue_1 = grupo_acesso_factory.create(name="ue_nivel1")
    unidade = unidade_factory.create()
    usuario_a_ser_notificado = usuario_factory.create()
    associacao = associacao_factory.create(unidade=unidade)
    periodo_2023_1 = periodo_factory.create(data_inicio_realizacao_despesas=date(2023, 1, 1))
    pc = prestacao_conta_factory.create(periodo=periodo_2023_1, associacao=associacao)

    permission_notificacao = Permission.objects.filter(codename='recebe_notificacao_geracao_ata_retificacao').first()
    grupo_ue_1.permissions.add(permission_notificacao)
    usuario_a_ser_notificado.visoes.add(visao_ue)
    usuario_a_ser_notificado.groups.add(grupo_ue_1)
    usuario_a_ser_notificado.unidades.add(unidade)

    notificar_pendencia_geracao_ata_retificacao(pc)

    notificacao = Notificacao.objects.first()

    assert Notificacao.objects.count() == 1
    assert notificacao.tipo == Notificacao.TIPO_NOTIFICACAO_AVISO
    assert notificacao.categoria == Notificacao.CATEGORIA_NOTIFICACAO_GERACAO_ATA
    assert notificacao.remetente == Notificacao.REMETENTE_NOTIFICACAO_DRE
    assert notificacao.titulo == "Geração da ata de retificação"
    assert notificacao.descricao == f"A ata de retificação da PC {pc.periodo.referencia} não foi gerada e a DRE {pc.associacao.unidade.formata_nome_dre()} não pode receber a PC apresentada após acertos. Favor efetuar a geração da ata."
    assert notificacao.usuario == usuario_a_ser_notificado

import pytest
from datetime import date
from django.contrib.auth.models import Permission

from sme_ptrf_apps.core.fixtures.factories import PeriodoFactory, PrestacaoContaFactory, UnidadeFactory, AssociacaoFactory
from sme_ptrf_apps.users.fixtures.factories.usuario_factory import UsuarioFactory
from sme_ptrf_apps.users.fixtures.factories.visao_factory import VisaoFactory
from sme_ptrf_apps.users.fixtures.factories.grupo_acesso_factory import GrupoAcessoFactory
from sme_ptrf_apps.core.models import Notificacao
from sme_ptrf_apps.core.services.notificacao_services.notificacao_pendencia_geracao_ata import notificar_pendencia_geracao_ata_apresentacao

pytestmark = pytest.mark.django_db

def test_notifica_pendencia_geracao_ata_apresentacao():
    visao_ue = VisaoFactory(nome='UE')
    grupo_ue_1 = GrupoAcessoFactory(name="ue_nivel1")
    unidade = UnidadeFactory()
    usuario_a_ser_notificado = UsuarioFactory()
    associacao = AssociacaoFactory(unidade=unidade)
    periodo_2023_1 = PeriodoFactory(data_inicio_realizacao_despesas=date(2023, 1, 1))
    pc = PrestacaoContaFactory(periodo=periodo_2023_1, associacao=associacao)

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

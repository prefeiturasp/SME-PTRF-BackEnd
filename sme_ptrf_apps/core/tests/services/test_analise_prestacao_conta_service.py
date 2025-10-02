import pytest
from datetime import datetime, date
from sme_ptrf_apps.core.models import AnaliseContaPrestacaoConta
from sme_ptrf_apps.core.services.analise_prestacao_conta_service import cria_solicitacao_acerto_em_contas_com_pendencia

pytestmark = pytest.mark.django_db


def test_cria_solicitacao_acerto_em_contas_com_pendencia(
    periodo_factory,
    prestacao_conta_factory,
    analise_prestacao_conta_factory,
    conta_associacao_factory,

):
    periodo_2023_1 = periodo_factory.create(data_inicio_realizacao_despesas=datetime(2023, 1, 1),
                                            data_fim_realizacao_despesas=datetime(2023, 5, 30))
    pc = prestacao_conta_factory(periodo=periodo_2023_1, status="DEVOLVIDA", analise_atual=None)
    analise = analise_prestacao_conta_factory(prestacao_conta=pc)

    conta_associacao_factory(associacao=pc.associacao, data_inicio=date(2019, 2, 2))
    conta_associacao_factory(associacao=pc.associacao, data_inicio=date(2019, 2, 2))

    cria_solicitacao_acerto_em_contas_com_pendencia(analise)

    registros = AnaliseContaPrestacaoConta.objects.filter(analise_prestacao_conta=analise)

    assert registros.count() == 2
    assert all(
        r.observacao_solicitar_envio_do_comprovante_do_saldo_da_conta == "Corrigir pendências na conciliação"
        for r in registros
    )

import pytest
from datetime import date
from freezegun import freeze_time
from sme_ptrf_apps.situacao_patrimonial.services.bem_produzido_service import BemProduzidoService

pytestmark = pytest.mark.django_db


@freeze_time('2024-01-01')
class TestBemProduzidoServiceVerificarSePoderInformarValores:

    def test_sem_despesas_retorna_false(self):
        resultado = BemProduzidoService.verificar_se_pode_informar_valores([])
        assert resultado['pode_informar_valores'] is False

    def test_periodo_nao_finalizado_permite(self, associacao_factory, periodo_factory, despesa_factory):
        associacao = associacao_factory.create()
        periodo_factory.create(
            referencia='2025.1',
            data_inicio_realizacao_despesas=date(2025, 1, 1),
            data_fim_realizacao_despesas=date(2025, 4, 30),
        )
        despesa = despesa_factory.create(associacao=associacao, data_transacao='2025-01-15')
        
        resultado = BemProduzidoService.verificar_se_pode_informar_valores([despesa])
        assert resultado['pode_informar_valores'] is True

    def test_pc_nao_apresentada_permite(self, associacao_factory, periodo_factory, despesa_factory, prestacao_conta_factory):
        associacao = associacao_factory.create()
        periodo = periodo_factory.create(
            referencia='2023.1',
            data_inicio_realizacao_despesas=date(2023, 1, 1),
            data_fim_realizacao_despesas=date(2023, 4, 30),
        )
        despesa = despesa_factory.create(associacao=associacao, data_transacao='2023-01-15')
        prestacao_conta_factory.create(periodo=periodo, associacao=associacao, status='NAO_APRESENTADA')
        
        resultado = BemProduzidoService.verificar_se_pode_informar_valores([despesa])
        assert resultado['pode_informar_valores'] is True

    @pytest.mark.parametrize("status_pc", [
        'NAO_RECEBIDA', 'RECEBIDA', 'EM_ANALISE', 'DEVOLVIDA', 'DEVOLVIDA_RETORNADA',
        'DEVOLVIDA_RECEBIDA', 'APROVADA', 'APROVADA_RESSALVA', 'REPROVADA',
        'EM_PROCESSAMENTO', 'A_PROCESSAR', 'CALCULADA', 'DEVOLVIDA_CALCULADA',
    ])
    def test_todos_status_exceto_nao_apresentada_nao_permite(
        self, associacao_factory, periodo_factory, despesa_factory, prestacao_conta_factory, status_pc
    ):
        associacao = associacao_factory.create()
        periodo = periodo_factory.create(
            referencia='2023.1',
            data_inicio_realizacao_despesas=date(2023, 1, 1),
            data_fim_realizacao_despesas=date(2023, 4, 30),
        )
        despesa = despesa_factory.create(associacao=associacao, data_transacao='2023-01-15')
        prestacao_conta_factory.create(periodo=periodo, associacao=associacao, status=status_pc)
        
        resultado = BemProduzidoService.verificar_se_pode_informar_valores([despesa])
        assert resultado['pode_informar_valores'] is False

    def test_multiplas_despesas_uma_permite(
        self, associacao_factory, periodo_factory, despesa_factory, prestacao_conta_factory
    ):
        associacao = associacao_factory.create()
        
        periodo_1 = periodo_factory.create(referencia='2023.1', data_inicio_realizacao_despesas=date(2023, 1, 1), data_fim_realizacao_despesas=date(2023, 4, 30))
        despesa_1 = despesa_factory.create(associacao=associacao, data_transacao='2023-01-15')
        prestacao_conta_factory.create(periodo=periodo_1, associacao=associacao, status='APROVADA')
        
        periodo_2 = periodo_factory.create(referencia='2023.2', data_inicio_realizacao_despesas=date(2023, 5, 1), data_fim_realizacao_despesas=date(2023, 8, 31))
        despesa_2 = despesa_factory.create(associacao=associacao, data_transacao='2023-05-15')
        prestacao_conta_factory.create(periodo=periodo_2, associacao=associacao, status='NAO_APRESENTADA')
        
        resultado = BemProduzidoService.verificar_se_pode_informar_valores([despesa_1, despesa_2])
        assert resultado['pode_informar_valores'] is True


def _periodo(periodo_factory, recurso, referencia, inicio, fim):
    return periodo_factory.create(
        referencia=referencia,
        data_inicio_realizacao_despesas=inicio,
        data_fim_realizacao_despesas=fim,
        recurso=recurso,
    )


def _despesa(despesa_factory, associacao, recurso, data_transacao):
    return despesa_factory.create(
        associacao=associacao,
        recurso=recurso,
        data_transacao=data_transacao,
        data_documento=data_transacao,
    )


def _vincular(bem_produzido_factory, bem_produzido_despesa_factory, associacao, recurso, despesa, status):
    bem = bem_produzido_factory.create(
        associacao=associacao,
        recurso=recurso,
        status=status,
    )
    bem_produzido_despesa_factory.create(bem_produzido=bem, despesa=despesa)
    return bem


@freeze_time('2025-03-10')
class TestBemProduzidoEmModoVisualizacao:

    def test_sem_despesas_nao_e_visualizacao(self, associacao_factory, recurso_factory, bem_produzido_factory):
        from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido

        associacao = associacao_factory.create()
        recurso = recurso_factory.create(nome="PTRF modo", legado=False)
        bem = bem_produzido_factory.create(
            associacao=associacao,
            recurso=recurso,
            status=BemProduzido.STATUS_COMPLETO,
        )

        assert BemProduzidoService.bem_produzido_em_modo_visualizacao(bem) is False

    def test_periodo_aberto_permite_edicao(
        self, associacao_factory, recurso_factory, periodo_factory, despesa_factory,
        bem_produzido_factory, bem_produzido_despesa_factory, prestacao_conta_factory,
    ):
        from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido

        associacao = associacao_factory.create()
        recurso = recurso_factory.create(nome="PTRF aberto", legado=False)
        periodo = _periodo(periodo_factory, recurso, '2025.1', date(2025, 1, 1), date(2025, 4, 30))
        despesa = _despesa(despesa_factory, associacao, recurso, date(2025, 2, 10))
        prestacao_conta_factory.create(periodo=periodo, associacao=associacao, status='NAO_APRESENTADA')
        bem = _vincular(
            bem_produzido_factory, bem_produzido_despesa_factory,
            associacao, recurso, despesa, BemProduzido.STATUS_COMPLETO,
        )

        assert BemProduzidoService.bem_produzido_em_modo_visualizacao(bem) is False

    def test_pc_entregue_no_periodo_da_despesa_mais_recente_e_visualizacao(
        self, associacao_factory, recurso_factory, periodo_factory, despesa_factory,
        bem_produzido_factory, bem_produzido_despesa_factory, prestacao_conta_factory,
    ):
        from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido

        associacao = associacao_factory.create()
        recurso = recurso_factory.create(nome="PTRF fechado", legado=False)
        periodo_antigo = _periodo(periodo_factory, recurso, '2024.2', date(2024, 9, 1), date(2024, 12, 31))
        periodo_recente = _periodo(periodo_factory, recurso, '2025.1', date(2025, 1, 1), date(2025, 2, 28))
        despesa_antiga = _despesa(despesa_factory, associacao, recurso, date(2024, 10, 1))
        despesa_recente = _despesa(despesa_factory, associacao, recurso, date(2025, 1, 20))
        prestacao_conta_factory.create(periodo=periodo_antigo, associacao=associacao, status='NAO_APRESENTADA')
        prestacao_conta_factory.create(periodo=periodo_recente, associacao=associacao, status='APROVADA')

        bem = bem_produzido_factory.create(
            associacao=associacao,
            recurso=recurso,
            status=BemProduzido.STATUS_COMPLETO,
        )
        bem_produzido_despesa_factory.create(bem_produzido=bem, despesa=despesa_antiga)
        bem_produzido_despesa_factory.create(bem_produzido=bem, despesa=despesa_recente)

        assert BemProduzidoService.bem_produzido_em_modo_visualizacao(bem) is True

    def test_rascunho_em_periodo_fechado_permanece_editavel(
        self, associacao_factory, recurso_factory, periodo_factory, despesa_factory,
        bem_produzido_factory, bem_produzido_despesa_factory, prestacao_conta_factory,
    ):
        from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido

        associacao = associacao_factory.create()
        recurso = recurso_factory.create(nome="PTRF rascunho fechado", legado=False)
        periodo = _periodo(periodo_factory, recurso, '2025.1', date(2025, 1, 1), date(2025, 2, 28))
        despesa = _despesa(despesa_factory, associacao, recurso, date(2025, 1, 20))
        prestacao_conta_factory.create(periodo=periodo, associacao=associacao, status='APROVADA')
        bem = _vincular(
            bem_produzido_factory, bem_produzido_despesa_factory,
            associacao, recurso, despesa, BemProduzido.STATUS_INCOMPLETO,
        )

        assert BemProduzidoService.bem_produzido_em_modo_visualizacao(bem) is False

    def test_despesa_mais_recente_em_periodo_aberto_permite_edicao_mesmo_com_periodo_anterior_fechado(
        self, associacao_factory, recurso_factory, periodo_factory, despesa_factory,
        bem_produzido_factory, bem_produzido_despesa_factory, prestacao_conta_factory,
    ):
        from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido

        associacao = associacao_factory.create()
        recurso = recurso_factory.create(nome="PTRF misto", legado=False)
        periodo_antigo = _periodo(periodo_factory, recurso, '2025.1', date(2025, 1, 1), date(2025, 2, 28))
        _periodo(periodo_factory, recurso, '2025.2', date(2025, 3, 1), date(2025, 6, 30))
        despesa_antiga = _despesa(despesa_factory, associacao, recurso, date(2025, 1, 15))
        despesa_recente = _despesa(despesa_factory, associacao, recurso, date(2025, 3, 5))
        prestacao_conta_factory.create(periodo=periodo_antigo, associacao=associacao, status='APROVADA')

        bem = bem_produzido_factory.create(
            associacao=associacao,
            recurso=recurso,
            status=BemProduzido.STATUS_INCOMPLETO,
        )
        bem_produzido_despesa_factory.create(bem_produzido=bem, despesa=despesa_antiga)
        bem_produzido_despesa_factory.create(bem_produzido=bem, despesa=despesa_recente)

        assert BemProduzidoService.bem_produzido_em_modo_visualizacao(bem) is False

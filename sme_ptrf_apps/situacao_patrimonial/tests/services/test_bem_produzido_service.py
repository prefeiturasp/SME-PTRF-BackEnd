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


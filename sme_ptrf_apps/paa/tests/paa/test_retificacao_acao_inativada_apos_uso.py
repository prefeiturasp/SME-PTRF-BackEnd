"""
Testes de integração: Ação PTRF utilizada em uma versão anterior do PAA e
inativada (exibir_paa=False) antes de uma retificação.

Regra de negócio (Ref. história 152458 / paas_acoes_conclusao):
Quando o PAA é concluído (status GERADO), as Ações PTRF disponíveis naquele momento
são "congeladas" em `Paa.acoes_conclusao` (ver `RegistrarAcoesPtrfConclusaoPaaService`).
Se, depois disso, a Ação for inativada (campo `exibir_paa=False` em `core.Acao`), ela deixa
de aparecer nas telas correntes do PAA (ex.: nova elaboração), mas deve continuar sendo
listada durante uma retificação do PAA que já a utilizou, pois já foi usada em uma versão
anterior (`AcoesPaaService.obter_ptrf`, condição `Q(acao__in=acoes_conclusao)`).

Este teste simula o fluxo ponta a ponta:
1. PAA em elaboração com uma Receita Prevista de R$1000,00 para a Ação "PTRF Básico";
2. PAA é concluído (GERADO) e o histórico de ações da conclusão é registrado;
3. A Ação "PTRF Básico" é inativada (exibir_paa=False);
4. O PAA entra em retificação;
5. A Ação e a receita de R$1000,00 devem continuar disponíveis/listadas.
"""
from decimal import Decimal

import pytest

from sme_ptrf_apps.paa.services.acoes_paa_service import (
    AcoesPaaService,
    AcoesReceitasPrevistasPaaService,
)
from sme_ptrf_apps.paa.services.paa_service import PaaService
from sme_ptrf_apps.paa.services.registrar_acoes_conclusao_paa_service import (
    RegistrarAcoesPtrfConclusaoPaaService,
)


@pytest.fixture
def flag_paa_retificacao(flag_factory):
    """Flag 'paa-retificacao' ativa para todos (necessária para o merge com acoes_conclusao)."""
    return flag_factory.create(name='paa-retificacao', everyone=True)


@pytest.fixture
def acao_ptrf_basico(acao_factory):
    """Ação PTRF Básico: recurso legado (padrão da factory) e exibir_paa=True."""
    return acao_factory.create(nome='PTRF Básico', exibir_paa=True)


@pytest.fixture
def acao_associacao_ptrf_basico(acao_associacao_factory, paa, acao_ptrf_basico):
    """Vínculo ativo da Ação 'PTRF Básico' com a Associação do PAA."""
    return acao_associacao_factory.create(associacao=paa.associacao, acao=acao_ptrf_basico)


@pytest.fixture
def receita_1000_ptrf_basico(receita_prevista_paa_factory, paa, acao_associacao_ptrf_basico):
    """Receita prevista de R$1000,00 (custeio) para a Ação 'PTRF Básico'."""
    return receita_prevista_paa_factory.create(
        paa=paa,
        acao_associacao=acao_associacao_ptrf_basico,
        previsao_valor_custeio=Decimal('1000.00'),
        previsao_valor_capital=Decimal('0.00'),
        previsao_valor_livre=Decimal('0.00'),
    )


@pytest.mark.django_db
class TestAcaoInativadaAposUsoContinuaDisponivelNaRetificacao:

    def _concluir_e_registrar_historico(self, paa):
        """
        Simula a conclusão da 1ª versão do PAA: status GERADO + registro das Ações
        disponíveis naquele momento em `acoes_conclusao`.

        Usa `RegistrarAcoesPtrfConclusaoPaaService` diretamente (em vez de
        `PaaService.registra_historico_acoes`) para manter o teste isolado do
        congelamento de saldo, que depende de um `Periodo` legado vigente na data
        atual e não é relevante para a regra sendo testada aqui.
        """
        PaaService.concluir_paa(paa)
        quantidade = RegistrarAcoesPtrfConclusaoPaaService.registrar(paa)
        return quantidade

    def test_acao_utilizada_e_depois_inativada_continua_listada_na_retificacao(
        self, paa, acao_associacao_ptrf_basico, receita_1000_ptrf_basico, flag_paa_retificacao
    ):
        """Ação usada na 1ª versão do PAA e depois inativada continua no obter_ptrf durante retificação."""
        self._concluir_e_registrar_historico(paa)

        # A ação foi registrada como "já utilizada" na conclusão do PAA
        assert acao_associacao_ptrf_basico.acao in paa.acoes_conclusao.all()

        # A Ação "PTRF Básico" é inativada após a geração da 1ª versão do PAA
        acao = acao_associacao_ptrf_basico.acao
        acao.exibir_paa = False
        acao.save()

        # PAA entra em retificação
        paa.set_paa_status_em_retificacao()
        assert paa.status_em_retificacao is True

        resultado = AcoesPaaService(paa).obter_ptrf()

        assert acao_associacao_ptrf_basico in resultado, (
            "A Ação 'PTRF Básico' deveria continuar listada na retificação, "
            "pois já foi utilizada na primeira geração do PAA."
        )

        receitas = paa.receitaprevistapaa_set.filter(acao_associacao=acao_associacao_ptrf_basico)
        assert receitas.count() == 1
        assert receitas.first().previsao_valor_custeio == Decimal('1000.00')

    def test_acao_utilizada_e_inativada_aparece_serializada_com_receita_de_1000_na_retificacao(
        self, paa, acao_associacao_ptrf_basico, receita_1000_ptrf_basico, flag_paa_retificacao
    ):
        """A serialização usada pela tela do PAA também deve manter a Ação e sua receita de R$1000."""
        self._concluir_e_registrar_historico(paa)

        acao = acao_associacao_ptrf_basico.acao
        acao.exibir_paa = False
        acao.save()

        paa.set_paa_status_em_retificacao()

        serializado = AcoesReceitasPrevistasPaaService(paa).serialized_ptrf_com_receitas_previstas()

        acao_serializada = next(
            (item for item in serializado if item['acao']['uuid'] == str(acao.uuid)), None
        )
        assert acao_serializada is not None, "Ação 'PTRF Básico' deveria continuar listada na retificação"

        receitas_previstas = acao_serializada['receitas_previstas_paa']
        assert len(receitas_previstas) == 1
        assert Decimal(receitas_previstas[0]['previsao_valor_custeio']) == Decimal('1000.00')

    def test_sem_flag_paa_retificacao_acao_inativada_nao_e_mais_listada(
        self, paa, acao_associacao_ptrf_basico, receita_1000_ptrf_basico
    ):
        """
        Sem a flag 'paa-retificacao' ativa, o merge com `acoes_conclusao` não é aplicado
        (comportamento legado): uma ação inativada deixa de ser listada mesmo tendo sido
        utilizada antes. Mantido aqui para deixar explícito que a regra depende da flag.
        """
        self._concluir_e_registrar_historico(paa)

        acao = acao_associacao_ptrf_basico.acao
        acao.exibir_paa = False
        acao.save()

        paa.set_paa_status_em_retificacao()

        resultado = AcoesPaaService(paa).obter_ptrf()

        assert acao_associacao_ptrf_basico not in resultado

    def test_acao_nunca_utilizada_e_inativada_nao_aparece_na_retificacao(
        self, paa, acao_factory, acao_associacao_factory, flag_paa_retificacao
    ):
        """
        Contraponto: uma Ação inativada que nunca foi utilizada em uma versão anterior do
        PAA (não está em `acoes_conclusao`) não deve aparecer. Garante que o merge feito em
        `obter_ptrf` não libera indiscriminadamente todas as ações inativas durante a
        retificação, apenas as que já haviam sido usadas.
        """
        acao_nao_utilizada = acao_factory.create(nome='Ação Nunca Usada', exibir_paa=False)
        acao_associacao_nao_utilizada = acao_associacao_factory.create(
            associacao=paa.associacao, acao=acao_nao_utilizada
        )

        paa.set_paa_status_em_retificacao()

        resultado = AcoesPaaService(paa).obter_ptrf()

        assert acao_associacao_nao_utilizada not in resultado

"""
Suite de integração — PlanoOrcamentarioService + fluxo PAA → GERADO → RETIFICAÇÃO

Valida o ciclo completo:
  1. Criação de um PAA com receitas PTRF, PDDE, Recursos Próprios e Outros Recursos
  2. Vinculação de prioridades que consomem o saldo de cada fonte
  3. Informação de introdução, conclusão e objetivos
  4. Transição para status GERADO
  5. Início da retificação (criação da réplica-snapshot)
  6. Modificação de receitas e prioridades
  7. Verificação de que _calcular_secao_ptrf(), _calcular_secao_pdde() e
     _calcular_secao_outros_recursos() retornam dicts com a prop 'historicos'
     indicando corretamente: None (sem alteração), 'adicionado', 'modificado', 'removido'.
"""

import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import patch

from sme_ptrf_apps.paa.services.plano_orcamentario_service import PlanoOrcamentarioService
from sme_ptrf_apps.paa.services.retificacao_paa_service import RetificacaoPaaService
from sme_ptrf_apps.paa.models import AtaPaa, DocumentoPaa
from sme_ptrf_apps.paa.enums import PaaStatusEnum, RecursoOpcoesEnum
from sme_ptrf_apps.core.fixtures.factories import AcaoAssociacaoFactory

pytestmark = pytest.mark.django_db


# helpers

def _saldo_zero():
    """Retorna saldo zerado para mock de AcaoAssociacao.saldo_atual()."""
    return {'saldo_atual_custeio': 0.0, 'saldo_atual_capital': 0.0, 'saldo_atual_livre': 0.0}


def _service(paa):
    return PlanoOrcamentarioService(paa)


# fixtures locais

@pytest.fixture
def periodo_paa_integ(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='Integ 2025',
        data_inicial=date(2025, 1, 1),
        data_final=date(2025, 12, 31),
    )


@pytest.fixture
def paa_integ(paa_factory, periodo_paa_integ, associacao):
    return paa_factory.create(
        periodo_paa=periodo_paa_integ,
        associacao=associacao,
        texto_introducao='Introdução original do PAA.',
        texto_conclusao='Conclusão original do PAA.',
    )


@pytest.fixture
def acao_ptrf(acao_factory):
    """Ação PTRF que aceita custeio e capital (exibir_paa=True por padrão)."""
    return acao_factory(
        nome='Ação PTRF Integração',
        aceita_custeio=True,
        aceita_capital=True,
        aceita_livre=False,
    )


@pytest.fixture
def acao_assoc_ptrf(paa_integ, acao_ptrf):
    return AcaoAssociacaoFactory.create(
        associacao=paa_integ.associacao,
        acao=acao_ptrf,
        status='ATIVA',
    )


@pytest.fixture
def receita_ptrf(paa_integ, acao_assoc_ptrf, receita_prevista_paa_factory):
    """Receita PTRF com saldo suficiente para prioridades."""
    return receita_prevista_paa_factory.create(
        paa=paa_integ,
        acao_associacao=acao_assoc_ptrf,
        previsao_valor_custeio='500.00',
        previsao_valor_capital='300.00',
        previsao_valor_livre='0.00',
    )


@pytest.fixture
def prioridade_ptrf(paa_integ, acao_assoc_ptrf, receita_ptrf, prioridade_paa_factory):
    """Prioridade PTRF que consome o saldo de custeio integralmente."""
    return prioridade_paa_factory.create(
        paa=paa_integ,
        recurso=RecursoOpcoesEnum.PTRF.name,
        acao_associacao=acao_assoc_ptrf,
        acao_pdde=None,
        programa_pdde=None,
        tipo_aplicacao='CUSTEIO',
        valor_total='500.00',
    )


@pytest.fixture
def acao_pdde_integ(acao_pdde_factory):
    return acao_pdde_factory.create(
        aceita_custeio=True,
        aceita_capital=True,
        aceita_livre_aplicacao=False,
    )


@pytest.fixture
def receita_pdde_integ(paa_integ, acao_pdde_integ, receita_prevista_pdde_factory):
    """Receita PDDE com saldo suficiente para prioridades."""
    return receita_prevista_pdde_factory.create(
        paa=paa_integ,
        acao_pdde=acao_pdde_integ,
        previsao_valor_custeio='800.00',
        previsao_valor_capital='400.00',
        previsao_valor_livre='0.00',
        saldo_custeio='0.00',
        saldo_capital='0.00',
        saldo_livre='0.00',
    )


@pytest.fixture
def prioridade_pdde(paa_integ, acao_pdde_integ, receita_pdde_integ, prioridade_paa_factory):
    """Prioridade PDDE que consome o saldo de custeio integralmente."""
    return prioridade_paa_factory.create(
        paa=paa_integ,
        recurso=RecursoOpcoesEnum.PDDE.name,
        acao_pdde=acao_pdde_integ,
        programa_pdde=acao_pdde_integ.programa,
        acao_associacao=None,
        tipo_aplicacao='CUSTEIO',
        valor_total='800.00',
    )


@pytest.fixture
def recurso_proprio_integ(paa_integ, recurso_proprio_paa_factory, fonte_recurso_paa_factory):
    fonte = fonte_recurso_paa_factory.create()
    return recurso_proprio_paa_factory.create(
        paa=paa_integ,
        associacao=paa_integ.associacao,
        fonte_recurso=fonte,
        valor='1000.00',
        descricao='Recurso próprio de integração',
    )


@pytest.fixture
def outro_recurso_integ(outro_recurso_factory):
    return outro_recurso_factory.create(
        nome='Outro Recurso Integração',
        aceita_custeio=True,
        aceita_capital=False,
        aceita_livre_aplicacao=False,
    )


@pytest.fixture
def outro_recurso_periodo_integ(periodo_paa_integ, outro_recurso_integ, outro_recurso_periodo_factory):
    # sem unidades → disponível para todas as associações
    return outro_recurso_periodo_factory.create(
        periodo_paa=periodo_paa_integ,
        outro_recurso=outro_recurso_integ,
        ativo=True,
    )


@pytest.fixture
def receita_outro_recurso(paa_integ, outro_recurso_periodo_integ,
                          receita_prevista_outro_recurso_periodo_factory):
    return receita_prevista_outro_recurso_periodo_factory.create(
        paa=paa_integ,
        outro_recurso_periodo=outro_recurso_periodo_integ,
        previsao_valor_custeio='600.00',
        previsao_valor_capital='0.00',
        previsao_valor_livre='0.00',
        saldo_custeio='0.00',
        saldo_capital='0.00',
        saldo_livre='0.00',
    )


@pytest.fixture
def prioridade_outro_recurso(paa_integ, outro_recurso_integ, receita_outro_recurso,
                             prioridade_paa_factory):
    """Prioridade Outro Recurso que consome o saldo de custeio integralmente."""
    return prioridade_paa_factory.create(
        paa=paa_integ,
        recurso=RecursoOpcoesEnum.OUTRO_RECURSO.name,
        outro_recurso=outro_recurso_integ,
        acao_associacao=None,
        acao_pdde=None,
        programa_pdde=None,
        tipo_aplicacao='CUSTEIO',
        valor_total='600.00',
    )


@pytest.fixture
def objetivo_integ(paa_integ, objetivo_paa_factory):
    objetivo = objetivo_paa_factory.create(paa=paa_integ)
    paa_integ.objetivos.add(objetivo)
    return objetivo


@pytest.fixture
def paa_completo_gerado(
    paa_integ,
    receita_ptrf, prioridade_ptrf,
    receita_pdde_integ, prioridade_pdde,
    recurso_proprio_integ,
    receita_outro_recurso, prioridade_outro_recurso,
    objetivo_integ,
    ata_paa_factory, documento_paa_factory,
):
    """
    PAA com todos os dados (PTRF, PDDE, RecursoPróprio, OutrosRecursos,
    prioridades, objetivos) em estado GERADO.
    """
    ata_paa_factory.create(
        paa=paa_integ,
        status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
    )
    documento_paa_factory.create(
        paa=paa_integ,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
    )
    paa_integ.status = PaaStatusEnum.GERADO.name
    paa_integ.save()
    return paa_integ


@pytest.fixture
def paa_em_retificacao(paa_completo_gerado, replica_paa_factory):
    """
    PAA em EM_RETIFICACAO com réplica (snapshot do estado GERADO).
    O snapshot é gerado via RetificacaoPaaService para garantir fidelidade
    ao que a aplicação produziria.
    """
    snapshot = RetificacaoPaaService(paa_completo_gerado, None).gerar_snapshot()
    replica_paa_factory.create(
        paa=paa_completo_gerado,
        historico=snapshot,
    )
    paa_completo_gerado.status = PaaStatusEnum.EM_RETIFICACAO.name
    paa_completo_gerado.save()
    return paa_completo_gerado


# Testes: PAA sem retificação (EM_ELABORACAO)

class TestPlanoOrcamentarioPaaEmElaboracao:
    """
    PAA sem réplica: a prop 'historicos' deve ser None em todas as linhas,
    pois não há snapshot para comparar.
    """

    def test_secao_ptrf_historicos_none_sem_retificacao(
        self, paa_integ, acao_assoc_ptrf, receita_ptrf
    ):
        with patch(
            'sme_ptrf_apps.core.models.acao_associacao.AcaoAssociacao.saldo_atual',
            return_value=_saldo_zero(),
        ):
            svc = _service(paa_integ)
            receitas = svc._obter_receitas_ptrf()
            prioridades = svc._obter_prioridades_agrupadas()
            secao = svc._calcular_secao_ptrf(receitas, prioridades['PTRF'])

        assert secao is not None, "Seção PTRF deve ser criada quando há receitas"
        linhas_acao = [linha for linha in secao['linhas'] if not linha.get('isTotal')]
        assert linhas_acao, "Deve haver ao menos uma linha de ação"
        assert all(linha['historicos'] is None for linha in linhas_acao), (
            "historicos deve ser None quando não há retificação em curso"
        )

    def test_secao_pdde_historicos_none_sem_retificacao(
        self, paa_integ, receita_pdde_integ, prioridade_pdde
    ):
        svc = _service(paa_integ)
        acoes_pdde = svc._obter_acoes_pdde_totais()
        prioridades = svc._obter_prioridades_agrupadas()
        secao = svc._calcular_secao_pdde(acoes_pdde, prioridades['PDDE'])

        assert secao is not None, "Seção PDDE deve ser criada quando há receitas"
        linhas_acao = [linha for linha in secao['linhas'] if not linha.get('isTotal')]
        assert linhas_acao, "Deve haver ao menos uma linha de ação"
        assert all(linha['historicos'] is None for linha in linhas_acao), (
            "historicos deve ser None quando não há retificação em curso"
        )

    def test_secao_outros_recursos_historicos_none_sem_retificacao(
        self, paa_integ, recurso_proprio_integ, receita_outro_recurso
    ):
        svc = _service(paa_integ)
        receitas = svc._obter_receitas_outros_recursos()
        prioridades = svc._obter_prioridades_outros_recursos()
        secao = svc._calcular_secao_outros_recursos(receitas, prioridades)

        assert secao is not None, "Seção Outros Recursos deve ser criada"
        linhas_recurso = [linha for linha in secao['linhas'] if not linha.get('isTotal')]
        assert linhas_recurso, "Deve haver ao menos uma linha de recurso"
        assert all(linha['historicos'] is None for linha in linhas_recurso), (
            "historicos deve ser None quando não há retificação em curso"
        )

    def test_construir_plano_completo_sem_retificacao_inclui_tres_secoes(
        self, paa_integ, acao_assoc_ptrf, receita_ptrf, prioridade_ptrf,
        receita_pdde_integ, prioridade_pdde,
        recurso_proprio_integ, receita_outro_recurso, prioridade_outro_recurso,
    ):
        with patch(
            'sme_ptrf_apps.core.models.acao_associacao.AcaoAssociacao.saldo_atual',
            return_value=_saldo_zero(),
        ):
            svc = _service(paa_integ)
            plano = svc.construir_plano_orcamentario()

        chaves = [s['key'] for s in plano['secoes']]
        assert 'ptrf' in chaves
        assert 'pdde' in chaves
        assert 'outros_recursos' in chaves


# Testes: PAA em retificação — historicos reflete alterações
class TestPlanoOrcamentarioPaaRetificacaoHistoricos:
    """
    Após criar réplica-snapshot e modificar dados do PAA,
    a prop 'historicos' nas linhas de cada seção deve refletir a ação:
      - None: item não foi alterado em relação ao snapshot
      - 'adicionado': item inexistia no snapshot e foi inserido
      - 'modificado': item existia no snapshot mas teve valores alterados
      - 'removido': item existia no snapshot mas foi removido
    """

    # Seção PTRF
    def test_secao_ptrf_historicos_none_para_receita_inalterada(
        self, paa_em_retificacao, acao_assoc_ptrf, receita_ptrf
    ):
        """Receita PTRF não modificada após o snapshot → historicos = None."""
        with patch(
            'sme_ptrf_apps.core.models.acao_associacao.AcaoAssociacao.saldo_atual',
            return_value=_saldo_zero(),
        ):
            svc = _service(paa_em_retificacao)
            receitas = svc._obter_receitas_ptrf()
            prioridades = svc._obter_prioridades_agrupadas()
            secao = svc._calcular_secao_ptrf(receitas, prioridades['PTRF'])

        assert secao is not None
        # a key na linha é str(acao.uuid), não str(acao_associacao.uuid)
        linha = next(
            (linha for linha in secao['linhas'] if linha['key'] == str(acao_assoc_ptrf.acao.uuid)),
            None,
        )
        assert linha is not None
        assert linha['historicos'] is None

    def test_secao_ptrf_historicos_modificado_apos_alterar_previsao_custeio(
        self, paa_em_retificacao, acao_assoc_ptrf, receita_ptrf
    ):
        """Alterar previsão de custeio de uma receita PTRF → historicos = 'modificado'."""
        receita_ptrf.previsao_valor_custeio = Decimal('999.00')
        receita_ptrf.save()

        with patch(
            'sme_ptrf_apps.core.models.acao_associacao.AcaoAssociacao.saldo_atual',
            return_value=_saldo_zero(),
        ):
            svc = _service(paa_em_retificacao)
            receitas = svc._obter_receitas_ptrf()
            prioridades = svc._obter_prioridades_agrupadas()
            secao = svc._calcular_secao_ptrf(receitas, prioridades['PTRF'])

        assert secao is not None
        linha = next(
            (linha for linha in secao['linhas'] if linha['key'] == str(acao_assoc_ptrf.acao.uuid)),
            None,
        )
        assert linha is not None
        assert linha['historicos'] == 'modificado'

    def test_secao_ptrf_historicos_adicionado_ao_inserir_nova_acao(
        self, paa_em_retificacao, acao_factory, receita_prevista_paa_factory
    ):
        """
        Adicionar nova AcaoAssociacao + ReceitaPrevistaPaa após o snapshot
        → historicos = 'adicionado' para a nova ação.
        """
        nova_acao = acao_factory(
            nome='Nova Ação PTRF Pós-Snapshot',
            aceita_custeio=True,
            aceita_capital=False,
            aceita_livre=False,
        )
        nova_acao_assoc = AcaoAssociacaoFactory.create(
            associacao=paa_em_retificacao.associacao,
            acao=nova_acao,
            status='ATIVA',
        )
        receita_prevista_paa_factory.create(
            paa=paa_em_retificacao,
            acao_associacao=nova_acao_assoc,
            previsao_valor_custeio='250.00',
            previsao_valor_capital='0.00',
            previsao_valor_livre='0.00',
        )

        with patch(
            'sme_ptrf_apps.core.models.acao_associacao.AcaoAssociacao.saldo_atual',
            return_value=_saldo_zero(),
        ):
            svc = _service(paa_em_retificacao)
            receitas = svc._obter_receitas_ptrf()
            prioridades = svc._obter_prioridades_agrupadas()
            secao = svc._calcular_secao_ptrf(receitas, prioridades['PTRF'])

        assert secao is not None
        linha_nova = next(
            (linha for linha in secao['linhas'] if linha['key'] == str(nova_acao.uuid)),
            None,
        )
        assert linha_nova is not None, "Nova ação deve aparecer na seção PTRF"
        assert linha_nova['historicos'] == 'adicionado'

    def test_secao_ptrf_historicos_removido_ao_excluir_receita(
        self, paa_em_retificacao, acao_assoc_ptrf, receita_ptrf
    ):
        """
        Remover a ReceitaPrevistaPaa após o snapshot mantém a linha fora da seção,
        mas o snapshot a registra como 'removido' nas alterações.
        O snapshot marcará a ação como removida; a seção não terá linha para ela
        (pois não há receita para exibir), mas a propriedade alteracao estará disponível.
        """
        uuid_acao_assoc = str(acao_assoc_ptrf.uuid)
        receita_ptrf.delete()

        svc = _service(paa_em_retificacao)
        alteracoes = svc._obter_alteracoes()

        # A ação deve aparecer como 'removida' nas alterações de receitas_ptrf
        assert 'receitas_ptrf' in alteracoes
        assert uuid_acao_assoc in alteracoes['receitas_ptrf']
        assert alteracoes['receitas_ptrf'][uuid_acao_assoc]['acao'] == 'removido'

    # Seção PDDE
    def test_secao_pdde_historicos_none_para_acao_inalterada(
        self, paa_em_retificacao, acao_pdde_integ, receita_pdde_integ
    ):
        """Ação PDDE não modificada após o snapshot → historicos = None."""
        svc = _service(paa_em_retificacao)
        acoes_pdde = svc._obter_acoes_pdde_totais()
        prioridades = svc._obter_prioridades_agrupadas()
        secao = svc._calcular_secao_pdde(acoes_pdde, prioridades['PDDE'])

        assert secao is not None
        linha = next(
            (linha for linha in secao['linhas'] if linha['key'] == str(acao_pdde_integ.uuid)),
            None,
        )
        assert linha is not None
        assert linha['historicos'] is None

    def test_secao_pdde_historicos_modificado_apos_alterar_receita(
        self, paa_em_retificacao, acao_pdde_integ, receita_pdde_integ
    ):
        """Alterar previsão de custeio de uma receita PDDE → historicos = 'modificado'."""
        receita_pdde_integ.previsao_valor_custeio = Decimal('1500.00')
        receita_pdde_integ.save()

        svc = _service(paa_em_retificacao)
        acoes_pdde = svc._obter_acoes_pdde_totais()
        prioridades = svc._obter_prioridades_agrupadas()
        secao = svc._calcular_secao_pdde(acoes_pdde, prioridades['PDDE'])

        assert secao is not None
        linha = next(
            (linha for linha in secao['linhas'] if linha['key'] == str(acao_pdde_integ.uuid)),
            None,
        )
        assert linha is not None
        assert linha['historicos'] == 'modificado'

    def test_secao_pdde_historicos_adicionado_ao_inserir_nova_acao(
        self, paa_em_retificacao, acao_pdde_factory, receita_prevista_pdde_factory
    ):
        """
        Inserir nova AcaoPdde + ReceitaPrevistaPdde após o snapshot
        → historicos = 'adicionado' para a nova ação.
        """
        nova_acao_pdde = acao_pdde_factory.create(
            aceita_custeio=True,
            aceita_capital=False,
            aceita_livre_aplicacao=False,
        )
        receita_prevista_pdde_factory.create(
            paa=paa_em_retificacao,
            acao_pdde=nova_acao_pdde,
            previsao_valor_custeio='400.00',
            previsao_valor_capital='0.00',
            previsao_valor_livre='0.00',
            saldo_custeio='0.00',
            saldo_capital='0.00',
            saldo_livre='0.00',
        )

        svc = _service(paa_em_retificacao)
        acoes_pdde = svc._obter_acoes_pdde_totais()
        prioridades = svc._obter_prioridades_agrupadas()
        secao = svc._calcular_secao_pdde(acoes_pdde, prioridades['PDDE'])

        assert secao is not None
        linha_nova = next(
            (linha for linha in secao['linhas'] if linha['key'] == str(nova_acao_pdde.uuid)),
            None,
        )
        assert linha_nova is not None, "Nova ação PDDE deve aparecer na seção"
        assert linha_nova['historicos'] == 'adicionado'

    def test_secao_pdde_historicos_removido_ao_excluir_receita(
        self, paa_em_retificacao, acao_pdde_integ, receita_pdde_integ
    ):
        """
        Remover ReceitaPrevistaPdde após o snapshot → ação aparece como 'removida'
        nas alterações (verificação via _obter_alteracoes).
        """
        uuid_acao_pdde = str(acao_pdde_integ.uuid)
        receita_pdde_integ.delete()

        svc = _service(paa_em_retificacao)
        alteracoes = svc._obter_alteracoes()

        assert 'receitas_pdde' in alteracoes
        assert uuid_acao_pdde in alteracoes['receitas_pdde']
        assert alteracoes['receitas_pdde'][uuid_acao_pdde]['acao'] == 'removido'

    # Seção Outros Recursos
    def test_secao_outros_recursos_historicos_none_para_recurso_inalterado(
        self, paa_em_retificacao, outro_recurso_integ, receita_outro_recurso
    ):
        """Outro Recurso não modificado após snapshot → historicos = None."""
        svc = _service(paa_em_retificacao)
        receitas = svc._obter_receitas_outros_recursos()
        prioridades = svc._obter_prioridades_outros_recursos()
        secao = svc._calcular_secao_outros_recursos(receitas, prioridades)

        assert secao is not None
        # key na linha é str(outro_recurso.uuid), não str(outro_recurso_periodo.uuid)
        linha = next(
            (linha for linha in secao['linhas'] if linha['key'] == str(outro_recurso_integ.uuid)),
            None,
        )
        assert linha is not None
        assert linha['historicos'] is None

    def test_secao_outros_recursos_historicos_modificado_apos_alterar_receita(
        self, paa_em_retificacao, outro_recurso_integ, receita_outro_recurso
    ):
        """Alterar previsão de custeio de receita Outro Recurso → historicos = 'modificado'."""
        receita_outro_recurso.previsao_valor_custeio = Decimal('900.00')
        receita_outro_recurso.save()

        svc = _service(paa_em_retificacao)
        receitas = svc._obter_receitas_outros_recursos()
        prioridades = svc._obter_prioridades_outros_recursos()
        secao = svc._calcular_secao_outros_recursos(receitas, prioridades)

        assert secao is not None
        linha = next(
            (linha for linha in secao['linhas'] if linha['key'] == str(outro_recurso_integ.uuid)),
            None,
        )
        assert linha is not None
        assert linha['historicos'] == 'modificado'

    def test_secao_outros_recursos_historicos_adicionado_para_novo_outro_recurso(
        self, paa_em_retificacao, periodo_paa_integ,
        outro_recurso_factory, outro_recurso_periodo_factory,
        receita_prevista_outro_recurso_periodo_factory,
    ):
        """
        Inserir novo OutroRecurso + ReceitaPrevistaOutroRecursoPeriodo após snapshot
        → historicos = 'adicionado' para o novo recurso.
        """
        novo_outro_recurso = outro_recurso_factory.create(
            nome='Outro Recurso Novo Pós-Snapshot',
            aceita_custeio=True,
            aceita_capital=False,
            aceita_livre_aplicacao=False,
        )
        novo_periodo_recurso = outro_recurso_periodo_factory.create(
            periodo_paa=periodo_paa_integ,
            outro_recurso=novo_outro_recurso,
            ativo=True,
        )
        receita_prevista_outro_recurso_periodo_factory.create(
            paa=paa_em_retificacao,
            outro_recurso_periodo=novo_periodo_recurso,
            previsao_valor_custeio='300.00',
            previsao_valor_capital='0.00',
            previsao_valor_livre='0.00',
            saldo_custeio='0.00',
            saldo_capital='0.00',
            saldo_livre='0.00',
        )

        svc = _service(paa_em_retificacao)
        receitas = svc._obter_receitas_outros_recursos()
        prioridades = svc._obter_prioridades_outros_recursos()
        secao = svc._calcular_secao_outros_recursos(receitas, prioridades)

        assert secao is not None
        linha_nova = next(
            (linha for linha in secao['linhas'] if linha['key'] == str(novo_outro_recurso.uuid)),
            None,
        )
        assert linha_nova is not None, "Novo Outro Recurso deve aparecer na seção"
        assert linha_nova['historicos'] == 'adicionado'

    def test_secao_outros_recursos_recurso_proprio_historicos_adicionado(
        self, paa_em_retificacao, recurso_proprio_integ,
        recurso_proprio_paa_factory, fonte_recurso_paa_factory,
    ):
        """
        Adicionar novo RecursoProprioPaa após snapshot
        → historicos agregado = 'adicionado' na linha RECURSO_PROPRIO.
        """
        fonte = fonte_recurso_paa_factory.create()
        recurso_proprio_paa_factory.create(
            paa=paa_em_retificacao,
            associacao=paa_em_retificacao.associacao,
            fonte_recurso=fonte,
            valor='500.00',
            descricao='Novo recurso próprio pós-snapshot',
        )

        svc = _service(paa_em_retificacao)
        receitas = svc._obter_receitas_outros_recursos()
        prioridades = svc._obter_prioridades_outros_recursos()
        secao = svc._calcular_secao_outros_recursos(receitas, prioridades)

        assert secao is not None
        linha_rp = next(
            (linha for linha in secao['linhas'] if linha['key'] == 'RECURSO_PROPRIO'),
            None,
        )
        assert linha_rp is not None
        assert linha_rp['historicos'] == 'adicionado'

    def test_secao_outros_recursos_recurso_proprio_historicos_modificado(
        self, paa_em_retificacao, recurso_proprio_integ
    ):
        """
        Alterar o valor de um RecursoProprioPaa existente após snapshot
        → historicos agregado = 'modificado' na linha RECURSO_PROPRIO.
        """
        recurso_proprio_integ.valor = Decimal('9999.00')
        recurso_proprio_integ.save()

        svc = _service(paa_em_retificacao)
        receitas = svc._obter_receitas_outros_recursos()
        prioridades = svc._obter_prioridades_outros_recursos()
        secao = svc._calcular_secao_outros_recursos(receitas, prioridades)

        assert secao is not None
        linha_rp = next(
            (linha for linha in secao['linhas'] if linha['key'] == 'RECURSO_PROPRIO'),
            None,
        )
        assert linha_rp is not None
        assert linha_rp['historicos'] == 'modificado'

    #  Plano completo

    def test_construir_plano_completo_em_retificacao_inclui_tres_secoes(
        self, paa_em_retificacao, receita_ptrf, receita_pdde_integ,
        recurso_proprio_integ, receita_outro_recurso,
    ):
        """
        Valida que construir_plano_orcamentario() retorna as três seções
        (ptrf, pdde, outros_recursos) no PAA em retificação.
        """
        with patch(
            'sme_ptrf_apps.core.models.acao_associacao.AcaoAssociacao.saldo_atual',
            return_value=_saldo_zero(),
        ):
            svc = _service(paa_em_retificacao)
            plano = svc.construir_plano_orcamentario()

        chaves = [s['key'] for s in plano['secoes']]
        assert 'ptrf' in chaves
        assert 'pdde' in chaves
        assert 'outros_recursos' in chaves

    def test_construir_plano_historicos_aparecem_em_secoes_com_alteracao(
        self, paa_em_retificacao, receita_ptrf, acao_assoc_ptrf,
        receita_pdde_integ, acao_pdde_integ,
        recurso_proprio_integ, receita_outro_recurso, outro_recurso_integ,
    ):
        """
        Após modificar receitas em todas as seções, confirma que 'historicos'
        aparece em cada seção do plano orçamentário completo.
        """
        # Modifica receita PTRF
        receita_ptrf.previsao_valor_custeio = Decimal('111.00')
        receita_ptrf.save()

        # Modifica receita PDDE
        receita_pdde_integ.previsao_valor_custeio = Decimal('222.00')
        receita_pdde_integ.save()

        # Modifica receita Outro Recurso
        receita_outro_recurso.previsao_valor_custeio = Decimal('333.00')
        receita_outro_recurso.save()

        with patch(
            'sme_ptrf_apps.core.models.acao_associacao.AcaoAssociacao.saldo_atual',
            return_value=_saldo_zero(),
        ):
            svc = _service(paa_em_retificacao)
            plano = svc.construir_plano_orcamentario()

        secoes = {s['key']: s for s in plano['secoes']}

        # Seção PTRF: linha da ação modificada deve ter historicos = 'modificado'
        secao_ptrf = secoes['ptrf']
        linha_ptrf = next(
            (linha for linha in secao_ptrf['linhas'] if linha['key'] == str(acao_assoc_ptrf.acao.uuid)),
            None,
        )
        assert linha_ptrf is not None
        assert linha_ptrf['historicos'] == 'modificado'

        # Seção PDDE: linha da ação modificada deve ter historicos = 'modificado'
        secao_pdde = secoes['pdde']
        linha_pdde = next(
            (linha for linha in secao_pdde['linhas'] if linha['key'] == str(acao_pdde_integ.uuid)),
            None,
        )
        assert linha_pdde is not None
        assert linha_pdde['historicos'] == 'modificado'

        # Seção Outros Recursos: linha do outro recurso modificado deve ter historicos = 'modificado'
        secao_outros = secoes['outros_recursos']
        linha_outro = next(
            (linha for linha in secao_outros['linhas'] if linha['key'] == str(outro_recurso_integ.uuid)),
            None,
        )
        assert linha_outro is not None
        assert linha_outro['historicos'] == 'modificado'

    def test_cache_alteracoes_reutilizado_entre_chamadas(
        self, paa_em_retificacao, receita_ptrf
    ):
        """
        _obter_alteracoes() deve cachear o resultado na instância do service
        para evitar consultas desnecessárias ao banco em chamadas subsequentes.
        """
        svc = _service(paa_em_retificacao)

        resultado1 = svc._obter_alteracoes()
        resultado2 = svc._obter_alteracoes()

        assert resultado1 is resultado2, (
            "O resultado de _obter_alteracoes() deve ser o mesmo objeto (cache)"
        )

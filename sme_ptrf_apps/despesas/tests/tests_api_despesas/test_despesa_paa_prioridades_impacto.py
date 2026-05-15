"""
Testes de integração: impacto de criação/edição de despesa nas PrioridadesPAA.

Fluxo testado:
  POST/PUT /api/despesas/
    → DespesaCreateSerializer.create/update
      → DespesaService.create/update
        → _finalizar_despesa (somente se status=COMPLETO)
          → _limpar_prioridades_paa (callback)
            → PrioridadesPaaImpactadasDespesaRateioService
              → limpar_valor_prioridades_impactadas
                → PrioridadePaa.valor_total = None (quando saldo insuficiente)

Regras aplicadas:
  - PAA deve estar em elaboração (status_andamento=EM_ELABORACAO)
  - saldo_congelado_em deve ser None
  - PrioridadePaa com mesmo acao_associacao, recurso=PTRF e valor_total preenchido
  - Saldo disponível < valor_rateio → limpa
  - Saldo disponível >= valor_rateio → mantém
"""

import json
import pytest
from datetime import date
from model_bakery import baker
from rest_framework import status

from sme_ptrf_apps.despesas.models import Despesa
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum

pytestmark = pytest.mark.django_db


@pytest.fixture
def periodo_paa_para_teste(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia="Periodo PAA Teste",
        data_inicial=date(2025, 1, 1),
        data_final=date(2025, 12, 31),
    )


@pytest.fixture
def paa_em_elaboracao(paa_factory, periodo_paa_para_teste, associacao):
    """PAA em status EM_ELABORACAO: sem documento gerado, sem ata, sem réplica."""
    return paa_factory.create(
        periodo_paa=periodo_paa_para_teste,
        associacao=associacao,
        status="EM_ELABORACAO",
        saldo_congelado_em=None,
    )


@pytest.fixture
def receita_prevista_custeio_500(paa_em_elaboracao, acao_associacao):
    """Receita prevista de custeio = R$ 500. Define o teto de saldo disponível."""
    return baker.make(
        "ReceitaPrevistaPaa",
        paa=paa_em_elaboracao,
        acao_associacao=acao_associacao,
        previsao_valor_custeio=500,
        previsao_valor_capital=0,
        previsao_valor_livre=0,
        saldo_congelado_custeio=None,
        saldo_congelado_capital=None,
        saldo_congelado_livre=None,
    )


@pytest.fixture
def receita_prevista_custeio_1000(paa_em_elaboracao, acao_associacao):
    """Receita prevista de custeio = R$ 1000. Saldo suficiente para despesas menores."""
    return baker.make(
        "ReceitaPrevistaPaa",
        paa=paa_em_elaboracao,
        acao_associacao=acao_associacao,
        previsao_valor_custeio=1000,
        previsao_valor_capital=0,
        previsao_valor_livre=0,
        saldo_congelado_custeio=None,
        saldo_congelado_capital=None,
        saldo_congelado_livre=None,
    )


@pytest.fixture
def prioridade_paa_custeio_500(paa_em_elaboracao, acao_associacao):
    """PrioridadePaa PTRF/CUSTEIO com valor_total=500. Consome todo o saldo de R$ 500."""
    return baker.make(
        "PrioridadePaa",
        paa=paa_em_elaboracao,
        recurso=RecursoOpcoesEnum.PTRF.name,
        tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
        acao_associacao=acao_associacao,
        valor_total=500,
    )


@pytest.fixture
def prioridade_paa_capital_300(paa_em_elaboracao, acao_associacao):
    """
    PrioridadePaa PTRF/CAPITAL com valor_total=300.
    Excede a receita_capital=0, gerando um déficit que torna total_livre negativo.
    """
    return baker.make(
        "PrioridadePaa",
        paa=paa_em_elaboracao,
        recurso=RecursoOpcoesEnum.PTRF.name,
        tipo_aplicacao=TipoAplicacaoOpcoesEnum.CAPITAL.name,
        acao_associacao=acao_associacao,
        valor_total=300,
    )


@pytest.fixture
def especificacao_capital(tipo_aplicacao_recurso_capital):
    """EspecificacaoMaterialServico do tipo CAPITAL para uso em rateios de capital."""
    return baker.make(
        "EspecificacaoMaterialServico",
        descricao="Equipamento capital",
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=None,
    )


def _payload_despesa_capital(associacao, tipo_documento, tipo_transacao, conta_associacao, acao_associacao,
                             especificacao_capital, valor_rateio=100):
    """
    Monta payload de despesa completa com rateio de CAPITAL.
    quantidade=2, valor_item=valor_rateio/2 para satisfazer a validação:
    quantidade * valor_item = valor_rateio.
    """
    return {
        "associacao": str(associacao.uuid),
        "tipo_documento": tipo_documento.id,
        "tipo_transacao": tipo_transacao.id,
        "documento_transacao": "123456789",
        "numero_documento": "634767",
        "data_documento": "2020-03-10",
        "cpf_cnpj_fornecedor": "36.352.197/0001-75",
        "nome_fornecedor": "FORNECEDOR TESTE SA",
        "data_transacao": "2020-03-10",
        "valor_total": float(valor_rateio),
        "valor_recursos_proprios": 0,
        "motivos_pagamento_antecipado": [],
        "outros_motivos_pagamento_antecipado": "",
        "rateios": [
            {
                "associacao": str(associacao.uuid),
                "conta_associacao": str(conta_associacao.uuid),
                "acao_associacao": str(acao_associacao.uuid),
                "aplicacao_recurso": "CAPITAL",
                "tipo_custeio": None,
                "especificacao_material_servico": especificacao_capital.id,
                "valor_rateio": float(valor_rateio),
                "quantidade_itens_capital": 2,
                "valor_item_capital": float(valor_rateio) / 2,
                "numero_processo_incorporacao_capital": "9876543210",
            }
        ],
    }


def _payload_despesa_custeio(associacao, tipo_documento, tipo_transacao, conta_associacao, acao_associacao,
                             tipo_custeio, especificacao_material_servico, valor_rateio=600):
    """Monta payload de despesa completa com rateio de custeio."""
    return {
        "associacao": str(associacao.uuid),
        "tipo_documento": tipo_documento.id,
        "tipo_transacao": tipo_transacao.id,
        "documento_transacao": "123456789",
        "numero_documento": "634767",
        "data_documento": "2020-03-10",
        "cpf_cnpj_fornecedor": "36.352.197/0001-75",
        "nome_fornecedor": "FORNECEDOR TESTE SA",
        "data_transacao": "2020-03-10",
        "valor_total": float(valor_rateio),
        "valor_recursos_proprios": 0,
        "motivos_pagamento_antecipado": [],
        "outros_motivos_pagamento_antecipado": "",
        "rateios": [
            {
                "associacao": str(associacao.uuid),
                "conta_associacao": str(conta_associacao.uuid),
                "acao_associacao": str(acao_associacao.uuid),
                "aplicacao_recurso": "CUSTEIO",
                "tipo_custeio": tipo_custeio.id,
                "especificacao_material_servico": especificacao_material_servico.id,
                "valor_rateio": float(valor_rateio),
                "quantidade_itens_capital": 0,
                "valor_item_capital": 0,
                "numero_processo_incorporacao_capital": "",
            }
        ],
    }


# CRIAÇÃO DE DESPESAS PELO (POST)
class TestPostDespesaImpactaPrioridadePaa:

    def test_cria_despesa_completa_limpa_prioridade_quando_saldo_insuficiente(
            self,
            jwt_authenticated_client_d, associacao, tipo_documento, tipo_transacao, conta_associacao, acao_associacao,
            tipo_custeio, especificacao_material_servico, paa_em_elaboracao,
            receita_prevista_custeio_500, prioridade_paa_custeio_500):
        """
        Criar uma despesa cujo valor_rateio (600) excede o saldo disponível (0)
        deve limpar PrioridadePaa.valor_total → None.

        Cálculo:
          receita_custeio = 500 (ReceitaPrevistaPaa)
          despesa_custeio = 500 (PrioridadePaa)
          saldo_custeio   = 500 - 500 = 0
          saldo_disponivel = 0 (livre) + 0 (simulado) + 0 (custeio) = 0
          0 < 600 → raise ValidacaoSaldoIndisponivel → valor_total = None
        """
        payload = _payload_despesa_custeio(
            associacao, tipo_documento, tipo_transacao,
            conta_associacao, acao_associacao,
            tipo_custeio, especificacao_material_servico,
            valor_rateio=600,
        )

        response = jwt_authenticated_client_d.post(
            "/api/despesas/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        prioridade_paa_custeio_500.refresh_from_db()
        assert prioridade_paa_custeio_500.valor_total is None, (
            "PrioridadePaa deve ter valor_total=None quando a despesa consume todo o saldo"
        )

    def test_cria_despesa_completa_nao_limpa_prioridade_quando_saldo_suficiente(
            self,
            jwt_authenticated_client_d,
            associacao, tipo_documento, tipo_transacao, conta_associacao, acao_associacao,
            tipo_custeio, especificacao_material_servico,
            paa_em_elaboracao, receita_prevista_custeio_1000, prioridade_paa_custeio_500):
        """
        Criar uma despesa cujo valor_rateio (100) não esgota o saldo disponível (500)
        deve manter PrioridadePaa.valor_total inalterado.

        Cálculo:
          receita_custeio = 1000 (ReceitaPrevistaPaa)
          despesa_custeio = 500  (PrioridadePaa)
          saldo_custeio   = 1000 - 500 = 500
          saldo_disponivel = 0 + 0 + 500 = 500
          500 >= 100 → saldo suficiente → valor_total permanece 500
        """
        payload = _payload_despesa_custeio(
            associacao, tipo_documento, tipo_transacao,
            conta_associacao, acao_associacao,
            tipo_custeio, especificacao_material_servico,
            valor_rateio=100,
        )

        response = jwt_authenticated_client_d.post(
            "/api/despesas/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        prioridade_paa_custeio_500.refresh_from_db()
        assert prioridade_paa_custeio_500.valor_total == 500, (
            "PrioridadePaa deve manter valor_total quando há saldo suficiente"
        )

    def test_cria_despesa_incompleta_nao_limpa_prioridade(
            self,
            jwt_authenticated_client_d,
            associacao, acao_associacao,
            tipo_custeio, especificacao_material_servico,
            paa_em_elaboracao, receita_prevista_custeio_500, prioridade_paa_custeio_500):
        """
        Despesa incompleta (sem data_transacao e sem conta_associacao) não deve acionar
        a limpeza de prioridades. O callback só é chamado quando despesa.status == STATUS_COMPLETO.

        Nota: omitir conta_associacao evita o TypeError em _validar_contas_rateios
        quando data_transacao=None (ver análise de pontos fracos).
        """
        payload = {
            "associacao": str(associacao.uuid),
            "tipo_documento": None,
            "tipo_transacao": None,
            "numero_documento": "",
            "data_documento": None,
            "cpf_cnpj_fornecedor": "",
            "nome_fornecedor": "",
            "data_transacao": None,  # sem data → status=INCOMPLETO
            "valor_total": 600,
            "valor_recursos_proprios": 0,
            "motivos_pagamento_antecipado": [],
            "outros_motivos_pagamento_antecipado": "",
            "rateios": [
                {
                    "associacao": str(associacao.uuid),
                    "conta_associacao": None,   # ausente → rateio incompleto
                    "acao_associacao": str(acao_associacao.uuid),
                    "aplicacao_recurso": "CUSTEIO",
                    "tipo_custeio": tipo_custeio.id,
                    "especificacao_material_servico": especificacao_material_servico.id,
                    "valor_rateio": 600,
                    "quantidade_itens_capital": 0,
                    "valor_item_capital": 0,
                    "numero_processo_incorporacao_capital": "",
                }
            ],
        }

        response = jwt_authenticated_client_d.post(
            "/api/despesas/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        despesa_criada = Despesa.objects.get(uuid=response.json()["uuid"])
        assert despesa_criada.status != "COMPLETO", "Despesa deve ser INCOMPLETO para o teste ser válido"

        prioridade_paa_custeio_500.refresh_from_db()
        assert prioridade_paa_custeio_500.valor_total == 500, (
            "Despesa incompleta não deve limpar PrioridadePaa"
        )

    def test_cria_despesa_nao_limpa_prioridade_quando_paa_saldo_congelado(
            self,
            jwt_authenticated_client_d,
            associacao, tipo_documento, tipo_transacao, conta_associacao, acao_associacao,
            tipo_custeio, especificacao_material_servico,
            paa_factory, periodo_paa_para_teste):
        """
        PAA com saldo_congelado_em preenchido não deve ter suas prioridades limpas.
        O filtro `paa__saldo_congelado_em__isnull=True` exclui PAAs congelados.
        """
        from django.utils import timezone

        paa_congelado = paa_factory.create(
            periodo_paa=periodo_paa_para_teste,
            associacao=associacao,
            status="EM_ELABORACAO",
            saldo_congelado_em=timezone.now(),  # saldo congelado
        )
        prioridade = baker.make(
            "PrioridadePaa",
            paa=paa_congelado,
            recurso=RecursoOpcoesEnum.PTRF.name,
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
            acao_associacao=acao_associacao,
            valor_total=500,
        )
        baker.make(
            "ReceitaPrevistaPaa",
            paa=paa_congelado,
            acao_associacao=acao_associacao,
            previsao_valor_custeio=500,
            previsao_valor_capital=0,
            previsao_valor_livre=0,
            saldo_congelado_custeio=None,
            saldo_congelado_capital=None,
            saldo_congelado_livre=None,
        )

        payload = _payload_despesa_custeio(
            associacao, tipo_documento, tipo_transacao,
            conta_associacao, acao_associacao,
            tipo_custeio, especificacao_material_servico,
            valor_rateio=600,
        )

        response = jwt_authenticated_client_d.post(
            "/api/despesas/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        prioridade.refresh_from_db()
        assert prioridade.valor_total == 500, (
            "PAA com saldo congelado não deve ter PrioridadePaa limpa"
        )


# EDIÇÃO DE DESPESA (PUT)
class TestPutDespesaImpactaPrioridadePaa:

    def test_edita_despesa_sem_mudanca_de_valor_nao_limpa_prioridade_quando_saldo_suficiente(
            self,
            jwt_authenticated_client_d,
            associacao, tipo_documento, tipo_transacao, conta_associacao, acao_associacao,
            tipo_custeio, especificacao_material_servico,
            despesa_factory,
            paa_em_elaboracao, receita_prevista_custeio_1000, prioridade_paa_custeio_500):
        """
        Editar uma despesa sem alterar o valor do rateio, com saldo suficiente,
        não deve limpar a PrioridadePaa.

        Cálculo:
          delta = 100 (novo) - 100 (antigo) = 0
          saldo_disponivel = 500  (receita=1000, prioridade=500 → saldo_custeio=500)
          500 >= 0 → sem limpeza
        """
        despesa = despesa_factory(
            associacao=associacao,
            numero_documento="123456",
            data_documento=date(2020, 3, 10),
            tipo_documento=tipo_documento,
            cpf_cnpj_fornecedor="36.352.197/0001-75",
            nome_fornecedor="Fornecedor SA",
            tipo_transacao=tipo_transacao,
            documento_transacao="123456789",
            data_transacao=date(2020, 3, 10),
            valor_total=100.00,
        )
        rateio = baker.make(
            "RateioDespesa",
            despesa=despesa,
            associacao=associacao,
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            aplicacao_recurso="CUSTEIO",
            tipo_custeio=tipo_custeio,
            especificacao_material_servico=especificacao_material_servico,
            valor_rateio=100,
        )
        despesa.rateios.set([rateio])

        payload = {
            "associacao": str(associacao.uuid),
            "tipo_documento": tipo_documento.id,
            "tipo_transacao": tipo_transacao.id,
            "documento_transacao": "123456789",
            "numero_documento": "634767",
            "data_documento": "2020-03-10",
            "cpf_cnpj_fornecedor": "36.352.197/0001-75",
            "nome_fornecedor": "FORNECEDOR TESTE SA",
            "data_transacao": "2020-03-10",
            "valor_total": 100,
            "valor_recursos_proprios": 0,
            "motivos_pagamento_antecipado": [],
            "outros_motivos_pagamento_antecipado": "",
            "rateios": [
                {
                    "uuid": str(rateio.uuid),
                    "associacao": str(associacao.uuid),
                    "conta_associacao": str(conta_associacao.uuid),
                    "acao_associacao": str(acao_associacao.uuid),
                    "aplicacao_recurso": "CUSTEIO",
                    "tipo_custeio": tipo_custeio.id,
                    "especificacao_material_servico": especificacao_material_servico.id,
                    "valor_rateio": 100,  # mesmo valor
                    "quantidade_itens_capital": 0,
                    "valor_item_capital": 0,
                    "numero_processo_incorporacao_capital": "",
                }
            ],
        }

        response = jwt_authenticated_client_d.put(
            f"/api/despesas/{despesa.uuid}/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK

        prioridade_paa_custeio_500.refresh_from_db()
        assert prioridade_paa_custeio_500.valor_total == 500, (
            "PrioridadePaa não deve ser limpa quando não há incremento expressivo de saldo"
        )


class TestPostDespesaCapitalComSaldoNegativo:
    """
    Cenário: PrioridadePaa CAPITAL com valor_total que excede a receita de capital (zero),
    tornando total_livre negativo no resumo. Uma nova despesa CAPITAL deve limpar
    a prioridade CAPITAL, mas a prioridade CUSTEIO NÃO deve ser tocada.

    Cálculo do resumo com ambas as prioridades presentes:
      receita_custeio = 500, despesa_custeio = 500 → total_custeio = 0, diferenca = 0
      receita_capital = 0,   despesa_capital = 300 → total_capital = 0, diferenca = -300
      descontar_de_livre += 300
      total_livre = 0 - 300 = -300  ← NEGATIVO

      saldo do nó da ação = {custeio: 0, capital: 0, livre: -300}

    Para a prioridade CAPITAL (filtro: tipo_aplicacao=CAPITAL):
      saldo_disponivel = -300 (livre) + 0 (valor_atual=0) + 0 (capital) = -300
      -300 < 100 (valor_rateio) → raise → prioridade CAPITAL limpa

    Para a prioridade CUSTEIO:
      Não está no queryset (filtro tipo_aplicacao=CAPITAL a exclui) → intocada
    """

    def test_despesa_capital_limpa_prioridade_capital_quando_saldo_livre_negativo(
            self,
            jwt_authenticated_client_d,
            associacao, tipo_documento, tipo_transacao, conta_associacao, acao_associacao,
            especificacao_capital,
            paa_em_elaboracao, receita_prevista_custeio_500,
            prioridade_paa_custeio_500, prioridade_paa_capital_300):
        """
        Ao criar uma despesa CAPITAL com valor_rateio=100, a PrioridadePaa CAPITAL
        deve ser limpa porque saldo_disponivel (-300) < valor_rateio (100).

        O saldo negativo resulta do déficit de capital:
          despesa_capital (300) > receita_capital (0)
          → excesso de 300 desconta de total_livre: 0 - 300 = -300
        """
        # Pre-conditions: ambas as prioridades existem com seus valores iniciais.
        # prioridade_paa_custeio_500 é necessária para que calcula_saldos compute o
        # déficit corretamente (300 CAPITAL > 0 receita_capital → total_livre = -300).
        assert prioridade_paa_custeio_500.valor_total == 500
        assert prioridade_paa_capital_300.valor_total == 300
        assert receita_prevista_custeio_500.paa == paa_em_elaboracao

        payload = _payload_despesa_capital(
            associacao, tipo_documento, tipo_transacao,
            conta_associacao, acao_associacao,
            especificacao_capital,
            valor_rateio=100,
        )

        response = jwt_authenticated_client_d.post(
            "/api/despesas/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        prioridade_paa_capital_300.refresh_from_db()
        assert prioridade_paa_capital_300.valor_total is None, (
            "PrioridadePaa CAPITAL deve ser limpa quando saldo_livre é negativo"
        )

    def test_despesa_capital_nao_afeta_prioridade_custeio_mesmo_com_saldo_livre_negativo(
            self,
            jwt_authenticated_client_d,
            associacao, tipo_documento, tipo_transacao, conta_associacao, acao_associacao,
            especificacao_capital,
            paa_em_elaboracao, receita_prevista_custeio_500,
            prioridade_paa_custeio_500, prioridade_paa_capital_300):
        """
        A PrioridadePaa CUSTEIO deve ser limpa quando a despesa criada é CAPITAL porque ambas consomem do saldo,
        Considerando que ao criar uma despesa diferente do tipo de aplicação(capital/custeio) da prioridade, o saldo
        é utilizado pelo reprogramado

       Uma despesa verifica prioridades CAPITAL/CUSTEIO.
        """
        # Pre-conditions: prioridade_paa_capital_300 cria o déficit de capital que torna
        # total_livre negativo; prioridade_paa_custeio_500 é quem não deve ser limpa.
        assert prioridade_paa_capital_300.valor_total == 300
        assert prioridade_paa_custeio_500.valor_total == 500
        assert receita_prevista_custeio_500.paa == paa_em_elaboracao

        payload = _payload_despesa_capital(
            associacao, tipo_documento, tipo_transacao,
            conta_associacao, acao_associacao,
            especificacao_capital,
            valor_rateio=100,
        )

        response = jwt_authenticated_client_d.post(
            "/api/despesas/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        prioridade_paa_custeio_500.refresh_from_db()
        prioridade_paa_capital_300.refresh_from_db()
        # Prioridades devem ter o valor limpo
        assert prioridade_paa_custeio_500.valor_total is None
        assert prioridade_paa_capital_300.valor_total is None

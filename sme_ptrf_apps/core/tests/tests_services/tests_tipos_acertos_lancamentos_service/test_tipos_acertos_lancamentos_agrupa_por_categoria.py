import pytest
from sme_ptrf_apps.core.models import TipoAcertoLancamento
from sme_ptrf_apps.core.services import TipoAcertoLancamentoService

pytestmark = pytest.mark.django_db


def test_service_tabelas_categorias():
    resultado_esperado = [
        {
            "id": "DEVOLUCAO",
            "nome": "Devolução ao tesouro"
        },
        {
            "id": "EDICAO_LANCAMENTO",
            "nome": "Edição do lançamento"
        },
        {
            "id": "EXCLUSAO_LANCAMENTO",
            "nome": "Exclusão do lançamento"
        },
        {
            "id": "AJUSTES_EXTERNOS",
            "nome": "Ajustes externos"
        },
        {
            "id": "SOLICITACAO_ESCLARECIMENTO",
            "nome": "Solicitação de esclarecimento"
        }
    ]

    assert resultado_esperado == TipoAcertoLancamentoService.categorias(TipoAcertoLancamento.CATEGORIA_CHOICES)


def test_service_tabelas_agrupado_por_categorias(
    tipo_acerto_lancamento_agrupa_categoria_01,
    tipo_acerto_lancamento_agrupa_categoria_02,
    tipo_acerto_lancamento_agrupa_categoria_03,
    tipo_acerto_lancamento_agrupa_categoria_04,
    tipo_acerto_lancamento_agrupa_categoria_05  # Nao deve entrar na listagem
):

    resultado_esperado = [
        {
            "categoria": {
                "id": "DEVOLUCAO",
                "nome": "Devolução ao tesouro",
                "texto": "Esse tipo de acerto demanda informação da data de pagamento da devolução.",
                "cor": 1,
                "tipos_acerto_lancamento": [
                    {
                        "nome": "Teste",
                        "uuid": tipo_acerto_lancamento_agrupa_categoria_01.uuid
                    },
                    {
                        "nome": "Teste 2",
                        "uuid": tipo_acerto_lancamento_agrupa_categoria_02.uuid
                    },
                    {
                        "nome": "Teste 3",
                        "uuid": tipo_acerto_lancamento_agrupa_categoria_03.uuid
                    }
                ]
            }
        },
        {
            "categoria": {
                "id": "EDICAO_LANCAMENTO",
                "nome": "Edição do lançamento",
                "texto": "Esse tipo de acerto reabre o lançamento para edição.",
                "cor": 1,
                "tipos_acerto_lancamento": [
                    {
                        "nome": "Teste 4",
                        "uuid": tipo_acerto_lancamento_agrupa_categoria_04.uuid
                    }
                ]
            }
        }
    ]

    resultado = TipoAcertoLancamentoService.agrupado_por_categoria(TipoAcertoLancamento.CATEGORIA_CHOICES)

    assert resultado_esperado == resultado



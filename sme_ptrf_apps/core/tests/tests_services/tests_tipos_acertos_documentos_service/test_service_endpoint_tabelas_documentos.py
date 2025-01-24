import pytest
from sme_ptrf_apps.core.models import TipoAcertoDocumento, TipoDocumentoPrestacaoConta
from sme_ptrf_apps.core.services import TipoAcertoDocumentoService

pytestmark = pytest.mark.django_db


def test_service_tabelas_categorias():
    resultado_esperado = [
        {
            "id": "INCLUSAO_CREDITO",
            "nome": "Inclusão de crédito"
        },
        {
            "id": "INCLUSAO_GASTO",
            "nome": "Inclusão de gasto"
        },
        {
            "id": "EDICAO_INFORMACAO",
            "nome": "Edição de informação"
        },
        {
            "id": "AJUSTES_EXTERNOS",
            "nome": "Ajustes externos"
        },
        {
            "id": "SOLICITACAO_ESCLARECIMENTO",
            "nome": "Solicitação de esclarecimento"
        },

    ]

    assert resultado_esperado == TipoAcertoDocumentoService.categorias(TipoAcertoDocumento.CATEGORIA_CHOICES)


def test_service_tabelas_agrupado_por_categorias(
    tipo_acerto_documento_agrupa_categoria_01,
    tipo_acerto_documento_agrupa_categoria_02,
    tipo_acerto_documento_agrupa_categoria_03,
    tipo_acerto_documento_agrupa_categoria_04,
    tipo_acerto_documento_agrupa_categoria_05  # Nao deve entrar na listagem
):

    resultado_esperado = [
        {
            "id": "INCLUSAO_CREDITO",
            "nome": "Inclusão de crédito",
            "texto": "Esse tipo de acerto reabre o período para inclusão de um crédito.",
            "cor": 1,
            "tipos_acerto_documento": [
                {
                    "nome": "Teste",
                    "uuid": tipo_acerto_documento_agrupa_categoria_01.uuid
                },
                {
                    "nome": "Teste 2",
                    "uuid": tipo_acerto_documento_agrupa_categoria_02.uuid
                },
                {
                    "nome": "Teste 3",
                    "uuid": tipo_acerto_documento_agrupa_categoria_03.uuid
                }
                ]
        },
        {
            "id": "INCLUSAO_GASTO",
            "nome": "Inclusão de gasto",
            "texto": "Esse tipo de acerto reabre o período para inclusão de um gasto.",
            "cor": 1,
            "tipos_acerto_documento": [
                {
                    "nome": "Teste 4",
                    "uuid": tipo_acerto_documento_agrupa_categoria_04.uuid
                }
            ]
        }
    ]

    resultado = TipoAcertoDocumentoService.agrupado_por_categoria(TipoAcertoDocumento.CATEGORIA_CHOICES)

    assert resultado_esperado == resultado


def test_service_tabelas_tipos_documentos(tipo_documento_prestacao_conta_relacao_bens_01):
    resultado_esperado = [
        {
            "id": tipo_documento_prestacao_conta_relacao_bens_01.id,
            "nome": "Relação de bens da conta"
        }
    ]

    resultado = list(TipoDocumentoPrestacaoConta.lista_documentos())

    assert resultado_esperado == resultado


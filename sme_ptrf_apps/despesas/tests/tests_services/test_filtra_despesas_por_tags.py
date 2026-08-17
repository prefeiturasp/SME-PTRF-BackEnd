"""Testes para filtra_despesas_por_tags — decide se uma Despesa/RateioDespesa deve ser
excluída de uma listagem filtrada por tags de informação (ex.: Antecipado, Estornado)."""
from unittest.mock import MagicMock

import pytest

from sme_ptrf_apps.despesas.services.filtra_despesas_por_tags import filtra_despesas_por_tags
from ...models import Despesa

pytestmark = pytest.mark.django_db


def _item_neutro(**overrides) -> MagicMock:
    """Duble de Despesa com todos os predicados de tag em False (nenhuma tag se aplica).

    `conferido` inicia True para que TAG_NAO_CONCILIADA (que verifica `not conferido`)
    também comece neutra. Use overrides para forçar um predicado específico como True
    (ou `conferido=False`).
    """
    item = MagicMock()
    item.teve_pagamento_antecipado.return_value = False
    item.possui_estornos.return_value = False
    item.possui_retencao_de_impostos.return_value = False
    item.e_imposto_pago.return_value = False
    item.e_imposto_nao_pago.return_value = False
    item.tem_pagamento_com_recursos_proprios.return_value = False
    item.tem_pagamentos_em_multiplas_contas.return_value = False
    item.e_despesa_nao_reconhecida.return_value = False
    item.e_despesa_sem_comprovacao_fiscal.return_value = False
    item.conferido = True

    for nome, valor in overrides.items():
        if nome == "conferido":
            item.conferido = valor
        else:
            getattr(item, nome).return_value = valor

    return item


class TestSemCorrespondencia:
    def test_sem_filtro_retorna_true_mesmo_com_todos_os_predicados_verdadeiros(self):
        item = _item_neutro(
            teve_pagamento_antecipado=True,
            possui_estornos=True,
            possui_retencao_de_impostos=True,
            e_imposto_pago=True,
            e_imposto_nao_pago=True,
            tem_pagamento_com_recursos_proprios=True,
            tem_pagamentos_em_multiplas_contas=True,
            e_despesa_nao_reconhecida=True,
            e_despesa_sem_comprovacao_fiscal=True,
            conferido=False,
        )

        assert filtra_despesas_por_tags(item, []) is True

    def test_item_neutro_com_todas_as_tags_no_filtro_retorna_true(self):
        """`conferido` não tem estado neutro (é sempre True ou False), então TAG_CONCILIADA e
        TAG_NAO_CONCILIADA ficam de fora desta lista — são cobertas isoladamente abaixo."""
        item = _item_neutro()
        todas_as_tags = [
            Despesa.TAG_ANTECIPADO["id"],
            Despesa.TAG_ESTORNADO["id"],
            Despesa.TAG_IMPOSTO["id"],
            Despesa.TAG_IMPOSTO_PAGO["id"],
            Despesa.TAG_IMPOSTO_A_SER_PAGO["id"],
            Despesa.TAG_PARCIAL["id"],
            Despesa.TAG_NAO_RECONHECIDA["id"],
            Despesa.TAG_SEM_COMPROVACAO_FISCAL["id"],
        ]

        assert filtra_despesas_por_tags(item, todas_as_tags) is True

    def test_predicado_verdadeiro_mas_tag_fora_do_filtro_nao_afeta_o_resultado(self):
        item = _item_neutro(teve_pagamento_antecipado=True)

        assert filtra_despesas_por_tags(item, [Despesa.TAG_ESTORNADO["id"]]) is True


class TestCadaTagExcluiQuandoPredicadoVerdadeiro:
    def test_tag_antecipado(self):
        item = _item_neutro(teve_pagamento_antecipado=True)

        assert filtra_despesas_por_tags(item, [Despesa.TAG_ANTECIPADO["id"]]) is False

    def test_tag_estornado(self):
        item = _item_neutro(possui_estornos=True)

        assert filtra_despesas_por_tags(item, [Despesa.TAG_ESTORNADO["id"]]) is False

    def test_tag_imposto(self):
        item = _item_neutro(possui_retencao_de_impostos=True)

        assert filtra_despesas_por_tags(item, [Despesa.TAG_IMPOSTO["id"]]) is False

    def test_tag_imposto_pago(self):
        item = _item_neutro(e_imposto_pago=True)

        assert filtra_despesas_por_tags(item, [Despesa.TAG_IMPOSTO_PAGO["id"]]) is False

    def test_tag_imposto_a_ser_pago(self):
        item = _item_neutro(e_imposto_nao_pago=True)

        assert filtra_despesas_por_tags(item, [Despesa.TAG_IMPOSTO_A_SER_PAGO["id"]]) is False

    def test_tag_parcial_via_pagamento_com_recursos_proprios(self):
        item = _item_neutro(tem_pagamento_com_recursos_proprios=True)

        assert filtra_despesas_por_tags(item, [Despesa.TAG_PARCIAL["id"]]) is False

    def test_tag_parcial_via_pagamentos_em_multiplas_contas(self):
        item = _item_neutro(tem_pagamentos_em_multiplas_contas=True)

        assert filtra_despesas_por_tags(item, [Despesa.TAG_PARCIAL["id"]]) is False

    def test_tag_nao_reconhecida(self):
        item = _item_neutro(e_despesa_nao_reconhecida=True)

        assert filtra_despesas_por_tags(item, [Despesa.TAG_NAO_RECONHECIDA["id"]]) is False

    def test_tag_sem_comprovacao_fiscal(self):
        item = _item_neutro(e_despesa_sem_comprovacao_fiscal=True)

        assert filtra_despesas_por_tags(item, [Despesa.TAG_SEM_COMPROVACAO_FISCAL["id"]]) is False

    def test_tag_conciliada(self):
        item = _item_neutro(conferido=True)

        assert filtra_despesas_por_tags(item, [Despesa.TAG_CONCILIADA["id"]]) is False

    def test_tag_nao_conciliada(self):
        item = _item_neutro(conferido=False)

        assert filtra_despesas_por_tags(item, [Despesa.TAG_NAO_CONCILIADA["id"]]) is False

    def test_tag_no_filtro_mas_predicado_falso_retorna_true(self):
        item = _item_neutro(teve_pagamento_antecipado=False)

        assert filtra_despesas_por_tags(item, [Despesa.TAG_ANTECIPADO["id"]]) is True


class TestCurtoCircuitoEComportamentoDeRateio:
    def test_para_na_primeira_tag_que_corresponde_sem_avaliar_as_seguintes(self):
        item = _item_neutro(teve_pagamento_antecipado=True)

        resultado = filtra_despesas_por_tags(
            item,
            [Despesa.TAG_ANTECIPADO["id"], Despesa.TAG_ESTORNADO["id"]],
        )

        assert resultado is False
        item.possui_estornos.assert_not_called()

    def test_rateio_true_avalia_a_despesa_do_rateio_no_lugar_do_item(self):
        despesa = _item_neutro(teve_pagamento_antecipado=True)
        rateio = MagicMock(despesa=despesa)

        resultado = filtra_despesas_por_tags(rateio, [Despesa.TAG_ANTECIPADO["id"]], rateio=True)

        assert resultado is False
        despesa.teve_pagamento_antecipado.assert_called_once()

    def test_rateio_false_nao_acessa_o_atributo_despesa(self):
        item = _item_neutro(teve_pagamento_antecipado=True)
        item.despesa = None

        resultado = filtra_despesas_por_tags(item, [Despesa.TAG_ANTECIPADO["id"]], rateio=False)

        assert resultado is False

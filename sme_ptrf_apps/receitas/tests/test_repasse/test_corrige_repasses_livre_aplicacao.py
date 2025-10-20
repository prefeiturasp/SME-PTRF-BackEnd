from decimal import Decimal
from datetime import date

import pytest

from sme_ptrf_apps.receitas.models import Repasse, Receita, TipoReceita


pytestmark = pytest.mark.django_db


def test_corrige_repasses_livre_aplicacao_atualiza_repasses_com_receita():
    tipo_receita = TipoReceita.objects.create(
        nome='Tipo Receita Teste',
        aceita_capital=True,
        aceita_custeio=True,
        aceita_livre=True,
        e_repasse=True,
    )

    repasse_atualizado_1 = Repasse.objects.create(
        valor_livre=Decimal('100.00'),
        realizado_livre=False,
    )
    repasse_atualizado_2 = Repasse.objects.create(
        valor_livre=Decimal('50.00'),
        realizado_livre=False,
    )
    repasse_sem_receita = Repasse.objects.create(
        valor_livre=Decimal('75.00'),
        realizado_livre=False,
    )
    repasse_valor_zero = Repasse.objects.create(
        valor_livre=Decimal('0.00'),
        realizado_livre=False,
    )
    repasse_ja_realizado = Repasse.objects.create(
        valor_livre=Decimal('120.00'),
        realizado_livre=True,
    )

    Receita.objects.create(
        repasse=repasse_atualizado_1,
        tipo_receita=tipo_receita,
        data=date(2024, 1, 10),
    )
    Receita.objects.create(
        repasse=repasse_atualizado_2,
        tipo_receita=tipo_receita,
        data=date(2024, 1, 11),
    )
    Receita.objects.create(
        repasse=repasse_ja_realizado,
        tipo_receita=tipo_receita,
        data=date(2024, 1, 12),
    )

    quantidade_atualizada = (
        Repasse.objects.filter(
            valor_livre__gt=0,
            realizado_livre=False,
            receitas__isnull=False,
        )
        .distinct()
        .update(realizado_livre=True)
    )

    repasse_atualizado_1.refresh_from_db()
    repasse_atualizado_2.refresh_from_db()
    repasse_sem_receita.refresh_from_db()
    repasse_valor_zero.refresh_from_db()
    repasse_ja_realizado.refresh_from_db()

    assert quantidade_atualizada == 2
    assert repasse_atualizado_1.realizado_livre is True
    assert repasse_atualizado_2.realizado_livre is True
    assert repasse_sem_receita.realizado_livre is False
    assert repasse_valor_zero.realizado_livre is False
    assert repasse_ja_realizado.realizado_livre is True

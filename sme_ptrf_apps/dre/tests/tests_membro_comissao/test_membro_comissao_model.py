import pytest

from sme_ptrf_apps.dre.models import MembroComissao
from sme_ptrf_apps.core.models import Unidade

pytestmark = pytest.mark.django_db


def test_instance_model(membro_comissao_exame_contas):
    model = membro_comissao_exame_contas
    assert isinstance(model, MembroComissao)
    assert isinstance(model.dre, Unidade)
    assert model.rf
    assert model.nome
    assert model.email
    assert model.uuid
    assert model.comissoes is not None
    assert model.criado_em


def test_srt_model(membro_comissao_exame_contas):
    assert str(membro_comissao_exame_contas) == '<RF:123456 Nome:Jose Testando Qtd.Comissões:1>'


def test_admin():
    from django.contrib import admin
    assert admin.site._registry[MembroComissao]


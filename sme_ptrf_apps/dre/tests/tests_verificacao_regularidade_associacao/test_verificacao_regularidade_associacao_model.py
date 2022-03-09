import pytest
from django.contrib import admin

from ...models import (GrupoVerificacaoRegularidade, ListaVerificacaoRegularidade, ItemVerificacaoRegularidade,
                       VerificacaoRegularidadeAssociacao, AnaliseRegularidadeAssociacao)
from ....core.models import Associacao

pytestmark = pytest.mark.django_db


def test_instance_model(verificacao_regularidade_associacao_documento_cnpj):
    model = verificacao_regularidade_associacao_documento_cnpj
    assert isinstance(model, VerificacaoRegularidadeAssociacao)
    assert isinstance(model.item_verificacao, ItemVerificacaoRegularidade)
    assert isinstance(model.analise_regularidade, AnaliseRegularidadeAssociacao)
    assert model.regular
    assert model.uuid
    assert model.id


def test_srt_model(verificacao_regularidade_associacao_documento_cnpj):
    verificacao_id = verificacao_regularidade_associacao_documento_cnpj.id
    esperado = f'Verificação:{verificacao_id}-CNPJ'
    assert verificacao_regularidade_associacao_documento_cnpj.__str__() == esperado


def test_meta_modelo(verificacao_regularidade_associacao_documento_cnpj):
    assert verificacao_regularidade_associacao_documento_cnpj._meta.verbose_name == 'Verificação de regularidade de associação'
    assert verificacao_regularidade_associacao_documento_cnpj._meta.verbose_name_plural == 'Verificações de regularidade de associações'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[VerificacaoRegularidadeAssociacao]

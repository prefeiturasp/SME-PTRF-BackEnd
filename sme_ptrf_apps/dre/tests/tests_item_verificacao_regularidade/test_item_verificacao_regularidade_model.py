import pytest
from django.contrib import admin

from ...models import ListaVerificacaoRegularidade, ItemVerificacaoRegularidade

pytestmark = pytest.mark.django_db

def test_instance_model(item_verificacao_regularidade_documentos_associacao_cnpj):
    model = item_verificacao_regularidade_documentos_associacao_cnpj
    assert isinstance(model, ItemVerificacaoRegularidade)
    assert isinstance(model.lista, ListaVerificacaoRegularidade)
    assert model.descricao
    assert model.uuid
    assert model.id


def test_srt_model(item_verificacao_regularidade_documentos_associacao_cnpj):
    assert item_verificacao_regularidade_documentos_associacao_cnpj.__str__() == 'CNPJ'


def test_meta_modelo(item_verificacao_regularidade_documentos_associacao_cnpj):
    assert item_verificacao_regularidade_documentos_associacao_cnpj._meta.verbose_name == 'Item de verificação de regularidade'
    assert item_verificacao_regularidade_documentos_associacao_cnpj._meta.verbose_name_plural == 'Itens de verificação de regularidade'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[ItemVerificacaoRegularidade]

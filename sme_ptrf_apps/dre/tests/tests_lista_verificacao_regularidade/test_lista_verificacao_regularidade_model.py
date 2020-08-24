import pytest
from django.contrib import admin

from ...models import GrupoVerificacaoRegularidade, ListaVerificacaoRegularidade

pytestmark = pytest.mark.django_db

def test_instance_model(lista_verificacao_regularidade_documentos_associacao):
    model = lista_verificacao_regularidade_documentos_associacao
    assert isinstance(model, ListaVerificacaoRegularidade)
    assert isinstance(model.grupo, GrupoVerificacaoRegularidade)
    assert model.titulo
    assert model.uuid
    assert model.id
    assert model.itens_de_verificacao


def test_srt_model(lista_verificacao_regularidade_documentos_associacao):
    assert lista_verificacao_regularidade_documentos_associacao.__str__() == 'Documentos da Associação'


def test_meta_modelo(lista_verificacao_regularidade_documentos_associacao):
    assert lista_verificacao_regularidade_documentos_associacao._meta.verbose_name == 'Lista de verificação de regularidade'
    assert lista_verificacao_regularidade_documentos_associacao._meta.verbose_name_plural == 'Listas de verificação de regularidade'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[ListaVerificacaoRegularidade]

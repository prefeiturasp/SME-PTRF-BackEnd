import pytest
from django.contrib import admin

from ...models import GrupoVerificacaoRegularidade

pytestmark = pytest.mark.django_db

def test_instance_model(grupo_verificacao_regularidade_documentos):
    model = grupo_verificacao_regularidade_documentos
    assert isinstance(model, GrupoVerificacaoRegularidade)
    assert model.titulo
    assert model.uuid
    assert model.id
    assert model.listas_de_verificacao


def test_srt_model(grupo_verificacao_regularidade_documentos):
    assert grupo_verificacao_regularidade_documentos.__str__() == 'Documentos'


def test_meta_modelo(grupo_verificacao_regularidade_documentos):
    assert grupo_verificacao_regularidade_documentos._meta.verbose_name == 'Grupo de verificação de regularidade'
    assert grupo_verificacao_regularidade_documentos._meta.verbose_name_plural == 'Grupos de verificação de regularidade'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[GrupoVerificacaoRegularidade]

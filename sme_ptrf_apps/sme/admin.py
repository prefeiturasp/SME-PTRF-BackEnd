from django.contrib import admin
from .models import (
    ParametrosSme,
    TipoUnidadeAdministrativa
)

# Register your models here.
admin.site.register(ParametrosSme)


@admin.register(TipoUnidadeAdministrativa)
class TipoUnidadeAdministrativaAdmin(admin.ModelAdmin):

    list_display = [
        'tipo_unidade_administrativa',
        'inicio_codigo_eol',
    ]
    readonly_fields = ('uuid', 'criado_em', 'alterado_em', )

    search_fields = [
        'tipo_unidade_administrativa',
        'inicio_codigo_eol',
    ]

    list_filter = [
        'tipo_unidade_administrativa',
    ]

from django.contrib import admin

from .models import TipoTransacao, TipoDocumento, TipoCusteio

admin.site.register(TipoTransacao)
admin.site.register(TipoDocumento)
admin.site.register(TipoCusteio)


from django.contrib import admin

from .models import TipoTransacao, TipoDocumento, TipoCusteio, Despesa

admin.site.register(TipoTransacao)
admin.site.register(TipoDocumento)
admin.site.register(TipoCusteio)
admin.site.register(Despesa)

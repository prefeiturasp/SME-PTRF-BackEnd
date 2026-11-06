from django.db import models


class AlertaPaginaQuerySet(models.QuerySet):
    def ativos(self):
        return self.filter(ativo=True)

    def da_categoria(self, categoria):
        return self.filter(categoria=categoria)

    def do_recurso(self, recurso):
        return self.filter(recurso=recurso)

    def com_envio_de_email(self):
        return self.filter(enviar_email=True)

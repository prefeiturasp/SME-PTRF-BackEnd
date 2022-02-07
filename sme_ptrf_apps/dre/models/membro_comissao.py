import logging
from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from django.db.models.signals import pre_save
from django.dispatch import receiver


logger = logging.getLogger(__name__)


class MembroComissao(ModeloBase):
    history = AuditlogHistoryField()

    rf = models.CharField('RF', max_length=10)
    nome = models.CharField('Nome', max_length=160)
    email = models.EmailField("E-mail", max_length=254, null=True, blank=True)

    dre = models.ForeignKey('core.Unidade', on_delete=models.PROTECT, related_name='membros_de_comissoes',
                            to_field="codigo_eol", limit_choices_to={'tipo_unidade': 'DRE'})

    comissoes = models.ManyToManyField('Comissao', related_name='membros', verbose_name='Comissões')

    cargo = models.CharField('Cargo', max_length=65, blank=True, default="", null=True)

    @property
    def qtd_comissoes(self):
        return self.comissoes.count()

    def get_cargo_eol(self):
        from sme_ptrf_apps.core.services import TerceirizadasService
        if self.rf:
            result = TerceirizadasService.get_informacao_servidor(self.rf)
            if result:
                try:
                    cargo = result[0]["cargo"]
                    return cargo
                except Exception as e:
                    logger.info(f"{e}")
                    return ""
        return ""

    class Meta:
        verbose_name = "Membro de Comissão"
        verbose_name_plural = "Membros de Comissões"

    def __str__(self):
        return f"<RF:{self.rf} Nome:{self.nome} Qtd.Comissões:{self.qtd_comissoes}>"


@receiver(pre_save, sender=MembroComissao)
def membro_comissao_pre_save(instance, **kwargs):
    if not instance.cargo:
        instance.cargo = instance.get_cargo_eol()


auditlog.register(MembroComissao)

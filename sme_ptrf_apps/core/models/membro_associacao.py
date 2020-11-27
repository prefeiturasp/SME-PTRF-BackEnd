from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver

from sme_ptrf_apps.core.choices import MembroEnum, RepresentacaoCargo
from sme_ptrf_apps.core.models_abstracts import ModeloBase

User = get_user_model()


class MembroAssociacao(ModeloBase):
    nome = models.CharField('Nome', max_length=160)

    associacao = models.ForeignKey('Associacao', on_delete=models.PROTECT,
                                   related_name='cargos',
                                   blank=True, null=True)

    cargo_associacao = models.CharField(
        'Cargo Associação',
        max_length=65,
        blank=True,
        null=True,
        choices=MembroEnum.choices(),
        default=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.value)

    cargo_educacao = models.CharField('Cargo Educação', max_length=45, blank=True, null=True, default="")

    representacao = models.CharField(
        'Representação',
        max_length=25,
        choices=RepresentacaoCargo.choices(),
        default=RepresentacaoCargo.SERVIDOR.value
    )

    codigo_identificacao = models.CharField('Código EOL ou RF', max_length=10, blank=True, null=True, default="")

    email = models.EmailField("E-mail", max_length=254, null=True, blank=True)

    usuario = models.OneToOneField(User, on_delete=models.PROTECT, related_name='membro', blank=True, null=True)

    class Meta:
        verbose_name = "Membro da Associação"
        verbose_name_plural = "07.3) Membros das Associações"

    def __str__(self):
        return f"<Nome: {self.nome}, Representacao: {self.representacao}>"


@receiver(pre_save, sender=MembroAssociacao)
def membro_pre_save(instance, **kwargs):
    """Deve garantir que um membro da associação NÃO seja cadastrado mais de uma vez."""

    membro = MembroAssociacao.objects.filter(Q(nome__iexact=(instance.nome or None)) | Q(
        codigo_identificacao__exact=(instance.codigo_identificacao or None))).first()

    if membro and membro.id != instance.id:
        raise ValueError("Membro já cadastrado")

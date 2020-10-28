import base64
import uuid

from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from sme_ptrf_apps.core.choices import RepresentacaoCargo
from sme_ptrf_apps.core.models import Associacao, Unidade
from sme_ptrf_apps.core.models_abstracts import ModeloIdNome


class Visao(ModeloIdNome):

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Visão'
        verbose_name_plural = 'Visões'


class Grupo(Group):
    descricao = models.TextField(blank=True, default='')
    visoes = models.ManyToManyField(Visao, blank=True)


class User(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, null=True)
    name = CharField(_("Nome do usuário"), blank=True, max_length=255)
    hash_redefinicao = models.TextField(blank=True, default='', 
                                        help_text='Campo utilizado para registrar hash na redefinição de senhas.')

    unidades = models.ManyToManyField(Unidade, blank=True)
    visoes = models.ManyToManyField(Visao, blank=True)
    groups = models.ManyToManyField(
        Grupo,
        verbose_name=_('grupos'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="user_set",
        related_query_name="user",
    )

    tipo_usuario = models.CharField(
        'Tipo Usuário',
        max_length=25,
        choices=RepresentacaoCargo.choices(),
        default=RepresentacaoCargo.SERVIDOR.value
    )


    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    @property
    def create_hash(self):
        hash_encode = base64.b64encode(str(self.uuid).encode('utf-8') + str(self.username).encode('utf-8'))
        return hash_encode.decode('utf-8')

    def validar_hash(self, hash_encode):
        if hash_encode == self.create_hash:
            return True
        return False

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

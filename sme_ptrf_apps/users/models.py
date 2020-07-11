import base64
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from sme_ptrf_apps.core.models import Associacao


class User(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, null=True)
    name = CharField(_("Nome do usuário"), blank=True, max_length=255)
    associacao = models.ForeignKey(Associacao, on_delete=models.PROTECT, related_name="usuarios",
                                null=True, blank=True)
    hash_redefinicao = models.TextField(blank=True, default='', 
                                        help_text='Campo utilizado para registrar hash na redefinição de senhas.')

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

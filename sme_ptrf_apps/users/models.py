from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from sme_ptrf_apps.core.models import Associacao


class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = CharField(_("Name of User"), blank=True, max_length=255)

    associacao = models.ForeignKey(Associacao, on_delete=models.PROTECT, related_name='users',
                                   blank=True, null=True)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

from django import forms
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from sme_ptrf_apps.users.forms import UserChangeForm, UserCreationForm
from sme_ptrf_apps.users.models import Visao
from sme_ptrf_apps.core.models import Unidade

User = get_user_model()


class UnidadeChangeListForm(forms.ModelForm):
    # here we only need to define the field we want to be editable
    unidades = forms.ModelMultipleChoiceField(
        queryset=Unidade.objects.all(), required=False)

class UnidadeInline(admin.TabularInline):
    model = Unidade.user_set.through
    extra = 1

@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (("User", {"fields": ("name",)}),) + auth_admin.UserAdmin.fieldsets
    list_display = ["uuid", "username", "name", "is_superuser",]
    search_fields = ["name"]
    inlines = [UnidadeInline,]

admin.site.register(Visao)
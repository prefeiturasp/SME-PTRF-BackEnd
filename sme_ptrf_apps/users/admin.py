from django import forms
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group

from sme_ptrf_apps.users.forms import UserChangeForm, UserCreationForm
from sme_ptrf_apps.users.models import Visao, Grupo
from sme_ptrf_apps.core.models import Unidade

User = get_user_model()


class UnidadeChangeListForm(forms.ModelForm):
    # here we only need to define the field we want to be editable
    unidades = forms.ModelMultipleChoiceField(
        queryset=Unidade.objects.all(), required=False)

class UnidadeInline(admin.TabularInline):
    model = Unidade.user_set.through
    extra = 1

class VisaoInline(admin.TabularInline):
    model = Visao.user_set.through
    extra = 1

@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (("User", {"fields": ("name", "tipo_usuario")}),) + auth_admin.UserAdmin.fieldsets
    list_display = ["uuid", "username", "name", "tipo_usuario", "is_superuser",]
    search_fields = ["name"]
    inlines = [UnidadeInline, VisaoInline]


admin.site.register(Visao)
admin.site.register(Permission)
admin.site.register(Grupo)
admin.site.unregister(Group)

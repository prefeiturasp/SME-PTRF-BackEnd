from django import forms
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

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
    fieldsets = (("User", {"fields": ("name", "e_servidor")}),) + auth_admin.UserAdmin.fieldsets
    list_display = ["uuid", "username", "name", "e_servidor", "is_superuser",]
    search_fields = ["name"]
    inlines = [UnidadeInline, VisaoInline]


@admin.register(Permission)
class PermissaoAdmin(admin.ModelAdmin):
    list_display = ["name", "nome_permissao", "nome_plicativo", "nome_modelo"]
    search_fields = ["name"]

    def nome_plicativo(self, obj):
        return obj.content_type.app_label

    def nome_modelo(self, obj):
        return obj.content_type

    def nome_permissao(self, obj):
        return obj.codename


@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    """
    Versão estendida dos grupos de acesso, queinclui as visões e descrição. As permissões continuam a ser inseridas
    na versão padrão de Group.
    """
    list_display = ["name"]

    fieldsets = (
        ('', {'fields': ('name', )},),
        ('Extras', {'fields': ('descricao', 'visoes')}),
    )


admin.site.register(Visao)

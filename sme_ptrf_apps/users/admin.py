from django import forms
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from sme_ptrf_apps.users.forms import UserChangeForm, UserCreationForm
from sme_ptrf_apps.users.models import Visao, Grupo, UnidadeEmSuporte
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
    list_display = ["uuid", "username", "name", "e_servidor", "is_superuser", ]
    list_filter = ("is_staff", "is_superuser", "is_active", "groups", "unidades__tipo_unidade", "unidades", "unidades__dre", )
    search_fields = ["name", "username", ]
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


@admin.register(UnidadeEmSuporte)
class UnidadeEmSuporteAdmin(admin.ModelAdmin):
    def get_nome_user(self, obj):
        return obj.user.name if obj and obj.user else ''

    get_nome_user.short_description = 'Nome Usuário'

    list_display = ('unidade', 'user', 'get_nome_user', 'criado_em')
    list_filter = ('unidade__dre', 'unidade__tipo_unidade',)
    list_display_links = ('unidade', 'user')
    readonly_fields = ('uuid', 'id')
    search_fields = ('unidade__nome', 'unidade__codigo_eol', 'user__name', 'user__username')
    autocomplete_fields = ['unidade', 'user',]


admin.site.register(Visao)



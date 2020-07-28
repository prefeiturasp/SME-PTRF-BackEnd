from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from sme_ptrf_apps.users.forms import UserChangeForm, UserCreationForm

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (("User", {"fields": ("name","associacao",)}),) + auth_admin.UserAdmin.fieldsets
    list_display = ["uuid", "username", "name", "is_superuser", 'associacao']
    search_fields = ["name"]

    actions = ['importa_usuarios']

    def importa_usuarios(self, request, queryset):
        from sme_ptrf_apps.users.services.carga_usuarios import carrega_usuarios
        carrega_usuarios()
        self.message_user(request, "Usuários Carregados.")

    importa_usuarios.short_description = "Fazer carga de usuários."

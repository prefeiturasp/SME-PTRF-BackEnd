from django import forms

from .models import Comissao


class ComissaoAdminForm(forms.ModelForm):
    class Meta:
        model = Comissao
        fields = ['nome', 'recursos', 'responsavel_analise_pc']

    def clean(self):
        cleaned_data = super().clean()
        recursos = list(cleaned_data.get('recursos') or [])

        if len(recursos) <= 0:
            self.add_error('recursos', 'Pelo menos um recurso deve ser selecionado.')

        self.instance._recursos_validacao = recursos
        return cleaned_data

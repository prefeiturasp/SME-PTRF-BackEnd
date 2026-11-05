from django import forms

from ..models.alerta_pagina import AlertaPagina
from ..services import AlertaPaginaService


class SimulacaoEnvioEmailForm(forms.Form):
    data = forms.DateField(
        label='Data simulada',
        initial=AlertaPaginaService.data_de_hoje(),
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        help_text='Dia para o qual o disparo será simulado.',
    )


class AlertaPaginaForm(forms.ModelForm):
    class Meta:
        model = AlertaPagina
        fields = '__all__'

    def clean(self):
        dados = super().clean()
        if dados.get('enviar_email') and not dados.get('grupos_email'):
            self.add_error('grupos_email', 'Selecione ao menos um grupo quando o envio de e-mail estiver habilitado.')
        return dados

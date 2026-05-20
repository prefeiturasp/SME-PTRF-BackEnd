from django.urls import reverse
from django.utils.html import escape, format_html, mark_safe
from sme_ptrf_apps.paa.models import (
    ReceitaPrevistaPaa,
    RecursoProprioPaa,
    ReceitaPrevistaPdde,
    PrioridadePaa,
    AtaPaa,
    DocumentoPaa,
    AtividadeEstatutariaPaa,
    ReceitaPrevistaOutroRecursoPeriodo
)


class PaaTabelasMixin:
    """Métodos readonly que renderizam registros relacionados ao PAA como tabelas HTML."""

    @staticmethod
    def _link(app_label, model_name, pk, label):
        url = reverse(f'admin:{app_label}_{model_name}_change', args=[pk])
        return format_html('<a href="{}">{}</a>', url, label)

    @staticmethod
    def _check_boolean(b):
        return '✓' if b else '✗'

    @staticmethod
    def _table(headers, rows):
        style_th = 'padding:4px 8px;text-align:left;background:#f8f8f8;border-bottom:1px solid #ccc'
        style_td = 'padding:4px 8px;border-bottom:1px solid #eee;vertical-align:top'
        ths = ''.join(f'<th style="{style_th}">{escape(h)}</th>' for h in headers)
        if rows:
            trs = ''
            for row in rows:
                cells = ''.join(
                    f'<td style="{style_td}">'
                    f'{c if hasattr(c, "__html__") else escape(str(c) if c is not None else "-")}'
                    f'</td>'
                    for c in row
                )
                trs += f'<tr>{cells}</tr>'
        else:
            trs = (
                f'<tr><td colspan="{len(headers)}" style="{style_td};color:#999">'
                f'Nenhum registro.</td></tr>'
            )
        return mark_safe(
            f'<div style="overflow-x:auto">'
            f'<table style="border-collapse:collapse;width:100%">'
            f'<thead><tr>{ths}</tr></thead><tbody>{trs}</tbody>'
            f'</table></div>'
        )

    def tabela_objetivos(self, obj):
        if not obj or not obj.pk:
            return self._table(['UUID', 'Nome', 'Status', 'Criado no PAA'], [])
        rows = [
            [
                self._link('paa', 'objetivopaa', item.pk, item.uuid),
                item.nome,
                item.get_status_display(),
                self._check_boolean(bool(item.paa_id)),
            ]
            for item in obj.objetivos.all()
        ]
        return self._table(['UUID', 'Nome', 'Status', 'Criado no PAA'], rows)
    tabela_objetivos.short_description = 'Objetivos'

    def tabela_atividades_estatutarias(self, obj):
        if not obj or not obj.pk:
            return self._table(['UUID', 'Atividade Estatutária', 'Data', 'Criada no PAA'], [])
        qs = AtividadeEstatutariaPaa.objects.filter(paa=obj).select_related('atividade_estatutaria')
        rows = [
            [
                self._link('paa', 'atividadeestatutariapaa', item.pk, item.uuid),
                str(item.atividade_estatutaria),
                item.data or '-',
                self._check_boolean(bool(item.atividade_estatutaria.paa_id)),
            ]
            for item in qs
        ]
        return self._table(['UUID', 'Atividade Estatutária', 'Data', 'Criada no PAA'], rows)
    tabela_atividades_estatutarias.short_description = 'Atividades Estatutárias'

    def tabela_receitas_ptrf(self, obj):
        if not obj or not obj.pk:
            return self._table([], [])
        headers = [
            'UUID', 'Ação Associação',
            'Saldo Custeio', 'Saldo Capital', 'Saldo Livre', 'Prev. Custeio', 'Prev. Capital', 'Prev. Livre']  # noqa
        rows = [
            [
                self._link('paa', 'receitaprevistapaa', item.pk, item.uuid),
                str(item.acao_associacao),
                item.saldo_congelado_custeio, item.saldo_congelado_capital, item.saldo_congelado_livre,
                item.previsao_valor_custeio, item.previsao_valor_capital, item.previsao_valor_livre,
            ]
            for item in ReceitaPrevistaPaa.objects.filter(paa=obj).select_related('acao_associacao')
        ]
        return self._table(headers, rows)
    tabela_receitas_ptrf.short_description = 'Receitas Previstas PTRF'

    def tabela_receitas_pdde(self, obj):
        if not obj or not obj.pk:
            return self._table([], [])
        headers = ['UUID', 'Ação PDDE', 'Saldo Custeio', 'Saldo Capital', 'Saldo Livre',
                   'Prev. Custeio', 'Prev. Capital', 'Prev. Livre']
        rows = [
            [
                self._link('paa', 'receitaprevistapdde', item.pk, item.uuid),
                str(item.acao_pdde),
                item.saldo_custeio, item.saldo_capital, item.saldo_livre,
                item.previsao_valor_custeio, item.previsao_valor_capital, item.previsao_valor_livre,
            ]
            for item in ReceitaPrevistaPdde.objects.filter(paa=obj).select_related('acao_pdde')
        ]
        return self._table(headers, rows)
    tabela_receitas_pdde.short_description = 'Receitas Previstas PDDE'

    def tabela_recursos_proprios(self, obj):
        if not obj or not obj.pk:
            return self._table([], [])
        headers = ['UUID', 'Fonte Recurso', 'Associação', 'Data Prevista', 'Descrição', 'Valor']
        rows = [
            [
                self._link('paa', 'recursopropriopaa', item.pk, item.uuid),
                str(item.fonte_recurso),
                str(item.associacao),
                item.data_prevista or '-',
                item.descricao or '-',
                item.valor,
            ]
            for item in RecursoProprioPaa.objects.filter(paa=obj).select_related('fonte_recurso', 'associacao')
        ]
        return self._table(headers, rows)
    tabela_recursos_proprios.short_description = 'Recursos Próprios'

    def tabela_outros_recursos_periodo(self, obj):
        if not obj or not obj.pk:
            return self._table([], [])
        headers = ['UUID', 'Outro Recurso (Período)', 'Saldo Custeio', 'Saldo Capital', 'Saldo Livre',
                   'Prev. Custeio', 'Prev. Capital', 'Prev. Livre']
        rows = [
            [
                self._link('paa', 'receitaprevistaoutrorecursoperiodo', item.pk, item.uuid),
                str(item.outro_recurso_periodo),
                item.saldo_custeio, item.saldo_capital, item.saldo_livre,
                item.previsao_valor_custeio, item.previsao_valor_capital, item.previsao_valor_livre,
            ]
            for item in ReceitaPrevistaOutroRecursoPeriodo.objects.filter(
                paa=obj).select_related('outro_recurso_periodo')
        ]
        return self._table(headers, rows)
    tabela_outros_recursos_periodo.short_description = 'Outros Recursos (Período)'

    def tabela_documentos(self, obj):
        if not obj or not obj.pk:
            return self._table([], [])
        headers = ['UUID', 'Status Geração', 'Versão', 'Versão Doc.', 'Retificação']
        rows = [
            [
                self._link('paa', 'documentopaa', item.pk, item.uuid),
                item.get_status_geracao_display() if hasattr(item, 'get_status_geracao_display') else item.status_geracao,  # noqa
                item.versao or '-',
                item.versao_documento or '-',
                self._check_boolean(item.retificacao),
            ]
            for item in DocumentoPaa.objects.filter(paa=obj)
        ]
        return self._table(headers, rows)
    tabela_documentos.short_description = 'Documentos'

    def tabela_atas(self, obj):
        if not obj or not obj.pk:
            return self._table([], [])
        headers = ['UUID', 'Tipo Ata', 'Status Geração PDF', 'Parecer Conselho', 'Prévia', 'Preenchida Em']
        rows = [
            [
                self._link('paa', 'atapaa', item.pk, item.uuid),
                item.get_tipo_ata_display() if hasattr(item, 'get_tipo_ata_display') else item.tipo_ata,
                item.status_geracao_pdf,
                item.parecer_conselho,
                self._check_boolean(item.previa),
                item.preenchida_em or '-',
            ]
            for item in AtaPaa.objects.filter(paa=obj)
        ]
        return self._table(headers, rows)
    tabela_atas.short_description = 'Atas'

    def tabela_prioridades(self, obj):
        if not obj or not obj.pk:
            return self._table([], [])
        headers = ['UUID', 'Prioridade', 'Recurso', 'Tipo Aplicação', 'Valor Total']
        rows = [
            [
                self._link('paa', 'prioridadepaa', item.pk, item.uuid),
                self._check_boolean(item.prioridade),
                item.recurso,
                item.tipo_aplicacao,
                item.valor_total,
            ]
            for item in PrioridadePaa.objects.filter(paa=obj)
        ]
        return self._table(headers, rows)
    tabela_prioridades.short_description = 'Prioridades'

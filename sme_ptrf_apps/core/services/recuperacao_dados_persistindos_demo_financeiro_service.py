from datetime import datetime

from sme_ptrf_apps.core.models import CategoriaDespesaChoices, InformacaoDespesaChoices, DemonstrativoFinanceiro


class RecuperaDadosDemoFinanceiro:

    def __init__(self, demonstrativo):
        self.demonstrativo = demonstrativo
        self.dados = demonstrativo.dados.first()
        self.dados_formatados = self.formata_dados()

    @staticmethod
    def formata_data(data):
        data_formatada = " - "
        if data:
            d = datetime.strptime(str(data), '%Y-%m-%d')
            data_formatada = d.strftime("%d/%m/%Y")

        return f'{data_formatada}'

    def retorna_dados_cabecalho(self):
        cabecalho = {
            "periodo_referencia": self.dados.periodo_referencia,
            "periodo_data_inicio": self.formata_data(self.dados.periodo_data_inicio),
            "periodo_data_fim": self.formata_data(self.dados.periodo_data_fim),
            "conta": self.dados.conta_associacao,
        }

        return cabecalho

    def retorna_dados_identificacao_apm(self):
        identificacao_apm = {
            "nome_associacao": self.dados.nome_associacao,
            "cnpj_associacao": self.dados.cnpj_associacao,
            "codigo_eol_associacao": self.dados.codigo_eol_associacao,
            "nome_dre_associacao": self.dados.nome_dre_associacao,
            "cargo_substituto_presidente_ausente": self.dados.cargo_substituto_presidente_ausente,
            "presidente_diretoria_executiva": self.dados.presidente_diretoria_executiva,
            "presidente_conselho_fiscal": self.dados.presidente_conselho_fiscal,
            "tipo_unidade": self.dados.tipo_unidade,
            "nome_unidade": self.dados.nome_unidade,
        }

        return identificacao_apm

    def retorna_identificacao_conta(self):
        identificacao_conta = {
            "banco": self.dados.banco,
            "agencia": self.dados.agencia,
            "conta": self.dados.conta,
            "data_extrato": self.dados.data_extrato.strftime("%d/%m/%Y") if self.dados.data_extrato else '',
            "saldo_extrato": self.dados.saldo_extrato,
            "encerrada_em": self.dados.conta_encerrada_em
        }

        return identificacao_conta

    def retorna_resumo_por_acao(self):
        lista_resumo = []

        for item in self.dados.itens_resumo_por_acao.exclude(total_geral=True):
            resumo_acao = {
                "acao_associacao": item.acao_associacao,
                "linha_custeio": {
                    "saldo_anterior": item.custeio_saldo_anterior,
                    "credito": item.custeio_credito,
                    "despesa_realizada": item.custeio_despesa_realizada,
                    "despesa_nao_realizada": item.custeio_despesa_nao_realizada,
                    "saldo_reprogramado_proximo": item.custeio_saldo_reprogramado_proximo,
                    "despesa_nao_demostrada_outros_periodos": item.custeio_despesa_nao_demostrada_outros_periodos,
                    "valor_saldo_bancario_custeio": item.custeio_valor_saldo_bancario_custeio,
                },
                "linha_livre": {
                    "saldo_anterior": item.livre_saldo_anterior,
                    "credito": item.livre_credito,
                    "saldo_reprogramado_proximo": item.livre_saldo_reprogramado_proximo,
                    "valor_saldo_reprogramado_proximo_periodo_livre": item.livre_valor_saldo_reprogramado_proximo_periodo,
                },
                "linha_capital": {
                    "saldo_anterior": item.capital_saldo_anterior,
                    "credito": item.capital_credito,
                    "despesa_realizada": item.capital_despesa_realizada,
                    "despesa_nao_realizada": item.capital_despesa_nao_realizada,
                    "saldo_reprogramado_proximo": item.capital_saldo_reprogramado_proximo,
                    "despesa_nao_demostrada_outros_periodos": item.capital_despesa_nao_demostrada_outros_periodos,
                    "valor_saldo_bancario_capital": item.capital_valor_saldo_bancario_capital,
                },
                "total_valores": item.total_valores,
                "saldo_bancario": item.saldo_bancario,
            }

            lista_resumo.append(resumo_acao)

        total_geral = self.dados.itens_resumo_por_acao.filter(total_geral=True).first()
        total_valores = {
            "saldo_anterior": {
                "C": total_geral.custeio_saldo_anterior,
                "L": total_geral.livre_saldo_anterior,
                "K": total_geral.capital_saldo_anterior
            },
            "credito": {
                "C": total_geral.custeio_credito,
                "L": total_geral.livre_credito,
                "K": total_geral.capital_credito,
            },
            "despesa_realizada": {
                "C": total_geral.custeio_despesa_realizada,
                "K": total_geral.capital_despesa_realizada
            },
            "despesa_nao_realizada": {
                "C": total_geral.custeio_despesa_nao_realizada,
                "K": total_geral.capital_despesa_nao_realizada
            },
            "saldo_reprogramado_proximo": {
                "C": total_geral.custeio_saldo_reprogramado_proximo,
                "L": total_geral.livre_saldo_reprogramado_proximo,
                "K": total_geral.capital_saldo_reprogramado_proximo
            },
            "despesa_nao_demostrada_outros_periodos": {
                "C": total_geral.custeio_despesa_nao_demostrada_outros_periodos,
                "K": total_geral.capital_despesa_nao_demostrada_outros_periodos
            },
            "valor_saldo_bancario": {
                "C": total_geral.custeio_valor_saldo_bancario_custeio,
                "K": total_geral.capital_valor_saldo_bancario_capital,
            },
            "total_valores": total_geral.total_valores,
            "saldo_bancario": total_geral.saldo_bancario,
        }

        resumo_por_acao = {
            "resumo_acoes": lista_resumo,
            "total_valores": total_valores
        }

        return resumo_por_acao

    def retorna_creditos_demonstrados(self):
        linhas = []

        for item in self.dados.itens_creditos.all():
            linha = {
                "tipo_receita": item.tipo_receita,
                "detalhamento": item.detalhamento,
                "nome_acao": item.nome_acao,
                "data": item.data.strftime("%d/%m/%Y") if item.data else '',
                "valor": item.valor
            }

            if item.receita_estornada:

                motivos_estorno = []
                for motivo in item.motivos_estorno.split("\r\n"):
                    if motivo:
                        motivos_estorno.append({
                            "motivo": motivo
                        })

                linha["estorno"] = {
                    "data_estorno": item.data_estorno.strftime("%d/%m/%Y") if item.data_estorno else '',
                    "numero_documento_despesa": item.numero_documento_despesa,
                    "motivos_estorno": motivos_estorno,
                    "outros_motivos_estorno": item.outros_motivos_estorno
                }

            linhas.append(linha)

        valor_total = self.dados.total_creditos

        creditos_demonstrados = {
            "linhas": linhas,
            "valor_total": valor_total
        }

        return creditos_demonstrados

    @staticmethod
    def retorna_dados_despesas(lista_despesas, valor_total):
        linhas = []

        for item in lista_despesas:
            linha = {
                "razao_social": item.razao_social if item.razao_social else "",
                "cnpj_cpf": item.cnpj_cpf,
                "tipo_documento": item.tipo_documento,
                "numero_documento": item.numero_documento if item.numero_documento else "",
                "nome_acao_documento": item.nome_acao_documento,
                "especificacao_material": item.especificacao_material,
                "tipo_despesa": item.tipo_despesa,
                "tipo_transacao": item.tipo_transacao,
                "data_documento": item.data_documento.strftime("%d/%m/%Y") if item.data_documento else '',
                "data_transacao": item.data_transacao.strftime("%d/%m/%Y") if item.data_transacao else '',
                "valor": item.valor,
            }

            if item.info_despesa == InformacaoDespesaChoices.GEROU_IMPOSTOS:
                linha["despesas_impostos"] = []

                for i in item.info_retencao_imposto.strip().split("\r\n"):
                    info_imposto = i.split(";")

                    if info_imposto and len(info_imposto) == 2:
                        valor_info = info_imposto[0]
                        data_transacao_info = info_imposto[1]

                        if data_transacao_info:
                            data_transacao = datetime.strptime(data_transacao_info, "%Y-%m-%d").date()
                            data_transacao = data_transacao.strftime("%d/%m/%Y")
                            info_pagamento = f'pago em {data_transacao}'
                        else:
                            info_pagamento = "pagamento ainda não realizado"

                        linha["despesas_impostos"].append({
                            "info_pagamento": info_pagamento,
                            "valor": valor_info
                        })

            if item.info_despesa == InformacaoDespesaChoices.IMPOSTO_GERADO:
                info_imposto_gerado = item.info_imposto_retido.strip().split(";")

                if info_imposto_gerado and len(info_imposto_gerado) == 3:
                    numero_documento_imposto_gerado = info_imposto_gerado[0]
                    data_transacao_imposto_gerado = info_imposto_gerado[1]
                    data_transacao_imposto_gerado = datetime.strptime(data_transacao_imposto_gerado, "%Y-%m-%d").date()
                    valor_imposto_gerado = info_imposto_gerado[2]

                    linha["despesa_geradora"] = {
                        "numero_documento": numero_documento_imposto_gerado if numero_documento_imposto_gerado else "",
                        "data_transacao": data_transacao_imposto_gerado.strftime(
                            "%d/%m/%Y") if data_transacao_imposto_gerado else "",
                        "valor": valor_imposto_gerado
                    }

            linhas.append(linha)

        despesas = {
            "linhas": linhas,
            "valor_total": valor_total
        }

        return despesas

    def retorna_despesas_demonstradas(self):
        lista_despesas = self.dados.itens_despesa.filter(
            categoria_despesa=CategoriaDespesaChoices.DEMONSTRADA).order_by('data_transacao', 'numero_documento')
        valor_total = self.dados.total_despesas_demonstradas

        despesas = self.retorna_dados_despesas(lista_despesas=lista_despesas, valor_total=valor_total)

        return despesas

    def retorna_despesas_nao_demonstradas(self):
        lista_despesas = self.dados.itens_despesa.filter(
            categoria_despesa=CategoriaDespesaChoices.NAO_DEMONSTRADA).order_by(
            'data_transacao', 'numero_documento')
        valor_total = self.dados.total_despesas_nao_demonstradas

        despesas = self.retorna_dados_despesas(lista_despesas=lista_despesas, valor_total=valor_total)

        return despesas

    def retorna_despesas_anteriores_nao_demonstradas(self):
        lista_despesas = self.dados.itens_despesa.filter(
            categoria_despesa=CategoriaDespesaChoices.NAO_DEMONSTRADA_PERIODO_ANTERIOR).order_by(
            'data_transacao', 'numero_documento')
        valor_total = self.dados.total_despesas_nao_demonstradas_periodos_anteriores

        despesas = self.retorna_dados_despesas(lista_despesas=lista_despesas, valor_total=valor_total)

        return despesas

    def retorna_justificativas_info_adicionais(self):
        justificativa = self.dados.justificativa_info_adicionais
        return justificativa

    def retorna_data_geracao(self):
        return self.dados.data_geracao.strftime("%d/%m/%Y") if self.dados.data_geracao else ''

    def retorna_texto_data_geracao_documento(self):
        return self.dados.texto_rodape

    def eh_previa(self):
        return self.demonstrativo.versao == DemonstrativoFinanceiro.VERSAO_PREVIA

    def formata_dados(self):
        dados_demonstrativo = {
            "cabecalho": self.retorna_dados_cabecalho(),
            "identificacao_apm": self.retorna_dados_identificacao_apm(),
            "identificacao_conta": self.retorna_identificacao_conta(),
            "resumo_por_acao": self.retorna_resumo_por_acao(),
            "creditos_demonstrados": self.retorna_creditos_demonstrados(),
            "despesas_demonstradas": self.retorna_despesas_demonstradas(),
            "despesas_nao_demonstradas": self.retorna_despesas_nao_demonstradas(),
            "despesas_anteriores_nao_demonstradas": self.retorna_despesas_anteriores_nao_demonstradas(),
            "justificativas": self.retorna_justificativas_info_adicionais(),
            "data_geracao_documento": self.retorna_texto_data_geracao_documento(),
            "data_geracao": self.retorna_data_geracao(),
            "previa": self.eh_previa()
        }

        return dados_demonstrativo

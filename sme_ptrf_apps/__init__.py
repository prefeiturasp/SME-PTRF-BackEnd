__version__ = "1.22.0"

__version_info__ = tuple(
    [
        int(num) if num.isdigit() else num
        for num in __version__.replace("-", ".", 1).split(".")
    ]
)


"""

            19-Saldo parcial próximo    (C): linha_custeio.valor_saldo_bancario_custeio
                                        (K): linha_capital.valor_saldo_bancario_capital
                                        (L): linha_livre.saldo_reprogramado_proximo  (mesmo da coluna 17)
                                        (T): saldo_bancario
                                        (*): 16+17+18


            16-Despesas Ñ Demonstradas  (C): linha_custeio.despesa_nao_realizada  (despesa_nao_realizada)
                                        (K): linha_capital.despesa_nao_realizada
                                        (L): XXXXX Não tem

            17-Saldo próximo período    (C): linha_custeio.saldo_reprogramado_proximo (saldo_reprogramado_proximo)
                                        (K): linha_capital.saldo_reprogramado_proximo
                                        (L): linha_livre.saldo_reprogramado_proximo
                                        (T): total_valores
                                        (*): 13+14-15-16

            18-Despesas Ñ Demonstr.Ant. (C): linha_custeio.despesa_nao_demostrada_outros_periodos (despesa_nao_demostrada_outros_periodos)
                                        (K): linha_capital.despesa_nao_demostrada_outros_periodos
                                        (L): XXXXX Não tem

"""

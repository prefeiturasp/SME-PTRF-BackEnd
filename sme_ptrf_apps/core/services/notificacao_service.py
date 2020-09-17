from datetime import date

def formata_data(data):
    meses = ('Jan.', 'Fev.', 'Mar.', 'Abr.', 'Mai.', 'Jun.', 'Jul.', 'Ago.', 'Set.', 'Out.', 'Nov.', 'Dez.')
    diasemana = ('Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo')
    ds = diasemana[date.weekday(data)] if data != date.today() else 'Hoje'
    ms = meses[data.month-1]

    return f"{ds} {data.day:0>2} {ms} {data.year}"
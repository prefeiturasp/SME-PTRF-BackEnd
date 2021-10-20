numeros_ordinais = {
        1: "Primeira",
        2: "Segunda",
        3: "Terceira",
        4: "Quarta",
        5: "Quinta",
        6: "Sexta",
        7: "Sétima",
        8: "Oitava",
        9: "Nona",
        10: "Décima",
        20: "Vigésima",
        30: "Trigésima",
        40: "Quadragésima"
    }


def formata_numero_ordinal(numero):
    if numero >= 50:
        raise Exception("A conversão para numeros ordinais só foi realizada até o número 49")

    try:
        if numero < 10:
            return numeros_ordinais[numero]
        elif numero >= 10 and numero <= 19:
            if numero == 10:
                return numeros_ordinais[numero]

            numero_str = str(numero)
            ultimo_numero = int(numero_str[1])
            numero_ordinal = numeros_ordinais[10] + " " + numeros_ordinais[ultimo_numero].lower()
            return numero_ordinal

        elif numero >= 20 and numero <= 29:
            if numero == 20:
                return numeros_ordinais[numero]

            numero_str = str(numero)
            ultimo_numero = int(numero_str[1])
            numero_ordinal = numeros_ordinais[20] + " " + numeros_ordinais[ultimo_numero].lower()
            return numero_ordinal

        elif numero >= 30 and numero <=39:
            if numero == 30:
                return numeros_ordinais[numero]

            numero_str = str(numero)
            ultimo_numero = int(numero_str[1])
            numero_ordinal = numeros_ordinais[30] + " " + numeros_ordinais[ultimo_numero].lower()
            return numero_ordinal

        elif numero >= 40 and numero <=49:
            if numero == 40:
                return numeros_ordinais[numero]

            numero_str = str(numero)
            ultimo_numero = int(numero_str[1])
            numero_ordinal = numeros_ordinais[40] + " " + numeros_ordinais[ultimo_numero].lower()
            return numero_ordinal
    except Exception as e:
        return f"ocorreu um erro: {e}"

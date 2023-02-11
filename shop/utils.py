import datetime


def gerar_code_carrinho():
    agora = datetime.datetime.now()
    dia = agora.day
    mes = agora.month
    ano = agora.year
    hora = agora.hour
    minuto = agora.minute
    segundo = agora.second
    code_proposto = "{}{}{}/{}{}{}".format(ano, mes, dia, hora, minuto, segundo)
    return code_proposto


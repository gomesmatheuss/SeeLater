import hashlib
import re
import datetime
from typing import Union

def hash_video_url(url):
    return hashlib.md5(url.encode()).hexdigest()

def get_yt_url_code(url):
    url_code = re.findall(r'\?v=(.*?)$', url)
    return url_code[0] if url_code else None

def format_timestamp(timestamp: Union[float, datetime.datetime]) -> str:
    if isinstance(timestamp, (int, float)):
        timestamp = datetime.datetime.fromtimestamp(timestamp)
    
    agora = datetime.datetime.now()
    diferenca = agora - timestamp if agora > timestamp else timestamp - agora
    
    segundos = int(diferenca.total_seconds())
    minutos = segundos // 60
    horas = minutos // 60
    dias = horas // 24
    semanas = dias // 7
    meses = dias // 30
    anos = dias // 365
    
    if segundos < 60:
        return "agora mesmo" if segundos < 10 else f"há {segundos} segundos"
    elif minutos < 60:
        return f"há {minutos} minuto{'s' if minutos > 1 else ''}"
    elif horas < 24:
        return f"há {horas} hora{'s' if horas > 1 else ''}"
    elif dias < 7:
        return f"há {dias} dia{'s' if dias > 1 else ''}"
    elif semanas < 4:
        return f"há {semanas} semana{'s' if semanas > 1 else ''}"
    elif meses < 12:
        return f"há {meses} {'meses' if meses > 1 else 'mês'}"
    else:
        return f"há {anos} ano{'s' if anos > 1 else ''}"

def format_view_count(view_count: int) -> str:
    """
    Formata a quantidade de visualizações seguindo um formato
    semelhante ao utilizado pelo YouTube.

    Regras:

    0 - 99.999
        Número completo com separador de milhar.

    100.000 - 999.999
        Número inteiro + "mil".

    1.000.000 - 999.999.999
        Milhões com até uma casa decimal + "M".

    1.000.000.000+
        Bilhões com até uma casa decimal + "B".
    """

    if view_count is None:
        return "0"

    view_count = int(view_count)

    # 0 - 99.999
    if view_count < 100_000:
        return f"{view_count:,}".replace(",", ".")

    # 100.000 - 999.999
    if view_count < 1_000_000:
        thousands = view_count // 1_000
        return f"{thousands}mil"

    # 1.000.000 - 999.999.999
    if view_count < 1_000_000_000:
        millions = view_count / 1_000_000

        if millions.is_integer():
            return f"{int(millions)}M"

        return f"{millions:.1f}M".replace(".", ",")

    # 1.000.000.000+
    billions = view_count / 1_000_000_000

    if billions.is_integer():
        return f"{int(billions)}B"

    return f"{billions:.1f}B".replace(".", ",")

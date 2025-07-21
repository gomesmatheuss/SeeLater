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

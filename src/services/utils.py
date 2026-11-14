import hashlib
import re
import datetime
from typing import Union
from urllib.parse import urlparse, parse_qs

def hash_video_url(url):
    return hashlib.md5(url.encode()).hexdigest()

def get_yt_url_code(url):
    if not isinstance(url, str) or not url.strip():
        return None

    url = url.strip()

    # Permite URLs sem protocolo explícito.
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        parsed_url = urlparse(url)
        hostname = (parsed_url.hostname or "").lower()

        # Formato: youtube.com/watch?v=ID
        if hostname in ("youtube.com", "www.youtube.com", "m.youtube.com"):
            if parsed_url.path != "/watch":
                return None

            video_id = parse_qs(parsed_url.query).get("v", [None])[0]

        # Formato: youtu.be/ID
        elif hostname == "youtu.be":
            video_id = parsed_url.path.strip("/").split("/")[0]

        else:
            return None

        # IDs de vídeos do YouTube possuem 11 caracteres.
        if video_id and re.fullmatch(r"[a-zA-Z0-9_-]{11}", video_id):
            return video_id

    except (ValueError, AttributeError):
        pass

    return None

def format_timestamp(timestamp: Union[float, datetime.datetime]) -> str:

    if timestamp is None:
        return "Data não disponível"

    if isinstance(timestamp, (int, float)):
        timestamp = datetime.datetime.fromtimestamp(timestamp)

    if not isinstance(timestamp, datetime.datetime):
        return "Data não disponível"

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

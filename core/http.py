import requests


_SESSION = None


def get_http_session() -> requests.Session:
    global _SESSION

    if _SESSION is None:
        session = requests.Session()
        session.headers.update({"User-Agent": "LUMA-Orion-Agent/1.0"})
        _SESSION = session

    return _SESSION

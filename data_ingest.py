# data_ingest.py
"""
Módulo para ingesta de datos desde API-Football (v3) con soporte de partidos en directo.
Ahora recibe la API key como parámetro para no depender de variables de entorno.
"""
import requests

BASE_URL = "https://v3.football.api-sports.io"

def _get(endpoint: str, params: dict = None, api_key: str = None) -> list:
    """
    Llama al endpoint de API-Football y devuelve la parte 'response'.
    """
    if not api_key:
        raise ValueError(
            "Falta la API Key de API-Football.\n"
            "Pásala como argumento a la función (desde Streamlit)."
        )
    headers = {
        "x-apisports-key": api_key,
        "Accept": "application/json"
    }
    url = f"{BASE_URL}{endpoint}"
    resp = requests.get(url, headers=headers, params=params or {})
    resp.raise_for_status()
    data = resp.json()
    if data.get("errors"):
        raise ValueError(f"Error API-Football: {data['errors']}")
    return data.get("response", [])

def fetch_live_fixtures(api_key: str) -> list:
    """
    Obtiene todos los partidos que están 'live' en este momento.
    """
    return _get("/fixtures", {"live": "all"}, api_key)

def fetch_upcoming_fixtures(league_id: int, season: int, api_key: str) -> list:
    """
    Obtiene los próximos fixtures para una liga y temporada dada.
    """
    params = {"league": league_id, "season": season}
    return _get("/fixtures", params, api_key)

def fetch_odds_for_fixture(fixture_id: int, api_key: str, bookmaker: str = None) -> list:
    """
    Obtiene cuotas para un fixture específico.
    """
    params = {"fixture": fixture_id}
    if bookmaker:
        params["bookmaker"] = bookmaker
    return _get("/odds", params, api_key)


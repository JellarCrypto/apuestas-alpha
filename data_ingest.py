# data_ingest.py
"""
Módulo para ingesta de datos desde API-Football (v3) vía RapidAPI, con soporte live.
Recibe la API Key de RapidAPI y usa los headers x-rapidapi-key/host.
"""
import requests

BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"

def _get(endpoint: str, params: dict = None, api_key: str = None) -> list:
    """
    Llama al endpoint de RapidAPI para API-Football y devuelve el 'response'.
    """
    if not api_key:
        raise ValueError(
            "Falta la API Key de RapidAPI.\n"
            "Pásala como argumento a la función (desde Streamlit)."
        )
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    url = f"{BASE_URL}{endpoint}"
    resp = requests.get(url, headers=headers, params=params or {})
    resp.raise_for_status()
    data = resp.json()
    # En RapidAPI el JSON viene en data['response']
    if data.get("errors"):
        raise ValueError(f"Error API-Football: {data['errors']}")
    return data["response"]

def fetch_live_fixtures(api_key: str) -> list:
    """
    Obtiene todos los partidos que están 'live' en este momento.
    """
    return _get("/fixtures", {"live": "all"}, api_key)

def fetch_upcoming_fixtures(league_id: int, season: int, api_key: str) -> list:
    """
    Obtiene los próximos fixtures para una liga y temporada dada.
    """
    return _get("/fixtures", {"league": league_id, "season": season}, api_key)

def fetch_odds_for_fixture(fixture_id: int, api_key: str, bookmaker: str = None) -> list:
    """
    Obtiene cuotas para un fixture específico.
    """
    params = {"fixture": fixture_id}
    if bookmaker:
        params["bookmaker"] = bookmaker
    return _get("/odds", params, api_key)

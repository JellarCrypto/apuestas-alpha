# data_ingest.py
"""
Módulo para ingesta de datos desde API-Football (v3) con soporte de partidos en directo.
Lee la API Key dinámicamente en cada petición para asegurar que se capta el valor inyectado en runtime.
"""
import os
import requests

BASE_URL = "https://v3.football.api-sports.io"

def _get(endpoint: str, params: dict = None) -> list:
    """
    Llama al endpoint de API-Football y devuelve la parte 'response'.
    """
    # Leer la API Key justo antes de cada petición
    api_key = os.getenv("API_FOOTBALL_KEY")
    if not api_key:
        raise ValueError(
            "Falta la API_KEY de API-Football.\n"
            "Define API_FOOTBALL_KEY inyectando en el sidebar antes de ejecutar las consultas."
        )
    headers = {
        "x-apisports-key": api_key,
        "Accept": "application/json"
    }

    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, headers=headers, params=params or {})
    response.raise_for_status()
    data = response.json()
    if data.get("errors"):
        raise ValueError(f"Error API-Football: {data['errors']}")
    return data.get("response", [])

def fetch_live_fixtures() -> list:
    """
    Obtiene todos los partidos que están 'live' en este momento.
    """
    return _get("/fixtures", {"live": "all"})

def fetch_upcoming_fixtures(league_id: int, season: int = None) -> list:
    """
    Obtiene los próximos fixtures para una liga y temporada dada.
    """
    params = {"league": league_id}
    if season is not None:
        params["season"] = season
    return _get("/fixtures", params)

def fetch_odds_for_fixture(fixture_id: int, bookmaker: str = None) -> list:
    """
    Obtiene cuotas para un fixture específico.
    """
    params = {"fixture": fixture_id}
    if bookmaker:
        params["bookmaker"] = bookmaker
    return _get("/odds", params)


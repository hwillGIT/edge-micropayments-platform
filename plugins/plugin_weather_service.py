import requests
import json
from typing import Dict, Any, Optional
from empic_sdk.device_sim.abstract import BaseDataGenerator


"""
WeatherService: Example `DataGenerator` implementation for IoT data.

This provider demonstrates how to extend ``BaseDataGenerator``:
    • Override `collect()` to implement **how** to fetch the raw data.  
    • Optionally override `process()` to normalize/augment that data.  
    • Do **not** handle retries, backoff, caching, or requester delivery yourself —
      those are managed by ``BaseDataGenerator``.
"""
class PluginWeatherService(BaseDataGenerator):

    # Architectural role:
    #     Initializes service-specific configuration and ensures the base
    #     class sets up retry/backoff, caching, and delivery.
    #
    # Implementation detail (WeatherService):
    #     Stores `latitude` and `longitude` (coming from `params` in the
    #     JSON config, passed in as **kwargs) for use when calling the
    #     Open-Meteo API.
    def __init__(self, config: dict, **kwargs):
        super().__init__(config, **kwargs)
        self.latitude = float(kwargs.get("latitude", 0.0))
        self.longitude = float(kwargs.get("longitude", 0.0))

    # Architectural role:
    #     Required hook. Called by ``BaseDataGenerator.produce(request_params)``
    #     whenever the backoff window allows. Should perform exactly one
    #     fetch of raw data from the provider’s source.
    #
    # Implementation detail (WeatherService):
    #     Builds a request URL for the Open-Meteo API using either the default
    #     configured lat/lon or request-specific overrides if provided, then
    #     returns the `current_weather` object from the API JSON.
    def collect(self, request_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        lat = float(request_params.get("lat", self.latitude)) if request_params else self.latitude
        lon = float(request_params.get("lon", self.longitude)) if request_params else self.longitude

        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}&current_weather=true"
        )
        resp = requests.get(url, timeout=(3.0, 8.0))
        resp.raise_for_status()
        return resp.json().get("current_weather") or {}

    # Architectural role:
    #     Optional hook. `BaseDataGenerator.produce()` passes the raw data
    #     here for transformation before caching and delivery. Subclasses
    #     override this to normalize or enrich their raw data.
    #
    # Implementation detail (WeatherService):
    #     Converts Celsius temperature to Fahrenheit and flattens the
    #     Open-Meteo payload to expose only selected fields in a
    #     user-friendly format.
    def process(self, raw: Dict[str, Any], request_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not raw:
            return {}
        temp_c = raw.get("temperature")
        return {
            "temperature_c": temp_c,
            "temperature_f": (temp_c * 9 / 5 + 32) if temp_c is not None else None,
            "windspeed_kmh": raw.get("windspeed"),
            "winddirection_deg": raw.get("winddirection"),
            "timestamp": raw.get("time"),
        }


# ----------------------------------------------------------------------
# Standalone demo usage (for developers testing outside the framework)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    cfg = {"latitude": 40.7128, "longitude": -74.0060}
    service = WeatherService(cfg)

    # Call produce() directly (this will invoke collect() + process()
    # and apply base retry/backoff/caching).
    snapshot = service.produce()
    print(json.dumps(snapshot, indent=2))

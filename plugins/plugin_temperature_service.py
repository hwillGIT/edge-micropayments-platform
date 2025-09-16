import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional
from empic_sdk.device_sim.abstract import BaseDataGenerator
from empic_sdk.device_sim.logic.temperature_sensor import TemperatureSensor

"""
TemperatureService: Example `DataGenerator` implementation for IoT data.

This provider demonstrates how to extend ``BaseDataGenerator``:
    • Override `collect()` to implement **how** to fetch the raw data.  
    • Optionally override `process()` to normalize/augment that data.  
    • Do **not** handle retries, backoff, caching, or requester delivery yourself —
      those are managed by ``BaseDataGenerator``.
"""
class PluginTemperatureService(BaseDataGenerator):

    # Architectural role:
    #     Initializes service-specific configuration and ensures the base
    #     class sets up retry/backoff, caching, and delivery.
    #
    # Implementation detail (PluginTemperatureService):
    #     Simple no-parameter system
    def __init__(self, config: dict, **kwargs):
        super().__init__(config, **kwargs)

    # Architectural role:
    #     Required hook. Called by ``BaseDataGenerator.produce(request_params)``
    #     whenever the backoff window allows. Should perform exactly one
    #     fetch of raw data from the provider’s source.
    #
    # Implementation detail (PluginTemperatureService):
    #     Read data from the temperature sensor
    def collect(self, request_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        temp = TemperatureSensor.read_temperature()
        now = datetime.now()
        current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")

        payload = {
            "temperature": temp,
            "time": current_time_str,
        }
        return payload


    # Architectural role:
    #     Optional hook. `BaseDataGenerator.produce()` passes the raw data
    #     here for transformation before caching and delivery. Subclasses
    #     override this to normalize or enrich their raw data.
    #
    # Implementation detail (PluginTemperatureService):
    #     Converts Celsius temperature to Fahrenheit
    def process(self, raw: Dict[str, Any], request_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not raw:
            return {}
        temp_c = raw.get("temperature")
        return {
            "temperature_c": temp_c,
            "temperature_f": (temp_c * 9 / 5 + 32) if temp_c is not None else None,
            "timestamp": raw.get("time"),
        }

# ----------------------------------------------------------------------
# Standalone demo usage (for developers testing outside the framework)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    cfg = {}
    service = PluginTemperatureService(cfg)

    # Call produce() directly (this will invoke collect() + process()
    # and apply base retry/backoff/caching).
    snapshot = service.produce()
    print(json.dumps(snapshot, indent=2))

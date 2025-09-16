from typing import Dict, Any
import json
import logging

from geopy.geocoders import Nominatim

from empic_sdk.device_sim.abstract import DataConsumer
from empic_sdk.device_sim.device_base import DeviceBase

logger = logging.getLogger(__name__)

class PluginWeatherConsumer(DataConsumer):
    """

    This is a custom plugin implementation. To run, invoke from the root of your project directory:
        python -m empic_sdk.device_sim.device_manager ./plugins/configs/plugin_weather_consumer.json

    New custom Consumers and Generators can be added to the plugins directory or a standalone 
    directory of your choosing. In the latter case, run as above, but with a path that resolves to your 
    json configuration file.

    Example `DataConsumer` that subscribes to services tagged as "weather".

    Architectural role:
        • Chooses providers to interact with based on their advertised tags/price.  
        • Supplies request-time parameters (via `get_request_params()`), which
          the framework forwards to the provider’s `collect()` / `process()`.  
        • Validates whether delivered data meets SLA/quality requirements.  
        • Handles the delivered data (e.g., logging, visualization, storage).  

    Implementation detail (WeatherConsumer):
        - Selects the cheapest weather provider under 0.50 USDC.  
        - Requests weather for New York City by default.  
        - Accepts only non-negative temperatures.  
        - Logs the received weather snapshot.
    """

    # Architectural role:
    #     Declares the type of service this consumer is interested in.
    # Implementation detail:
    #     Targets providers registered with the "weather" tag.
    service_tag = "weather"

    # Architectural role:
    #     Decide which provider(s) to request from among the registry candidates.
    # Implementation detail:
    #     Filters out providers charging more than 0.50 USDC and selects
    #     the cheapest eligible weather service.
    def select_services(self, candidates: list[dict]) -> list[str]:
        if not candidates:
            return []

        max_price = DeviceBase.usdc_to_base(0.50)
        eligible = [
            svc for svc in candidates
            if svc.get("price_usdc", DeviceBase.USDC_INVALID_PRICE) <= max_price
        ]
        if not eligible:
            return []

        cheapest = min(eligible, key=lambda s: s["price_usdc"])
        return [cheapest["service_id"]]

    # Architectural role:
    #     Provide request-time parameters to be included in the escrow request.
    #     These values will be passed into the provider’s `collect()` method.
    # Implementation detail:
    #     For demo purposes, always request weather data for New York City.
    #     Capture and return the request parameters from the config.
    #     Stores them in self.request_params for later use.
    def get_request_params(self) -> Dict[str, Any]:
        """
        Provide request-time parameters to be included in the escrow request.
        By default, returns the `request_params` found in the device config.
        Override here if WeatherConsumer needs custom logic.
        """
        request_params = super().get_request_params()
        logger.info(request_params)
        return request_params

    # Architectural role:
    #     Handle the final payload delivered from the provider after escrow release.
    # Implementation detail:
    #     Logs the processed weather data from the `"data"` field of the payload.
    def consume(self, service_data: dict) -> None:
        weather = service_data.get("data", {})
        logger.info("********************************")
        logger.info("Received weather update:")
        logger.info(json.dumps(weather, indent=2))
        logger.info("********************************")

    # Architectural role:
    #     Determine whether delivered data meets SLA/quality requirements.
    # Implementation detail:
    #     Valid if `temperature_c` exists in the provider’s `"data"` payload
    #     and is >= 0 °C.
    def _is_data_acceptable(self, service_data: dict) -> bool:
        temp_c = service_data.get("temperature_c")
        if temp_c is None:
            logger.info("temp_c missing in response", "service_data", service_data)
            return False
        valid = temp_c >= 0
        if not valid:
            logger.info("invalid temp_c value in response")

        return valid

    # Architectural role:
    #     Optional async hook for reacting to accepted data (e.g. storing,
    #     forwarding, visualizing). Called by the framework after successful
    #     escrow release.
    # Implementation detail:
    #     For demo purposes, pretty-prints the delivered weather snapshot.
    async def handle_data(self, service_data: dict):
        """
        Called after data is accepted. Logs weather data with location info.
        """
        weather = service_data.get("data", {}).copy()  # copy so we don’t mutate original
        weather["station"] = self.device.device_id

        logger.info("********************************")
        logger.info(json.dumps(weather, indent=2))
        logger.info("********************************")
from typing import Dict, Any
import json
import logging

from empic_sdk.device_sim.abstract import DataConsumer
from empic_sdk.device_sim.device_base import DeviceBase

logger = logging.getLogger(__name__)

class PluginTemperatureConsumer(DataConsumer):
    """

    This is a custom plugin implementation. To run, invoke from the root of your project directory:
        python -m empic_sdk.device_sim.device_manager ./plugins/configs/temperature_consumer.json

    New custom Consumers and Generators can be added to the plugins directory or a standalone 
    directory of your choosing. In the latter case, run as above, but with a path that resolves to your 
    json configuration file.

    Example `DataConsumer` that subscribes to services tagged as "temperature".

    Architectural role:
        • Chooses providers to interact with based on their advertised tags/price.  
        • Supplies request-time parameters (via `get_request_params()`), which
          the framework forwards to the provider’s `collect()` / `process()`.  
        • Validates whether delivered data meets SLA/quality requirements.  
        • Handles the delivered data (e.g., logging, visualization, storage).  

    Implementation detail (PluginTemperatureConsumer):
        - Selects the cheapest temperature provider under 0.50 USDC.  
        - Requests the temperature data  
        - Accepts only non-negative temperatures.  
        - Logs the received temperature snapshot.
    """

    # Architectural role:
    #     Declares the type of service this consumer is interested in.
    # Implementation detail:
    #     Targets providers registered with the "temperature" tag.
    service_tag = "temperature"

    # Architectural role:
    #     Decide which provider(s) to request from among the registry candidates.
    # Implementation detail:
    #     Filters providers with the desired delivery_mode (pubsub vs. pull), 
    #     excludes those charging more than 0.50 USDC and selects
    #     the cheapest eligible temperature sensor service.
    def select_services(self, candidates: list[dict]) -> list[str]:
            if not candidates:
                return []

            # read the preferred delivery mode from device config (default: "pull")
            preferred_mode = getattr(self.device, "delivery_mode", None) \
                or self.device.cfg.get("delivery_mode", "pull")

            # keep price filter (<= $0.50)
            max_price = DeviceBase.usdc_to_base(0.50)
            eligible = []
            for svc in candidates:
                price_ok = svc.get("price_usdc", DeviceBase.USDC_INVALID_PRICE) <= max_price
                modes = set((svc.get("delivery_modes") or []))
                mode_ok = (preferred_mode in modes) if modes else (preferred_mode == "pull")
                tag_ok = self.service_tag in (svc.get("tags") or [])
                if price_ok and mode_ok and tag_ok:
                    eligible.append(svc)

            if not eligible:
                return []

            cheapest = min(eligible, key=lambda s: s["price_usdc"])
            return [cheapest["service_id"]]

    # Architectural role:
    #     Provide request-time parameters to be included in the escrow request.
    #     These values will be passed into the provider’s `collect()` method.
    # Implementation detail:
    #     For demo purposes, requests temperature data from a temperature service
    #     Capture and return the request parameters from the config.
    #     Stores them in self.request_params for later use.
    def get_request_params(self) -> Dict[str, Any]:
        """
        Provide request-time parameters to be included in the escrow request.
        By default, returns the `request_params` found in the device config.
        Override here if PluginTemperatureConsumer needs custom logic.
        """
        return super().get_request_params()

    # Architectural role:
    #     Handle the final payload delivered from the provider after escrow release.
    # Implementation detail:
    #     Logs the processed temperature data from the `"data"` field of the payload.
    def consume(self, service_data: dict) -> None:
        temperature = service_data.get("data", {})
        logger.info("********************************")
        logger.info("Received temperature update:")
        logger.info(json.dumps(temperature, indent=2))
        logger.info("********************************")

    # Architectural role:
    #     Determine whether delivered data meets SLA/quality requirements.
    # Implementation detail:
    #     Valid if `temperature_c` exists in the provider’s `"data"` payload
    #     and is within range of normal human body temperature.
    def _is_data_acceptable(self, service_data: dict) -> bool:
        temperature_c = service_data.get("temperature_c")
        if temperature_c is None:
            logger.info("[%s] temperature_c missing in data: %s", self.device.device_id, service_data)
            return False
        valid = temperature_c >= 25.0 and temperature_c < 43.0
        if not valid:
            logger.info("[%s] invalid temperature_c value in data", self.device.device_id)
        return valid

    # Architectural role:
    #     Optional async hook for reacting to accepted data (e.g. storing,
    #     forwarding, visualizing). Called by the framework after successful
    #     escrow release.
    # Implementation detail:
    #     For demo purposes, pretty-prints the delivered temperature snapshot.
    async def handle_data(self, service_data: dict):
        """
        Called after data is accepted. Logs temperature data with timestamp.
        """
        temperature = service_data.get("data", {}).copy()  # copy so we don’t mutate original
        
        temperature["sensor_id"] = self.device.device_id
        temperature["escrow_id"] = service_data["escrow_id"]

        logger.info("********************************")
        logger.info(json.dumps(temperature, indent=2))
        logger.info("********************************")

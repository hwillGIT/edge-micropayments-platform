# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Commands

**Running Services and Consumers:**
```bash
# Run weather consumer
python -m empic_sdk.device_sim.device_manager plugins/configs/plugin_weather_consumer.json
# OR
./plugins/bin/run_custom_weather_consumer.sh

# Run weather service
python -m empic_sdk.device_sim.device_manager plugins/configs/plugin_weather_service.json
# OR
./plugins/bin/run_custom_weather_service.sh

# Run temperature consumer
python -m empic_sdk.device_sim.device_manager plugins/configs/plugin_temperature_consumer.json
# OR
./plugins/bin/run_custom_temperature_consumer.sh

# Run temperature service
python -m empic_sdk.device_sim.device_manager plugins/configs/plugin_temperature_service.json
# OR
./plugins/bin/run_custom_temperature_service.sh
```

**Package Installation:**
```bash
# Install/reinstall EMPIC SDK
pip uninstall empic-sdk
python -m pip install --force-reinstall empic_sdk-<version>-py3-none-any.whl

# Install/reinstall Python utilities
pip uninstall -y python-util
python -m pip install --force-reinstall python_util-<version>-py3-none-any.whl

# Install dependencies
pip install -r requirements.txt
```

**Debugging:**
- VSCode launch configurations are available in `.vscode/launch.json`
- Set `debugpy_port` in plugin configuration JSON files for remote debugging
- Each service/consumer needs unique `port` and `debugpy_port` values

## High-level Architecture

### EMPIC SDK Overview
The EMPIC SDK implements a Layer 3 micropayment protocol for IoT device interactions using escrow-protected stablecoin payments. The system follows this workflow:

1. **Registration**: Devices authenticate using SERVICE_API_KEY from EMPIC portal
2. **Service Discovery**: Consumers query registry for providers by service_tag
3. **Escrow Creation**: Consumer deposits USDC into escrow smart contract
4. **Data Exchange**: Providers deliver data via pull or pubsub modes
5. **Settlement**: Valid data triggers escrow release to provider

### Plugin Architecture

The SDK uses a plugin-based architecture where:

- **Data Consumers** (`DataConsumer` base class):
  - Select providers from registry based on price/criteria
  - Supply request parameters
  - Validate received data against SLA
  - Handle accepted data

- **Data Generators/Services** (`BaseDataGenerator` base class):
  - Implement `collect()` to fetch raw data
  - Optionally implement `process()` to transform data
  - Framework handles retry, backoff, caching, and delivery

### Configuration System

Each plugin has two components:
1. **Python implementation** (`plugins/*.py`): Business logic
2. **JSON configuration** (`plugins/configs/*.json`): Device-specific settings

Key configuration fields:
- `SERVICE_API_KEY`: Authentication key (or use .env file)
- `port`: HTTP server port (must be unique)
- `debugpy_port`: Debug port (must be unique)
- `signing_url`: Public URL for transaction signing
- `data_receipt_url`: Public URL for data receipt
- `wallets`: Blockchain wallet configuration
- `funding_mode`: "auto_fill" (dev) or "notify_low_funds" (prod)

### Device Manager

The central orchestrator `empic_sdk.device_sim.device_manager` loads configuration and instantiates the appropriate plugin class specified in the `class` field of consumer/generator configuration.

### Key Dependencies

- **Web3/Ethereum**: `web3`, `eth-account` for blockchain interactions
- **Async/Network**: `aiohttp`, `httpx`, `fastapi`, `uvicorn`
- **MQTT**: `aiomqtt`, `paho-mqtt` for pubsub delivery mode
- **Location**: `geopy` for geocoding services

## 📋 Configuration

### Service Configuration (`plugins/configs/`)
- **Weather Service** (Port 9085): IoT weather data provider
- **Temperature Service** (Port 9086): IoT temperature data provider  
- **Weather Consumer** (Port 9074): Weather data consumer client
- **Temperature Consumer** (Port 9087): Temperature data consumer client

**Key Settings:**
- API Key: `SERVICE_API_KEY` in `.env`
- Email notifications: `hubertwilliams@hotmail.com`
- **NEW: Delivery-Mode Specific Pricing:**
  - Pull mode: $0.01 per pull event
  - Pubsub mode: $0.40 per escrow event (subscription duration)
- **NEW: Cadence Support:** `cadence_sec` parameter for pull delivery periodicity
- Discovery intervals: 5 seconds (optimized)
- Large funding: 10,000 USDC initial balance

### Enhanced Pricing Model
```json
"pricing": {
  "pull": {
    "price_usdc": 0.01,
    "billing_model": "per_pull_event"
  },
  "pubsub": {
    "price_usdc": 0.40,
    "billing_model": "per_escrow_event"
  }
}
```

### Pull Cadence Configuration
```json
"consumers": [{
  "delivery_mode": "pull",
  "cadence_sec": 30,
  "class": "plugins.plugin_consumer.PluginConsumer"
}]
```

## 🔧 Recent Updates

### Delivery-Mode Specific Pricing (NEW)
- Services now support different pricing for pull vs pubsub delivery modes
- Pull mode: Charged per individual pull request event
- Pubsub mode: Charged per escrow event for the entire subscription duration

### Pull Cadence Support (NEW)
- Added `cadence_sec` parameter to consumer configurations
- Dictates the periodicity of pull requests when using pull delivery mode
- Default value: 30 seconds

### Multiprocessing Fix
- Resolved Python 3.13 + Windows + FastAPI compatibility issue
- Solution: Use WSL Linux with fork() multiprocessing
- Added wrapper scripts with proper multiprocessing setup

### Escrow ID Patch
- Implemented client-side escrow ID generation as fallback
- Handles server-side empty escrow_id responses
- Maintains proper MQTT topic format: `empic/{provider}/{service}/{escrow_id}`
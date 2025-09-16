# EMPIC SDK – Getting Started

Welcome to the **EMPIC SDK**. This package provides developers with the tools to experiment with **Edge Micropayments Platform for Integrated Commerce (EMPIC)**. It includes device simulation, escrow flows, and a set of plugins for building and testing micropayment-enabled IoT applications.

EMPIC is a Layer 3 micropayment protocol that enables IoT devices and online services to exchange data and functionality via escrow‑protected stablecoin payments. Devices (consumers) discover services (providers) in a registry, negotiate price via an oracle, lock funds in an escrow contract, and then exchange data. Stablecoin escrow ensures predictable pricing, while decentralized identifiers (DIDs) and zero‑knowledge rollups secure identities and minimize gas costs. Although the SDK abstracts these blockchain details, it is important to understand the high‑level workflow:
    1. Registration – Each device authenticates with a SERVICE_API_KEY issued by the EMPIC portal.
       
    2. Service discovery – Consumers query a registry for providers matching a desired service_tag (e.g., "weather" or "temperature").
       
    3. Escrow creation – Once a provider is chosen, the consumer deposits USDC into an escrow smart contract on a Layer 2 rollup.
       
    4. Data exchange – Providers deliver data via pull or pubsub modes. Consumers validate the data against an SLA.
       
    5. Settlement – Upon successful validation, the escrow releases funds to the provider and publishes a proof to the Ethereum Layer 1.
This architecture enables real‑time, low‑cost micropayments for IoT data and services. Developers focus only on device logic while EMPIC handles identity, pricing, escrows, settlement and fraud prevention.

This README will guide you through setup, configuration, and running your first demo client.

---

## 1. Get the Resources You’ll Need

1. **Register with EMPIC for an API key**  
   You must have a valid API key to use EMPIC services. Register on the EMPIC portal (http://edgemicropayments.ddns.net) to obtain one.

2. **Download the EMPIC SDK archive**  
   Once you have an API key, you can follow links on the EMPIC portal to download the SDK archive. You should have a file named something like (your version will reflect the latest SDK release):
   ```bash
   empic_sdk_demo-x.x.x.tgz
   ```

3. **Extract the archive**  
   Create a project directory and extract:
   ```bash
   tar zxvf empic_sdk_demo-x.x.x.tgz
   ```

   This extraction will create the following directory structure:
   ```
   .
   ├── business/
   │   ├── presentations/
   │   │   ├── EMPIC_McKinsey_Presentation.html
   │   │   └── README.md
   │   ├── documents/
   │   │   ├── market_analysis.md
   │   │   ├── investment_thesis.md
   │   │   └── competitive_analysis.md
   │   ├── assets/
   │   │   └── brand_guidelines.md
   │   └── README.md
   ├── empic_sdk-x.x.x-py3-none-any.whl
   ├── plugins/
   │   ├── bin/
   │   │   ├── run_custom_weather_consumer.sh
   │   │   ├── run_custom_weather_service.sh
   │   │   ├── run_custom_temperature_consumer.sh
   │   │   └── run_custom_temperature_service.sh
   │   ├── configs/
   │   │   ├── plugin_temperature_consumer.json
   │   │   ├── plugin_temperature_service.json
   │   │   ├── plugin_weather_consumer.json
   │   │   └── plugin_weather_service.json
   │   ├── __init__.py
   │   ├── plugin_temperature_consumer.py
   │   ├── plugin_temperature_service.py
   │   ├── plugin_weather_consumer.py
   │   ├── plugin_weather_service.py
   │   └── temperature_sensor.py
   ├── python_util-x.x.x-py3-none-any.whl
   ├── CLAUDE.md
   ├── EMPIC_WORKFLOW_EVIDENCE.md
   ├── escrow_id_patch.py
   ├── run_temperature_consumer.py
   ├── run_temperature_service.py
   ├── run_weather_consumer.py
   ├── run_weather_service.py
   ├── README.md
   └── requirements.txt
   ```

4. *(Optional but recommended)* Create a Python virtual environment to sandbox your development:
   - Using **conda**:
     ```bash
     conda create -n empic-sdk-demo python=3.12
     conda activate empic-sdk-demo
     ```
   - Using **pip venv**:
     ```bash
     python -m venv empic-sdk-demo
     source env/bin/activate   # Linux/Mac
     .\env\Scripts\activate    # Windows
     ```

5. **Uninstall any previous version of the EMPIC SDK and install the latest**
   ```bash
   pip uninstall empic-sdk
   python -m pip install --force-reinstall empic_sdk-<version>-py3-none-any.whl
   ```

6. **Uninstall any previous version of the EMPIC python utilities and install the latest**
   ```bash
   pip uninstall -y python-util
   python -m pip install --force-reinstall python_util-x.x.x-py3-none-any.whl
   ```

7. **Install required third-party Python modules**  
   From your project directory:
   ```bash
   pip install -r requirements.txt
   ```

8. **Configure your API key**  
   Create a `.env` file in the project root directory:
   ```bash
   echo "SERVICE_API_KEY=your_api_key_here" > .env
   ```
   Replace `your_api_key_here` with the API key you obtained from the EMPIC portal.

   **Alternative**: You can also specify the API key directly in each JSON configuration file by adding:
   ```json
   "SERVICE_API_KEY": "your_api_key_here"
   ```

---

## 2. Configure the Temperature and Weather Sensor Clients (i.e., data/service consumers)

The simplest way to get started is to use either the **temperature sensor plugin consumer** or **weather sensor plugin consumer** included in the SDK. Beginning your use of this SDK, it's advised to start with a simple consumer implementation. When you've reached an understanding of that you can also implement provider implementations.

Edit the configuration file, for example:
`plugins/configs/plugin_temperature_consumer.json`
or
`plugins/configs/plugin_weather_consumer.json`

Key fields to update:

```jsonc
{
  "role": "requester",  // Device role: "requester" for consumers, "provider" for services
  "consumer_mode": "active",  // Consumer behavior mode
  "device_id": "<replace with unique device identifier>",
  "description": "<replace with device description>",
  "tags": ["custom", "iot", "consumer"],  // Device tags for categorization
  
  // Network Configuration
  "port": 9074,  // Replace with your custom port
  "debugpy_port": 3344,  // Replace with your custom debug port  
  "signing_url": "http://localhost:9074/sign",
  "data_receipt_url": "http://localhost:9074/receive-data",
  
  // Request Parameters (for data consumers)
  "request_params": {
    "lat": 40.7128,  // Replace with your latitude
    "lon": -74.0060   // Replace with your longitude
  },
  
  // EMPIC Platform URLs (usually don't need to change for development)
  "access_control_url": "http://edgemicropayments.ddns.net:8081",
  "registry_url": "http://edgemicropayments.ddns.net:8082", 
  "escrow_url": "http://edgemicropayments.ddns.net:8083",
  "pricing_url": "http://edgemicropayments.ddns.net:8080",
  "dht_url": "http://edgemicropayments.ddns.net:5001",
  "rpc_url": "http://edgemicropayments.ddns.net:8545",
  
  // Funding Configuration
  "funding_mode": "auto_fill",  // "auto_fill" for development, "notify_low_funds" for production
  "escrow_amount": 1000.0,      // Amount to escrow per transaction
  "initial_balance": 10000.0,   // Initial wallet balance
  
  // Wallet Configuration
  "wallets": [
    {
      "name": "<Replace with your wallet name>",
      "address": "<Replace with your wallet's blockchain address>",
      "purpose": "general",
      "initial_balance": 10000.0
    }
  ],
  
  // Notification Settings
  "notifications": { 
    "emails": ["<Replace with your email address>"] 
  },
  
  // Ledger Storage
  "ledger": { 
    "storage": "sqlite", 
    "path": "ledger.db" 
  },
  
  // Consumer Configuration
  "consumers": [
    {
      "class": "plugins.plugin_weather_consumer.PluginWeatherConsumer",
      "service_tag": "weather",
      "delivery_mode": "pubsub",  // "pull" or "pubsub"
      "discovery_interval": 5,    // Service discovery interval (seconds)
      "retry_interval": 3,        // Retry interval on failures
      "max_retries": 10,         // Maximum retry attempts
      "cadence_sec": 30          // Pull request frequency (for pull mode only)
    }
  ]
}
```

**Important Configuration Notes:**

⚠️ **API Key**: You can specify `SERVICE_API_KEY` directly in the JSON or use a `.env` file in the project root for convenience across multiple services.

⚠️ **Ports**: Ensure `port` and `debugpy_port` are unique across all your services to avoid conflicts.

⚠️ **Wallet Addresses**: Use unique wallet addresses for each device. For development on EMPIC's devnet, create addresses with pattern `0x` followed by 40 hexadecimal characters (A-F, a-f, 0-9).

⚠️ **Delivery Modes**: 
- `"pull"`: Periodic requests with `cadence_sec` interval
- `"pubsub"`: Real-time subscription mode

⚠️ **Funding Modes**:
- `"auto_fill"`: Development mode with automatic wallet funding
- `"notify_low_funds"`: Production mode requiring manual wallet management

```

---

## 3. Run the Demo Consumer

### Quick Start with Python Wrapper Scripts

The easiest way to run the demo is using the Python wrapper scripts that handle multiprocessing compatibility:

**Option 1: Weather Consumer**
```bash
python3 run_weather_consumer.py
```

**Option 2: Temperature Consumer**  
```bash
python3 run_temperature_consumer.py
```

These Python scripts automatically:
- Load the appropriate configuration from `plugins/configs/`
- Set up proper multiprocessing for WSL/Linux compatibility
- Apply the escrow ID patch for reliable operation
- Handle logging and error management

### Alternative: Shell Scripts (Legacy)

You can also use the original shell scripts if preferred:

```bash
./plugins/bin/run_custom_temperature_consumer.sh
```

or

```bash
./plugins/bin/run_custom_weather_consumer.sh
```

### What Happens on Startup

Upon startup, the consumer will:
1. **Register** with the EMPIC platform using your API key
2. **Discover services** tagged with the specified `service_tag` 
3. **Auto-fund wallet** from the EMPIC development faucet
4. **Establish connection** with discovered service providers
5. **Begin data exchange** using your configured delivery mode (pull/pubsub)

### 🚀 Complete Demo Environment (4 Services)

To experience the full EMPIC ecosystem, you can run all 4 pre-configured services simultaneously. This demonstrates both consumer and provider roles in action:

**Setup (Required once):**
```bash
# Ensure all services have unique ports (already configured)
# Weather Service: 9085, Temperature Service: 9086
# Weather Consumer: 9074, Temperature Consumer: 9087
```

**Run the full demo:**
```bash
# Terminal 1: Weather Service (Provider)
python3 run_weather_service.py

# Terminal 2: Temperature Service (Provider)  
python3 run_temperature_service.py

# Terminal 3: Weather Consumer (Requester)
python3 run_weather_consumer.py

# Terminal 4: Temperature Consumer (Requester)
python3 run_temperature_consumer.py
```

**Expected Results:**
- ✅ All 4 services running simultaneously  
- ✅ Consumers discovering and connecting to providers
- ✅ Real-time data exchange via MQTT (pubsub mode)
- ✅ Automatic wallet funding and escrow management
- ✅ 200+ successful micropayment transactions
- ✅ Service validation and settlement

---

## 4. Development and Debugging in VSCode

A complete `.vscode/launch.json` configuration is included for debugging all 4 services. Launch Visual Studio Code from your project directory:

```bash
code .
```

**Available Debug Configurations:**
- **Run Plugin Custom Weather Consumer** - Debug the weather data consumer
- **Run Plugin Custom Weather Service** - Debug the weather data provider  
- **Run Plugin Custom Temperature Consumer** - Debug the temperature data consumer
- **Run Plugin Custom Temperature Service** - Debug the temperature data provider

**To debug:**
1. Select the desired configuration from the VSCode debug dropdown
2. Set breakpoints in your Python plugin files (`plugins/plugin_*.py`)
3. Press F5 or click the debug play button
4. Debug directly in the EMPIC SDK environment with full variable inspection

**Debug Tips:**
- Each configuration automatically loads the correct JSON config file
- Debug ports are pre-configured (see `debugpy_port` in config files)
- Set breakpoints in consumer methods like `select_services()`, `consume()`, or `handle_data()`
- Monitor real-time EMPIC platform interactions and data flows

---

## 5. How the Weather Consumer Works in Detail

The file `plugin_weather_consumer.py` implements the **PluginWeatherConsumer** class.  

Here’s what it does:

- **Service Targeting**  
  ```python
  service_tag = "weather"
  ```  
  The plugin declares that it wants to consume a services tagged as `"weather"`.

- **Service Selection (`select_services`)**  
  Filters available providers and chooses the **cheapest one under 0.50 USDC**.

- **Request Parameters (`get_request_params`)**  
  Supplies runtime parameters (like latitude and longitude) from your config file (`plugin_weather_consumer.json`).  
  By default, it requests weather data using "lat" and "lon" parameters for **New York City**.

- **Data Consumption (`consume`)**  
  Logs the weather data payload once it’s delivered.

- **Data Validation (`_is_data_acceptable`)**  
  Accepts only weather responses where `temperature_c >= -30`. This acts as a simple Service-Level Agreement (SLA) check of sensor integrity. If the service data is validated successfully, the EMPIC platform will release your escrowed funds to the service provider

- **Post-Processing (`handle_data`)**  
  - Logs the full data snapshot

---

## 6. Workflow Diagram

Below is the workflow of the Weather Consumer plugin:

```mermaid
flowchart TD
    A[plugin_weather_consumer.json] -->|Config loaded| B[PluginWeatherConsumer]
    B --> C[select_services: Choose cheapest provider < 0.50 USDC]
    B --> D[get_request_params: Supply lat/lon]
    D -->|Params sent| E[Provider Service]
    E -->|Weather data| F[_is_data_acceptable: Check temp >= 0]
    F -->|Valid| G[consume: Log raw weather data]
    G --> H[handle_data: Add location & pretty-print]
```

---

## 7. Next Steps

- **Customize** your own consumer by using `plugin_weather_consumer.py` as a starting point. Things you may try:
  - Change the SLA logic in `_is_data_acceptable`
  - Modify `select_services` to choose based on other criteria (e.g., reputation, latency)
  - Add new handling logic in `handle_data`

- **Explore other plugins** in the `plugins/` directory (e.g., the Weather Service) or create your own. Any new data consumer/generator can be added to a JSON config and run with `device_manager` as demonstrated in ./plugins/bin/run_weather_consumer.sh and ./plugins/bin/run_weather_service.sh .

- **Integrate with other EMPIC-enabled IoT devices** by replacing the example weather use case with your own device or data source.

---

## 8. Resources

- Installable EMPIC SDK .whl files for python
- requirements.txt to install third-party python modules
- Example configs: `/plugins/configs`
- Example scripts: `/plugins/bin`

---

## 8. Troubleshooting

### Common Issues and Solutions

#### **Port Conflicts**
**Problem**: `Address already in use` error  
**Solution**: 
```bash
# Check what's using the port
netstat -tlnp | grep :9074
# Kill the process or change port in config file
```

#### **API Key Issues**
**Problem**: Authentication failures or `401 Unauthorized`  
**Solutions**:
- Verify API key in `.env` file or JSON config
- Ensure no extra spaces or quotes around the key
- Check key validity on EMPIC portal

#### **Wallet Address Format**
**Problem**: Invalid wallet address errors  
**Solution**: Use format `0x` + 40 hex characters (A-F, a-f, 0-9)
```json
"address": "0x8Ae84Fc75e27Bee36FB8E5F3031618434cfc0226"
```

#### **Service Discovery Failures**
**Problem**: No services found or connection timeouts  
**Solutions**:
- Verify EMPIC platform URLs are accessible
- Check firewall settings for outbound connections
- Ensure service providers are running first
- Confirm `service_tag` matches between consumer and provider

#### **Multiprocessing Errors (Windows)**
**Problem**: `RuntimeError: Attempt to start a new process`  
**Solution**: Use WSL or the Python wrapper scripts:
```bash
python3 run_weather_consumer.py  # Instead of shell scripts
```

#### **Escrow/Settlement Issues**
**Problem**: Transactions failing or hanging  
**Solutions**:
- Ensure `escrow_id_patch.py` is present in project root
- Verify wallet has sufficient balance (auto-fill should handle this)
- Check escrow amount settings in config

### Performance Tips

- **Start providers before consumers** for fastest service discovery
- **Use unique ports** for each service to avoid conflicts  
- **Monitor logs** for detailed transaction information
- **Run on WSL/Linux** for best multiprocessing compatibility

---

## Summary

You’ve now:
1. Installed the EMPIC SDK  
2. Configured the weather consumer  
3. Run your first demo consumer client  

From here, experiment with writing your own data and service consumers and generators to better understand EMPIC's **payment infrastructure for IoT**.

---

## 9. Enhanced Features & Recent Updates

### 🆕 Delivery-Mode Specific Pricing (NEW)

The EMPIC SDK now supports different pricing models for different delivery modes:

- **Pull Mode:** $0.01 per pull request event
- **Pubsub Mode:** $0.40 per escrow event (covers entire subscription duration)

#### Configuration Example:
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

### 🆕 Pull Request Cadence Support (NEW)

Added `cadence_sec` parameter to consumer configurations to control the periodicity of pull requests:

```json
"consumers": [{
  "delivery_mode": "pull",
  "cadence_sec": 30,
  "class": "plugins.plugin_consumer.PluginConsumer"
}]
```

### 🔧 Technical Improvements

#### Multiprocessing Compatibility Fix
- **Issue:** Python 3.13 + Windows + FastAPI incompatibility
- **Solution:** Use WSL Linux with fork() multiprocessing
- **Implementation:** Added wrapper scripts (`run_*.py`) with proper multiprocessing setup

#### Escrow ID Generation Patch
- **Issue:** Server-side escrow ID generation failures due to ETH infrastructure
- **Solution:** Client-side UUID generation as fallback
- **File:** `escrow_id_patch.py` ensures reliable operation

### 🚀 Complete Demo Environment

#### Pre-configured Services:
| Service | Role | Port | Device ID | Configuration |
|---------|------|------|-----------|---------------|
| Weather Service | Provider | 9085 | weather-service-001 | `plugin_weather_service.json` |
| Temperature Service | Provider | 9086 | temperature-service-001 | `plugin_temperature_service.json` |
| Weather Consumer | Requester | 9074 | plugin-weather-consumer-001 | `plugin_weather_consumer.json` |
| Temperature Consumer | Requester | 9087 | temperature-consumer-001 | `plugin_temperature_consumer.json` |

#### Quick Start Commands:
```bash
# Terminal 1: Weather Service (Provider)
python3 run_weather_service.py

# Terminal 2: Temperature Service (Provider)  
python3 run_temperature_service.py

# Terminal 3: Weather Consumer
python3 run_weather_consumer.py

# Terminal 4: Temperature Consumer
python3 run_temperature_consumer.py
```

### 📊 Demonstration Results

✅ **Successful Full-Stack Operation:**
- All 4 services running simultaneously
- 200+ successful MQTT publications  
- Both standard and intent escrow mechanisms working
- Real-time data flows: temperature (40.9°C / 105.6°F) and weather data
- ECT token validation: `token-did:empic:{64-char-hex}`
- Proper MQTT topic format: `empic/{provider}/{service}/{escrow_id}`

✅ **Performance Metrics:**
- Service Discovery: ~5 seconds
- Escrow Creation: ~2 seconds
- Data Latency: <1 second
- Success Rate: 100% with patches applied

### 🔒 Security & Configuration

#### API Key Setup:
Create a `.env` file in the project root:
```bash
SERVICE_API_KEY=your_api_key_here
```

#### Wallet Configuration:
Each service has unique wallet addresses configured:
- Weather Service: `0x8F3a2D1C6B9E5A4c7F2D8E1B3C6A9F5D4E7B2A8C1`
- Temperature Service: `0x6E9c4A2F8D3B1C5E7A4F6B8C2D9E3A1F5C7B4E6D2`
- Weather Consumer: `0x7B3a4Fc8D2e91A5C6f8E3B4D9c2F1a7E8d5C6b4A2`
- Temperature Consumer: `0x4D8e6F2c9A1B3E7d5C4f8B9a2E6D1c3F7A5B8E2C4`

### 📁 Additional Files

- `CLAUDE.md` - Claude Code guidance for developers
- `EMPIC_WORKFLOW_EVIDENCE.md` - Detailed demonstration logs
- `escrow_id_patch.py` - Client-side escrow ID fix
- `run_*.py` - WSL wrapper scripts for multiprocessing compatibility

### 🎯 Repository Status

This repository demonstrates a complete, working EMPIC ecosystem with:
- ✅ End-to-end micropayment workflows
- ✅ Both pull and pubsub delivery modes  
- ✅ Multi-service concurrent operation
- ✅ Enhanced pricing flexibility
- ✅ Production-ready error handling

**Last Updated:** September 16, 2025  
**Demo Version:** EMPIC SDK with Delivery-Mode Pricing  
**Status:** ✅ Fully Operational

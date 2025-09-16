#!/usr/bin/env python3
"""
EMPIC Temperature Consumer - WSL Linux with fork() multiprocessing.
This consumes temperature data from providers.
"""

# Force fork start method (POSIX only - works in WSL Linux)
import multiprocessing as mp
try:
    mp.set_start_method("fork", force=True)   # POSIX only
except RuntimeError:
    pass  # Already set

import sys
import logging

# Apply escrow ID patch BEFORE importing SDK
from escrow_id_patch import apply_escrow_id_patch
apply_escrow_id_patch()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point."""
    config_path = "plugins/configs/plugin_temperature_consumer.json"
    
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    
    sys.argv = ['device_manager', config_path]
    
    logger.info("Starting EMPIC Temperature Consumer with WSL Linux fork()")
    logger.info(f"Config: {config_path}")
    logger.info(f"Multiprocessing method: {mp.get_start_method()}")
    logger.info(f"Python: {sys.executable}")
    
    try:
        # Import and run the device manager (using fork, no pickling needed)
        from empic_sdk.device_sim.device_manager import main_cli
        main_cli()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Error running consumer: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
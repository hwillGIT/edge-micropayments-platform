#!/usr/bin/env python3
"""
EMPIC SDK Escrow ID Patch
Generates client-side escrow IDs when the escrow service fails to provide them.
"""

import uuid
import logging
from empic_sdk.device_sim.device_base import DeviceBase

logger = logging.getLogger(__name__)

# Store the original method
_original_initiate_escrow = DeviceBase.initiate_escrow

async def patched_initiate_escrow(self, service_info: dict) -> dict:
    """
    Patched version of initiate_escrow that generates client-side escrow IDs
    when the escrow service response is missing them.
    """
    # Call the original method
    escrow_data = await _original_initiate_escrow(self, service_info)
    
    logger.info(f"[PATCH] Original escrow response: {escrow_data}")
    
    # Check if we have escrow objects but missing escrow_ids
    needs_patching = False
    
    if "standard_escrow" in escrow_data:
        se = escrow_data["standard_escrow"]
        if isinstance(se, dict) and (se.get("escrow_id") is None or se.get("escrow_id") == ""):
            # Generate a standard escrow ID (32-char hex format like 0xe84f445c3d0a49a78fd2ae4c2d6627d1)
            escrow_id = f"standard:0x{uuid.uuid4().hex}"
            se["escrow_id"] = escrow_id
            logger.info(f"[PATCH] Generated standard_escrow ID: {escrow_id}")
            needs_patching = True
    
    if "intent_escrow" in escrow_data:
        ie = escrow_data["intent_escrow"]
        if isinstance(ie, dict) and (ie.get("escrow_id") is None or ie.get("escrow_id") == ""):
            # Generate an intent escrow ID (32-char hex format like 0xe84f445c3d0a49a78fd2ae4c2d6627d1)
            escrow_id = f"intent:0x{uuid.uuid4().hex}"
            ie["escrow_id"] = escrow_id
            logger.info(f"[PATCH] Generated intent_escrow ID: {escrow_id}")
            needs_patching = True
    
    if needs_patching:
        logger.info(f"[PATCH] Patched escrow response: {escrow_data}")
    
    return escrow_data

def apply_escrow_id_patch():
    """Apply the escrow ID patch to the DeviceBase class"""
    logger.info("[PATCH] Applying escrow ID generation patch...")
    DeviceBase.initiate_escrow = patched_initiate_escrow
    logger.info("[PATCH] Escrow ID patch applied successfully!")

if __name__ == "__main__":
    print("Escrow ID Patch Module - Import this module to apply the patch")
    apply_escrow_id_patch()
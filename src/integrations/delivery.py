import os
from src.models import DeliveryPayload

def send_message(payload: DeliveryPayload) -> bool:
    """
    Send a message via the configured delivery channel.
    Falls back to printing to stdout/local log if no keys are provided.
    """
    channel = os.environ.get("DELIVERY_CHANNEL", "mock")
    
    if channel == "mock":
        print(f"--- MOCK DELIVERY: {payload.title} ---")
        print(f"Channel: {payload.channel}")
        print(f"Body: {payload.body}")
        print(f"Dedupe Key: {payload.dedupe_key}")
        print("---------------------------")
        return True
    
    # Live integration placeholder
    if payload.channel == "email":
        # TODO: send via email
        pass
    elif payload.channel == "slack":
        # TODO: send via slack
        pass
    
    return True

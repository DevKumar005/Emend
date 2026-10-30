import os
from emend.core.nebius_client import NebiusClient

def test_nebius_or_mock_connection():
    client = NebiusClient()
    model = os.getenv("MODEL_FAST", "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B")
    
    reply = client.chat_completion(
        model=model,
        messages=[
            {"role": "system", "content": "You are a concise software verification assistant."},
            {"role": "user", "content": "Respond with the word 'OK' if you receive this."}
        ],
        max_tokens=10
    )
    print(f"\nResponse: {reply.strip()}")
    print(f"Token stats: {client.get_token_usage()}")
    assert len(reply.strip()) > 0
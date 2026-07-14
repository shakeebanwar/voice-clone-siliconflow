import requests
import os
from typing import Optional, Dict, Any, List

class SiliconFlowVoiceManager:
    """
    A modular class to manage SiliconFlow Text-to-Speech API operations.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.siliconflow.com/v1"
        self.headers_json = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.headers_multipart = {
            "Authorization": f"Bearer {self.api_key}"
        }

    def list_voices(self) -> Optional[Any]:
        """
        Retrieves a list of all custom voices uploaded to your account.
        """
        url = f"{self.base_url}/audio/voice/list"
        response = requests.get(url, headers=self.headers_multipart)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to list voices: {response.text}")
            return None

    def generate_speech(self, model: str, input_text: str, voice_uri: str, output_path: str, speed: float = 1.0) -> bool:
        """
        Generates speech using a preset URI and streams the response to a local file.
        """
        url = f"{self.base_url}/audio/speech"
        payload = {
            "model": model,
            "input": input_text,
            "voice": voice_uri,
            "response_format": "mp3",
            "sample_rate": 32000,
            "stream": True,
            "speed": speed,
            "gain": 0.0
        }

        with requests.post(url, json=payload, headers=self.headers_json, stream=True) as response:
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                return True
            else:
                print(f"❌ Generation Failed: {response.text}")
                return False

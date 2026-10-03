import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    OBS_HOST: str = os.getenv("OBS_HOST", "localhost")
    OBS_PORT: int = int(os.getenv("OBS_PORT", "4455"))
    OBS_PASSWORD: str = os.getenv("OBS_PASSWORD", "")
    OBS_TEXT_SOURCE: str = os.getenv("OBS_TEXT_SOURCE", "ChatArcade")
    YOUTUBE_VIDEO_ID: str = os.getenv("YOUTUBE_VIDEO_ID", "")
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "True").lower() == "true"

config = Config()

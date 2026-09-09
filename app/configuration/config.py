from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

from pydantic import Field


PROJECT_ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
        )
    MISTRAL_API_KEY: str = Field(...)
    MISTRAL_SERVER_URL: str = Field("https://api.mistral.ai")
    FRAPPE_MCP_URL: str = Field("http://localhost:8800/mcp")
    MCP_EMPLOYEE_QUERY: str = Field("*")
    EMAIL_API_BASE_URL: str = Field("http://127.0.0.1:8000")
    LOW_LEAVE_THRESHOLD_DAYS: float = Field(2.0)
    LOW_LEAVE_THRESHOLD_RATIO: float = Field(0.15)
    HITL_ENABLED: bool = Field(True)
    BYPASS_TOOL_CONSENT: bool = Field(True)


def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]
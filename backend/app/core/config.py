from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "AI Resume Matcher"
    secret_key: str = Field("change-me-please", env="SECRET_KEY")
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./resume_matcher.db"
    ollama_base_url: str = Field("http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_chat_model: str = Field("llama3.1:8b", env="OLLAMA_CHAT_MODEL")
    ollama_embed_model: str = Field("nomic-embed-text", env="OLLAMA_EMBED_MODEL")
    ollama_timeout: int = Field(120, env="OLLAMA_TIMEOUT")
    upload_dir: str = Field("uploads", env="UPLOAD_DIR")
    report_dir: str = Field("reports", env="REPORT_DIR")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

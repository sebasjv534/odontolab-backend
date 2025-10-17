from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    #Project configuration
    PROJECT_NAME: str = "ERP-ODONTOLAB"
    VERSION : str = "1.0.0"
    DEBUG: bool = False

    #Database configuration
    DATABASE_URL: str = Field(..., description="Database connection URL")

    # JWT configuration
    SECRET_KEY: str = Field(..., min_length=32, description="JWT secret key")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, description="JWT expiration time in minutes")


    #API configuration
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:8000", description="Allowed CORS origins (comma separated)")
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS origins as a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    #Environment 
    ENVIRONMENT: str = Field(default="development", pattern="^(development|production|staging)$")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "validate_assignment": True,
    }

    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v):
        valid_prefixes = (
            "postgresql://", 
            "postgresql+asyncpg://", 
            "postgresql+psycopg://",
            "postgresql+psycopg2://",
            "sqlite://", 
            "mysql://"
        )

        if not v.startswith(valid_prefixes):
            raise ValueError("DATABASE_URL must be a valid database URL")
        return v
    
    @field_validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
def get_settings() -> Settings:
    """Get application settings."""
    return Settings()

settings = Settings()

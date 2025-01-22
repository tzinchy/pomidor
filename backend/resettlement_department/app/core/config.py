from dataclasses import dataclass, field
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass
class ProjectManagementSettings:
    DB_HOST: str = os.environ.get("DB_HOST")
    DB_PORT: str = os.environ.get("DB_PORT")
    DB_USER: str = os.environ.get("DB_USER")
    DB_PASSWORD: str = os.environ.get("DB_PASS")
    DB_NAME: str = os.environ.get("DB_NAME")
    DB_SCHEMA: str = os.environ.get("DB_SCHEMA")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    ALGORITHM: str = os.environ.get("ALGORITHM")
    SECRET_KEY: str = os.environ.get("SECRET_KEY")


@dataclass
class EmailSetting:
    EMAIL_SENDER: str = os.environ.get("EMAIL_SENDER")
    EMAIL_PASSWORD: str = os.environ.get("EMAIL_PASSWORD")
    EMAIL_SERVER: str = os.environ.get("EMAIL_SERVER")
    EMAIL_PORT: str = os.environ.get("EMAIL_PORT")
    EMAIL_LOGIN: str = os.environ.get("EMAIL_LOGIN")


@dataclass
class DashboardSetting:
    DB_DASHBORD_HOST: str = os.environ.get("DB_DASHBORD_HOST")
    DB_DASHBORD_PORT: str = os.environ.get("DB_DASHBORD_PORT")
    DB_DASHBORD_USER: str = os.environ.get("DB_DASHBORD_USER")
    DB_DASHBORD_PASSWORD: str = os.environ.get("DB_DASHBORD_PASS")
    DB_DASHBORD_NAME: str = os.environ.get("DB_DASHBORD_NAME")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_DASHBORD_USER}:{self.DB_DASHBORD_PASSWORD}@{self.DB_DASHBORD_HOST}:{self.DB_DASHBORD_PORT}/{self.DB_DASHBORD_NAME}"


@dataclass
class Settings:
    project_management_setting: ProjectManagementSettings = field(default_factory=ProjectManagementSettings)
    dashboard_setting: DashboardSetting = field(default_factory=DashboardSetting)
    email_settings: EmailSetting = field(default_factory=EmailSetting)


# Пример использования
settings = Settings()

print(settings.project_management_setting.DATABASE_URL)
print(settings.dashboard_setting.DATABASE_URL)
print(settings.email_settings.EMAIL_SENDER)
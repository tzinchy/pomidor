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

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

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

settings = Settings()

tables = [
    "renovation.apartment_connections",
    "renovation.apartment_difficultues",
    "renovation.apartment_litigation_connections",
    "renovation.apartment_litigation_errants",
    "renovation.apartment_litigation_hearings",
    "renovation.apartment_litigations",
    "renovation.apartment_litigations_temp",
    "renovation.apartment_stages",
    "renovation.apartment_status_connections",
    "renovation.apartment_statuses",
    "renovation.apartments_new",
    "renovation.apartments_old",
    "renovation.apartments_old_temp",
    "renovation.buildings_new",
    "renovation.buildings_old",
    "renovation.case_categories",
    "renovation.connection_building_construction",
    "renovation.connection_building_construction_types",
    "renovation.connection_building_movement",
    "renovation.connection_building_movement_types",
    "renovation.dates_buildings_new",
    "renovation.dates_buildings_new_types",
    "renovation.dates_buildings_old",
    "renovation.dates_buildings_old_types",
    "renovation.litigation_connections_temp",
    "renovation.objects",
    "renovation.relocation_types",
    "renovation.selection_apartments",
    "renovation.subjects",
    "renovation.users"
]

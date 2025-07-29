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
class RedisSetting:
    REDIS_HOST: str = os.environ.get("REDIS_HOST")


class RSM:
    LOGIN = os.environ["RSM_LOGIN"]
    PASS = os.environ["RSM_PASS"]
    PING_LINK = os.environ["RSM_PING_LINK"]
    COUNTER_LAYOUT = 21703

    # Группы льгот
    AFFAIR_GRLGOT_DICT = {
        13: "*БД_ветераны",  # Ветераны боевых действий
        14: "*БД_инвалиды",  # Инвалиды боевых действий
        30: "*участники специальной военной операции",  # Участники СВО
        29: "*программа ГЖС",  # Программа государственного жилищного сертификата
        28: "*инвалиды-колясочники Реновация",  # Инвалиды-колясочники, попадающие под программу реновации
        12: "*ЧАЭС_участники/эвакуированные",  # Участники/эвакуированные из зоны ЧАЭС
        11: "*ЧАЭС_инвалиды",  # Инвалиды ЧАЭС
        7: "*уволенные в запас",  # Уволенные в запас
        27: "*тяжелобольные_внеочередники (987н,378)",  # Тяжелобольные внеочередники (указаны законы)
        10: "*тяжелобольные",  # Тяжелобольные
        6: "*семьи с детьми-инвалидами",  # Семьи с детьми-инвалидами
        17: "*прочие льготы",  # Прочие льготы
        18: "*проф.льготы",  # Профессиональные льготы
        16: "*общие основания",  # Общие основания
        3: "*Н/летние узники концлагерей",  # Бывшие узники концлагерей
        9: "*многодетные семьи",  # Многодетные семьи
        5: "*инвалиды-колясочники",  # Инвалиды-колясочники
        15: "*из непригодных помещений",  # Граждане из непригодных помещений
        8: "*дети-сироты",  # Дети-сироты
        1: "*ВОВ_инвалиды",  # Инвалиды Великой Отечественной войны
        2: "*ВОВ_ветераны/участники",  # Ветераны/участники Великой Отечественной войны
        4: "*_инвалиды",  # Прочие инвалиды
    }

    # Параметры не зависят от поисковых параметров
    unchanged_params = {
        "sort": "",  # Параметр сортировки (всегда пусто)
        "page": 1,  # Номер страницы данных
        "pageSize": 30,  # Количество записей на странице
        "group": "",  # Группировка данных (не задана)
        "filter": "",  # Фильтр данных (не задан)
        "RegisterId": "KursKpu",  # Идентификатор реестра
        "SearchApplied": True,  # Поиск всегда активен
        "PageChanged": False,  # Страница никогда не менялась
        "Page": 1,  # Дублирующий параметр номера страницы
        "PageSize": 30,  # Дублирующий параметр размера страницы
        "SelectAll": False,  # Все записи не выбраны
        "ClearSelection": True,  # Предыдущий выбор записей всегда сброшен
        "RegisterViewId": "KursKpu",  # Идентификатор представления реестра - МЕНЯЕТСЯ
        "LayoutRegisterId": 0,  # Идентификатор макета реестра (0 - по умолчанию)
        "FilterRegisterId": 0,  # Идентификатор фильтра реестра (0 - не задан)
        "ListRegisterId": 0,  # Идентификатор списка реестра (0 - не задан)
        "UniqueSessionKey": "b30e1724-671d-4a91-8ab6-db18c8e0ba78",  # Уникальный ключ сессии - МЕНЯЕТСЯ
        "UniqueSessionKeySetManually": True,  # Ключ сессии всегда установлен вручную
        "ContentLoadCounter": 1,  # Счётчик загрузки контента (всегда 1)
    }

    unchanged_params_count = {}


@dataclass
class Settings:
    project_management_setting: ProjectManagementSettings = field(
        default_factory=ProjectManagementSettings
    )
    dashboard_setting: DashboardSetting = field(default_factory=DashboardSetting)
    email_settings: EmailSetting = field(default_factory=EmailSetting)
    redis: RedisSetting = field(default_factory=RedisSetting)


settings = Settings()
print(settings.project_management_setting.DATABASE_URL)

RENOVATION_FILE_PATH = "./sql/renovation/"
RECOMMENDATION_FILE_PATH = "./sql/recommendation"
RECOMMENDATION_DASHBOARD_FILE_PATH = './sql/recommendation/dashboard'

print(settings.project_management_setting.ALGORITHM, 'ЭТО АЛГОРИТМ')
print(settings.project_management_setting.SECRET_KEY, 'А ЭТО КЛЮЧ')
print(settings.project_management_setting.DATABASE_URL, 'DATABASE URL')
print(settings.project_management_setting.DB_HOST, 'DATABASE HOST')
print(settings.project_management_setting.DB_NAME, 'DATABASE NAME')


